"""
Main agent 是 Puzzle Fact Check 的主模型，其主要负责：
1. 核查规划：从新闻文本中提取核查点，并规划检索方案
2. 智能体协调：协调 metadata extractor, search agent 等子模型执行具体的检索任务
3. Supervisor: 对 search agent 的检索结果进行复核，并根据反馈更新核查计划 
4. 报告生成：根据核查结论生成报告
"""

from agents.base import BaseAgent
from langchain_core.messages import AIMessage, BaseMessage
from langgraph.graph.state import CompiledStateGraph, StateGraph, END
from langgraph.types import interrupt, Command
from langgraph.pregel import RetryPolicy
from langgraph.checkpoint.memory import MemorySaver
from .prompts import (
    fact_check_plan_prompt_template,
    fact_check_plan_output_parser,
    evaluate_search_result_output_parser,
    evaluate_search_result_prompt_template,
    write_fact_checking_report_prompt_template,
)
from ..searcher.states import SearchAgentState
from ..searcher.graph import SearchAgentGraph
from ..metadata_extractor.graph import MetadataExtractAgentGraph
from ..metadata_extractor.states import MetadataState
from utils.exceptions import AgentExecutionException

from pubsub import pub
from .events import MainAgentEvents, CLIModeEvents, DBEvents, APIMode

from typing import List, Optional, Any, Dict, Literal
from .states import (
    FactCheckPlanState,
    RetrievalResult,
    RetrievalResultVerification,
    CheckPoint,
    CheckPoints,
    RetrievalStep,
)
from langchain_core.runnables import RunnableConfig
from langchain_openai.chat_models.base import BaseChatOpenAI


