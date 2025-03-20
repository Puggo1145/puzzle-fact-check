import json
import uuid
from agents.base import BaseAgent
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph.state import CompiledStateGraph, StateGraph, END
from langgraph.types import interrupt, Command
from .prompts import (
    fact_check_plan_prompt_template,
    fact_check_plan_output_parser,
    human_feedback_prompt_template,
    evaluate_search_result_output_parser,
    evaluate_search_result_prompt_template,
    write_fact_checking_report_prompt_template,
)
from ..searcher.states import SearchAgentState
from ..searcher.graph import SearchAgentGraph
from ..metadata_extractor.graph import MetadataExtractAgentGraph
from ..metadata_extractor.states import MetadataState, Knowledge, BasicMetadata

from pubsub import pub
from .events import MainAgentEvents, CLIModeEvents, DBEvents

from langgraph.pregel import RetryPolicy

from typing import List, Optional, Any, Dict, Literal
from models import ChatQwen
from langchain_deepseek import ChatDeepSeek
from .states import (
    FactCheckPlanState,
    RetrievalResult,
    RetrievalResultVerification,
    CheckPoint,
    CheckPoints,
    RetrievalStep,
)
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from utils.exceptions import AgentExecutionException


class MainAgent(BaseAgent[ChatDeepSeek | ChatQwen]):
    def __init__(
        self,
        model: ChatDeepSeek | ChatQwen,
        metadata_extract_model: ChatOpenAI | ChatQwen,
        search_model: ChatQwen,
        mode: Literal["CLI", "API"] = "CLI",
        max_search_tokens: int = 5000,
        max_retries: int = 1, # search agent 在一个任务上允许的最多重试次数
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
        
        self.db_events = DBEvents()
        if mode == "CLI":
            self.cli_events = CLIModeEvents()

    def _build_graph(self) -> CompiledStateGraph:
        graph_builder = StateGraph(FactCheckPlanState)

        graph_builder.add_node("initialization", self.initialization)
        graph_builder.add_node("invoke_metadata_extract_agent", self.invoke_metadata_extract_agent)
        graph_builder.add_node("extract_check_point", self.extract_check_point)
        graph_builder.add_node("invoke_search_agent", self.invoke_search_agent)
        graph_builder.add_node("human_verification", self.human_verification)
        graph_builder.add_node(
            node="evaluate_search_result", 
            action=self.evaluate_search_result, 
            retry=RetryPolicy(
                max_attempts=3,
                retry_on=ValueError
            )
        )
        graph_builder.add_node("write_fact_checking_report", self.write_fact_checking_report)

        graph_builder.set_entry_point("initialization")
        graph_builder.add_edge("initialization", "invoke_metadata_extract_agent")
        graph_builder.add_edge("invoke_metadata_extract_agent", "extract_check_point")
        graph_builder.add_edge("extract_check_point", "human_verification")

        graph_builder.add_conditional_edges(
            "human_verification",
            self.should_continue_to_retrieval,
            ["extract_check_point", END, "invoke_search_agent"],
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
            checkpointer=self.memory_saver,
        )
        
    def initialization(self, state: FactCheckPlanState):
        pub.sendMessage(
            MainAgentEvents.STORE_NEWS_TEXT.value,
            news_text=state.news_text
        )
        
        return state

    def invoke_metadata_extract_agent(self, state: FactCheckPlanState):
        result = self.metadata_extract_agent.invoke({"news_text": state.news_text})
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
        pub.sendMessage(MainAgentEvents.EXTRACT_CHECK_POINT_START.value)

        messages = [
            fact_check_plan_prompt_template.format(
                news_text=state.news_text,
                basic_metadata=get_basic_metadata_json(state.metadata.basic_metadata), # type: ignore 上一个节点已经处理了 metadata 不存在的情况
                knowledges=get_knowledges_json(state.metadata.retrieved_knowledges), # type: ignore 上一个节点已经处理了 knowledges 不存在的情况
            )
        ]
        # 如果存在人类反馈，将人类反馈嵌入此处
        if state.human_feedback and state.check_points:
            human_feedback_prompt = human_feedback_prompt_template.format(
                human_feedback=state.human_feedback
            )
            messages_with_feedback: List[BaseMessage] = [
                AIMessage(str(state.check_points)),
                human_feedback_prompt,
            ]
            messages.extend(messages_with_feedback)

        response = self.model.invoke(messages)
        check_points: CheckPoints = fact_check_plan_output_parser.invoke(response)
        
        pub.sendMessage(
            MainAgentEvents.EXTRACT_CHECK_POINT_END.value,
            check_points_result=check_points
        )
        
        formatted_check_points = get_formatted_check_points(check_points)  # 只保存需要核查的 check_point

        return {
            "check_points": formatted_check_points,
            "human_feedback": "",
        }

    def human_verification(self, state: FactCheckPlanState):
        """
        Human-in-the-loop
        将检索方案交给人类进行核验，根据反馈开始核查或更新检索方案
        """
        # 中断图的执行，等待人类输入
        result = interrupt(
            {
                "question": "根据您提供的新闻文本，我规划了以下事实核查方案:\n\n"
                + f"{state.check_points}\n"
                + "选择 'continue' 开始核查，或输入修改建议",
            }
        )

        if result == "revise":
            return Command(goto="extract_check_point")
        else:
            return Command(resume="")

    def should_continue_to_retrieval(self, state: FactCheckPlanState):
        """
        决定是否继续执行检索
        如果有 check point 和 basic_metadata，则创建检索任务
        如果没有，则结束图的执行
        """
        # 如果存在人类反馈，重新提取核查点
        if state.human_feedback:
            return "extract_check_point"

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
        current_task = self._get_current_retrieval_task(state)
        if not current_task:
            raise AgentExecutionException(
                agent_type="main",
                message="无法找到检索任务",
            )
        
        self.retries += 1
        
        result = self.search_agent.invoke(current_task)
        
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
    def invoke(self, initial_state: Any, config: Optional[RunnableConfig] = None):
        if not config or not config.get("configurable"):
            raise ValueError("Agent 缺少 thread_id 配置")

        result = super().invoke(initial_state, config)

        if self.mode == "CLI":
            thread_config = config.get("configurable", {})
            while True:
                states = self.graph.get_state({"configurable": thread_config})
                interrupts = (
                    states.tasks[0].interrupts if len(states.tasks) > 0 else False
                )
                if interrupts:
                    result = get_user_feedback()

                    if result["action"] == "continue":
                        super().invoke(
                            Command(resume="continue"),
                            config={"configurable": thread_config},
                        )
                    else:
                        super().invoke(
                            Command(
                                resume="revise",
                                update={
                                    "human_feedback": result["feedback"],
                                },
                            ),
                            config={"configurable": thread_config},
                        )
                else:
                    break

        return result

def cli_select_option(options, prompt):
    """实现命令行选择功能"""
    import readchar
    import sys

    selected = 0
    print(prompt)

    def print_options():
        sys.stdout.write("\r" + " " * 100 + "\r")
        for i, option in enumerate(options):
            if i == selected:
                sys.stdout.write(f"[•] {option}  ")
            else:
                sys.stdout.write(f"[ ] {option}  ")
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
            return options[selected]


def get_user_feedback():
    """处理用户交互，返回用户反馈"""
    choice = cli_select_option(["continue", "revise"], "请选择操作：")

    if choice == "continue":
        return {"action": "continue"}
    else:
        print("\n请输入您的修改建议：")
        feedback = input("> ")
        return {"action": "revise", "feedback": feedback}


def get_formatted_check_points(check_points: CheckPoints):
    """格式化 check points"""
    formatted_check_points = [
        {
            **check_point.model_dump(),
            "id": str(uuid.uuid4()),  # 为每个 check point 生成唯一 id
            "retrieval_step": [
                {
                    **retrieval_step.model_dump(),
                    "id": str(uuid.uuid4()),  # 为每个 retrieval step 生成唯一 id
                }
                for retrieval_step in check_point.retrieval_step # type: ignore 是核查点必存在
            ],
        }
        for check_point in check_points.items
        if check_point.is_verification_point
    ]
    
    return formatted_check_points


def get_basic_metadata_json(basic_metadata: BasicMetadata):
    """格式化 basic metadata"""
    formatted_basic_metadata = {
        "新闻类型": basic_metadata.news_type,
        "时间": basic_metadata.when,
        "地点": basic_metadata.where,
        "人物": basic_metadata.who,
        "事件": basic_metadata.what,
        "原因": basic_metadata.why,
        "过程": basic_metadata.how,
    }
    
    return json.dumps(formatted_basic_metadata, ensure_ascii=False)


def get_knowledges_json(knowledges: List[Knowledge]):
    """格式化 knowledges"""
    formatted_knowledges = [
        {
            "名称": knowledge.term,
            "类别": knowledge.category,
            "定义": knowledge.description,
        }
        for knowledge in knowledges
    ]
    
    return json.dumps(formatted_knowledges, ensure_ascii=False)