class MainAgent(BaseAgent):
    def __init__(
        self,
        model: BaseChatOpenAI,
        metadata_extract_model: BaseChatOpenAI,
        search_model: BaseChatOpenAI,
        mode: Literal["CLI", "API"] = "CLI",
        max_search_tokens: int = 5000,
        max_retries: int = 1, # main agent 在一个任务上允许的最多重试次数
    ):
        super().__init__(
            mode=mode,
            model=model,
        )
        
        self.mode = mode
        self.metadata_extract_agent = MetadataExtractAgentGraph(
            mode=mode,
            model=metadata_extract_model,
        )
        self.search_agent = SearchAgentGraph(
            mode=mode,
            model=search_model,
            max_search_tokens=max_search_tokens,
        )
        
        # graph 内部动态条件参数
        self.retries = 0
        self.max_retries = max_retries
        self.current_retrieval_task_index = 0  # 跟踪当前检索任务的索引
        self.total_retrieval_tasks_nums = 0  # 总任务数
        self._interrupted = False  # 中断标志
        
        # self.db_events = DBEvents()
        if mode == "CLI":
            self.cli_events = CLIModeEvents()
        elif mode == "API":
            # API 模式下只创建一个空的APIMode实例
            # 实际的事件处理由service.py中的SSEModeEvents处理
            self.api_mode = APIMode()

    def _build_graph(self) -> CompiledStateGraph:
        graph_builder = StateGraph(FactCheckPlanState)

        graph_builder.add_node("initialization", self.initialization)
        graph_builder.add_node("invoke_metadata_extract_agent", self.invoke_metadata_extract_agent)
        graph_builder.add_node("extract_check_point", self.extract_check_point)
        graph_builder.add_node("invoke_search_agent", self.invoke_search_agent)
        graph_builder.add_node("evaluate_search_result", self.evaluate_search_result)
        graph_builder.add_node("write_fact_checking_report", self.write_fact_checking_report)

        graph_builder.set_entry_point("initialization")
        graph_builder.add_edge("initialization", "invoke_metadata_extract_agent")
        graph_builder.add_edge("invoke_metadata_extract_agent", "extract_check_point")
        graph_builder.add_conditional_edges(
            "extract_check_point",
            self.should_continue_to_retrieval,
            ["invoke_search_agent", END]
        )
        graph_builder.add_edge("invoke_search_agent", "evaluate_search_result")
        graph_builder.add_conditional_edges(
            "evaluate_search_result",
            self.should_retry_or_continue,
            {
                "retry": "invoke_search_agent",
                "next": "invoke_search_agent",
                "finish": "write_fact_checking_report"
            }
        )
        graph_builder.set_finish_point("write_fact_checking_report")

        return graph_builder.compile(
            checkpointer=MemorySaver(),
        )
        
    def initialization(self, state: FactCheckPlanState):
        pub.sendMessage(
            MainAgentEvents.STORE_NEWS_TEXT.value,
            news_text=state.news_text
        )
        
        # Check for interruption in a safer way
        if self._check_interruption():
            return interrupt({"status": "interrupted", "message": "任务已被中断"})
        
        return state

    def invoke_metadata_extract_agent(self, state: FactCheckPlanState):
        result = self.metadata_extract_agent.graph.invoke({"news_text": state.news_text})
        metadata = MetadataState(**result)
        
        if not metadata.basic_metadata:
            raise AgentExecutionException(
                agent_type="main",
                message="无法从文本中提取新闻元数据，请检查文本",
            )

        return {"metadata": metadata}

    def extract_check_point(self, state: FactCheckPlanState):
        """
        对新闻文本进行核查前规划：
        1. 提取陈述
        2. 评估每个陈述，确定核查点
        3. 规划检索方案

        Returns:
            核查方案 JSON
        """
        # Check for interruption
        if self._check_interruption():
            return interrupt({"status": "interrupted", "message": "任务已被中断"})
        
        pub.sendMessage(MainAgentEvents.EXTRACT_CHECK_POINT_START.value)

        messages = [
            fact_check_plan_prompt_template.format(
                news_text=state.news_text,
                # 上一个节点已经处理了 metadata 不存在的情况
                basic_metadata=state.metadata.basic_metadata.serialize_for_llm(), # type: ignore
                # 上一个节点已经处理了 knowledges 不存在的情况
                knowledges=state.metadata.serialize_retrieved_knowledges_for_llm(), # type: ignore
            )
        ]

        response = self.model.invoke(messages)
        check_points: CheckPoints = fact_check_plan_output_parser.invoke(response)
        pub.sendMessage(
            MainAgentEvents.EXTRACT_CHECK_POINT_END.value,
            check_points_result=check_points
        )
        
        formatted_check_points = state.get_formatted_check_points(check_points)
        
        return {
            "check_points": formatted_check_points
        }

    def should_continue_to_retrieval(self, state: FactCheckPlanState):
        """
        决定是否继续执行检索
        如果有 check point 和 basic_metadata，则创建检索任务
        如果没有，则结束图的执行
        """
        # 没有核查点或元数据，结束图执行
        if (
            len(state.check_points) == 0
            or not state.metadata
            or not state.metadata.basic_metadata
        ):
            raise AgentExecutionException(
                agent_type="main",
                message="无法从文本中提取核查点或元数据，请检查文本",
            )

        return "invoke_search_agent"

    def invoke_search_agent(self, state: FactCheckPlanState):
        """根据检索规划调用子检索模型执行深度检索"""        
        # Check for interruption
        if self._check_interruption():
            return interrupt({"status": "interrupted", "message": "任务已被中断"})
        
        current_task = self._get_current_retrieval_task(state)
        if not current_task:
            raise AgentExecutionException(
                agent_type="main",
                message="无法找到检索任务",
            )
        
        self.retries += 1
        
        result = self.search_agent.graph.invoke(current_task)
        
        search_state = SearchAgentState(**result)
        if not search_state.result:
            raise AgentExecutionException(
                agent_type="searcher",
                message="检索模型未返回结果",
            )

        retrieval_result = RetrievalResult(
            check_point_id=search_state.check_point_id,
            retrieval_step_id=search_state.retrieval_step_id,
            summary=search_state.result.summary,
            conclusion=search_state.result.conclusion,
            confidence=search_state.result.confidence,
            evidences=search_state.evidences,
        )

        updates = [{
            "id": retrieval_result.retrieval_step_id, 
            "data": {
                "result": retrieval_result,
            }
        }]
        updated_check_points = self._batch_update_retrieval_steps(state, updates)

        return {"check_points": updated_check_points}

    def evaluate_search_result(self, state: FactCheckPlanState):
        """主模型对当前 search agent 的检索结论进行复核推理"""
        # Check for interruption
        if self._check_interruption():
            return interrupt({"status": "interrupted", "message": "任务已被中断"})
                
        current_task = self._get_current_retrieval_task(state)
        if not current_task:
            raise AgentExecutionException(
                agent_type="main",
                message="无法找到当前检索任务",
            )
            
        current_step = self.find_retrieval_step(state, current_task.retrieval_step_id)
        if not current_step:
            raise AgentExecutionException(
                agent_type="main",
                message="无法找到当前检索步骤",
            )
        
        current_result = current_step.result
        if not current_result:
            raise AgentExecutionException(
                agent_type="main",
                message="无法找到当前检索步骤的结果",
            )

        pub.sendMessage(MainAgentEvents.EVALUATE_SEARCH_RESULT_START.value)
        
        # 评估当前检索结果
        response = self.model.invoke([
            evaluate_search_result_prompt_template.format(
                news_text=state.news_text,
                current_step=current_step,
                current_result=current_result
            )
        ])
        verification_result: RetrievalResultVerification = evaluate_search_result_output_parser.invoke(response)
        
        updates = [{
            "id": current_step.id, 
            "data": {
                "verification": verification_result,
            }
        }]

        # 主模型不认可检索结论，需要更新检索步骤
        if not verification_result.verified and (verification_result.updated_purpose or verification_result.updated_expected_sources):
            update_data = {
                "purpose": verification_result.updated_purpose,
                "expected_sources": verification_result.updated_expected_sources,
            }
            updates.append({"id": current_step.id, "data": update_data})

        updated_check_points = self._batch_update_retrieval_steps(state, updates)
        
        pub.sendMessage(
            MainAgentEvents.EVALUATE_SEARCH_RESULT_END.value,
            verification_result=verification_result
        )
        
        return {"check_points": updated_check_points}

    def should_retry_or_continue(self, state: FactCheckPlanState) -> Literal["retry", "next", "finish"]:        
        """
        根据评估结果决定是重试当前检索任务、继续下一个任务还是完成检索
        """
        # 检查是否已经处理完所有任务
        if self.current_retrieval_task_index >= self.total_retrieval_tasks_nums - 1:
            pub.sendMessage(
                MainAgentEvents.LLM_DECISION.value, 
                decision="完成检索", 
                reason="所有检索任务均已完成"
            )
            return "finish"
        
        current_task = self._get_current_retrieval_task(state)
        current_step = self.find_retrieval_step(state, current_task.retrieval_step_id)
        if not current_step or not current_step.verification:
            raise AgentExecutionException(
                agent_type="main",
                message="无法找到当前检索步骤的验证结果",
            )

        # 主模型对当前检索结果不满意，且 search agent 重试次数未超过最大重试次数，重试当前检索
        if not current_step.verification.verified and self.retries <= self.max_retries:
            pub.sendMessage(
                MainAgentEvents.LLM_DECISION.value, 
                decision="重试当前检索", 
                reason=current_step.verification.reasoning
            )
            return "retry"

        # 主模型不认可当前检索结果，但 search agent 重试次数超过最大重试次数，继续下一个任务
        if not current_step.verification.verified and self.retries > self.max_retries:
            pub.sendMessage(
                MainAgentEvents.LLM_DECISION.value, 
                decision="继续下一个任务", 
                reason=current_step.verification.reasoning
            )
        else:
        # 主模型认可当前检索结果，search agent 继续下一个任务
            pub.sendMessage(
                MainAgentEvents.LLM_DECISION.value, 
                decision="继续下一个任务", 
                reason="继续执行下一个检索任务"
            )
        
        # 重置重试计数器和更新当前检索任务索引，准备处理下一个任务
        self.retries = 0
        self.current_retrieval_task_index += 1

        return "next"
    
    def write_fact_checking_report(self, state: FactCheckPlanState):
        """main agent 认可全部核查结论将核查结果写入报告"""
        # Check for interruption
        if self._check_interruption():
            return interrupt({"status": "interrupted", "message": "任务已被中断"})
                
        pub.sendMessage(MainAgentEvents.WRITE_FACT_CHECKING_REPORT_START.value)
        
        response = self.model.invoke([
            write_fact_checking_report_prompt_template.format(
                news_text=state.news_text, 
                check_points=state.check_points
            )
        ])
        
        pub.sendMessage(
            MainAgentEvents.WRITE_FACT_CHECKING_REPORT_END.value,
            response_text=response.content
        )

        return state
    
    def _get_current_retrieval_task(self, state: FactCheckPlanState) -> SearchAgentState:
        """获取要执行的检索任务"""
        retrieval_tasks = [
            SearchAgentState(
                basic_metadata=state.metadata.basic_metadata, # type: ignore BasicMetadata 不存在的情况已经在前置节点处理
                check_point_id=check_point.id,
                retrieval_step_id=retrieval_step.id,
                content=check_point.content,
                purpose=retrieval_step.purpose,
                expected_sources=retrieval_step.expected_sources,
            )
            
            for check_point in state.check_points
            if check_point.retrieval_step
            
            for retrieval_step in check_point.retrieval_step
        ]
        
        self.total_retrieval_tasks_nums = len(retrieval_tasks)
        
        return retrieval_tasks[self.current_retrieval_task_index]

    def _batch_update_retrieval_steps(
        self, state: FactCheckPlanState, updates: List[Dict[str, Any]]
    ) -> List[CheckPoint]:
        """
        批量更新多个 retrieval_step

        Args:
            state: FactCheckPlanState
            updates: 更新数据列表，每项格式为 {"id": retrieval_step_id, "data": update_data}
                - id: 要更新的 retrieval_step 的 id
                - data: 要更新的数据字典

        Returns:
            更新后的完整 check_points 列表

        Raises:
            ValueError: 当找不到指定 id 的 retrieval_step 时
        """
        updated_check_points = state.check_points.copy()

        # 构建检索步骤的索引映射
        step_index = {}
        for i, check_point in enumerate(updated_check_points):
            if not check_point.retrieval_step:
                continue

            for j, step in enumerate(check_point.retrieval_step):
                step_index[step.id] = (i, j)

        # 批量更新
        for update in updates:
            retrieval_step_id = update["id"]
            update_data = update["data"]

            if retrieval_step_id in step_index:
                check_point_idx, step_idx = step_index[retrieval_step_id]
                step = updated_check_points[check_point_idx].retrieval_step[step_idx]

                for key, value in update_data.items():
                    if hasattr(step, key):
                        setattr(step, key, value)
                    else:
                        raise ValueError(f"Retrieval step 没有 '{key}' 属性")
            else:
                raise ValueError(
                    f"找不到 ID 为 '{retrieval_step_id}' 的 retrieval step"
                )

        # 返回完整的 check_points 列表
        return updated_check_points
    
    def find_retrieval_step(self, state: FactCheckPlanState, retrieval_step_id: str) -> Optional[RetrievalStep]:
        """查找指定 id 的 retrieval step"""
        for check_point in state.check_points:
            for step in check_point.retrieval_step: # type: ignore
                if step.id == retrieval_step_id:
                    return step
        return None

    # 重写 invoke 方法以支持 CLI 模式，令 Main Agent 能够在内部处理 human-in-the-loop 流程
    def invoke(self, input: Any, config: Optional[RunnableConfig] = None, **kwargs):
        if not config or not config.get("configurable"):
            raise ValueError("Agent 缺少 thread_id 配置")
        
        # 从配置中获取中断检查回调
        should_continue = config.get("configurable", {}).get("should_continue", lambda: True)
        
        try:
            # 在执行前检查是否应该继续
            if callable(should_continue) and not should_continue():
                pub.sendMessage(
                    MainAgentEvents.LLM_DECISION.value,
                    decision="任务中断",
                    reason="收到用户中断信号"
                )
                return {"status": "interrupted", "message": "任务已被中断"}
            
            # 修改图表执行策略，加入中断检查
            orig_invoke = self.graph.invoke
            
            def invoke_with_interrupt_check(*args, **kw):
                # 在每次图执行前检查是否应该继续
                if callable(should_continue) and not should_continue():
                    return interrupt({"status": "interrupted", "message": "任务已被中断"})
                return orig_invoke(*args, **kw)
            
            # 临时替换invoke方法添加中断检查
            self.graph.invoke = invoke_with_interrupt_check
            
            # 执行图
            result = self.graph.invoke(input, config, **kwargs)
            
            # 恢复原始方法
            self.graph.invoke = orig_invoke
            
            # 执行完成后再次检查是否被中断
            if callable(should_continue) and not should_continue():
                return {"status": "interrupted", "message": "任务已被中断"}
            
            return result
        except Exception as e:
            # 出现异常时恢复原始方法
            if hasattr(self, '_orig_invoke'):
                self.graph.invoke = getattr(self, '_orig_invoke')
            raise e

    def cancel_running_tasks(self):
        """
        取消所有正在运行的任务，包括API调用和子代理任务
        在收到中断信号时由AgentService调用
        """
        try:
            # 设置中断标志
            self._interrupted = True
            
            # 尝试取消metadata extract agent的任务
            try:
                # 安全地尝试调用子代理的取消方法，即使方法不存在也不会抛出异常
                if self.metadata_extract_agent and hasattr(self.metadata_extract_agent, 'cancel_running_tasks'):
                    getattr(self.metadata_extract_agent, 'cancel_running_tasks')()
            except Exception as e:
                print(f"无法取消metadata extract agent任务: {e}")
            
            # 尝试取消search agent的任务
            try:
                if self.search_agent and hasattr(self.search_agent, 'cancel_running_tasks'):
                    getattr(self.search_agent, 'cancel_running_tasks')()
            except Exception as e:
                print(f"无法取消search agent任务: {e}")
            
            # 发布中断事件通知其他组件
            pub.sendMessage(
                MainAgentEvents.LLM_DECISION.value,
                decision="任务中断",
                reason="收到用户中断信号"
            )
            
            # 如果模型支持中断，则中断当前正在进行的模型调用
            try:
                if hasattr(self.model, 'client') and hasattr(self.model.client, 'close'):
                    self.model.client.close()
            except Exception as e:
                print(f"无法关闭模型客户端连接: {e}")
            
            return True
        except Exception as e:
            print(f"取消任务时出错: {e}")
            return False

    def _check_interruption(self) -> bool:
        """检查是否应该中断执行"""
        try:
            # 尝试从线程本地存储获取运行配置
            thread_local = getattr(self.graph, "_thread_local", None)
            if thread_local and hasattr(thread_local, "run_config"):
                run_config = thread_local.run_config
                should_continue = run_config.get("configurable", {}).get("should_continue")
                if callable(should_continue) and not should_continue():
                    return True
                
            # 快速检查如果中断状态已经设置
            if hasattr(self, "_interrupted") and self._interrupted:
                return True
                
            return False
        except Exception:
            # 任何错误都不应中断任务
            return False

def cli_select_option(options: List[Dict[str, str]], hint: str):
    """实现命令行选择功能"""
    import readchar
    import sys

    selected = 0
    
    print(f"\n{hint}")

    def print_options():
        sys.stdout.write("\r" + " " * 100 + "\r")
        for i, option in enumerate(options):
            if i == selected:
                sys.stdout.write(f"[•] {option['label']}  ")
            else:
                sys.stdout.write(f"[ ] {option['label']}  ")
        sys.stdout.flush()

    print_options()

    while True:
        key = readchar.readkey()
        if key == readchar.key.LEFT and selected > 0:
            selected -= 1
            print_options()
        elif key == readchar.key.RIGHT and selected < len(options) - 1:
            selected += 1
            print_options()
        elif key == readchar.key.ENTER:
            sys.stdout.write("\n")
            return options[selected]["value"]


def get_user_feedback():
    """处理用户交互，返回用户反馈"""
    choice = cli_select_option(
        options=[
            {
                "label": "认可，开始检索",
                "value": "continue"
            },
            {
                "label": "修改核查计划",
                "value": "revise"
            }
        ], 
        hint="您是否认可当前的核查计划？"
    )

    if choice == "continue":
        return {"action": "continue"}
    else:
        print("\n请输入您的修改建议：")
        feedback = input("> ")
        return {"action": "revise", "feedback": feedback}
