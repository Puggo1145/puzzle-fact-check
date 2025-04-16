"""
Main agent 是 Puzzle Fact Check 的主模型，其主要负责：
1. 核查规划：从新闻文本中提取核查点，并规划检索方案
2. 智能体协调：协调 metadata extractor, search agent 等子模型执行具体的检索任务
3. Supervisor: 对 search agent 的检索结果进行复核，并根据反馈更新核查计划 
4. 报告生成：根据核查结论生成报告
"""

from agents.base import BaseAgent
from langgraph.graph.state import CompiledStateGraph, StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .prompts import (
    check_if_news_text_prompt_template,
    check_if_news_text_output_parser,
    fact_check_plan_prompt_template,
    fact_check_plan_output_parser,
    evaluate_search_result_output_parser,
    evaluate_search_result_prompt_template,
    write_fact_check_report_prompt_template,
    write_fact_check_report_output_parser,
)
from ..searcher.states import SearchAgentState
from ..searcher.graph import SearchAgentGraph
from ..metadata_extractor.graph import MetadataExtractAgentGraph
from ..metadata_extractor.states import MetadataState
from utils.exceptions import AgentExecutionException

from typing import List, Optional, Any, Dict, Literal
from .states import (
    FactCheckPlanState,
    RetrievalResult,
    RetrievalResultVerification,
    CheckPoint,
    CheckPoints,
    RetrievalStep,
    IsNewsText,
    Result,
)
from langchain_openai.chat_models.base import BaseChatOpenAI


class MainAgent(BaseAgent):
    def __init__(
        self,
        model: BaseChatOpenAI,
        metadata_extract_model: BaseChatOpenAI,
        search_model: BaseChatOpenAI,
        selected_tools: List[str],
        max_search_tokens: int = 5000,
        max_retries: int = 1, # main agent 在一个任务上允许的最多重试次数
    ):
        super().__init__(model=model)
        
        self.metadata_extract_model = metadata_extract_model
        self.metadata_extract_agent = MetadataExtractAgentGraph(
            model=metadata_extract_model,
        )
        self.search_agent = SearchAgentGraph(
            model=search_model,
            max_search_tokens=max_search_tokens,
            selected_tools=selected_tools,
        )
        
        # graph 内部动态条件参数
        self.retries = 0
        self.max_retries = max_retries
        self.current_retrieval_task_index = 0  # 跟踪当前检索任务的索引
        self.total_retrieval_tasks_nums = 0  # 总任务数
        
    def _build_graph(self) -> CompiledStateGraph:
        graph_builder = StateGraph(FactCheckPlanState)

        graph_builder.add_node("check_if_news_text", self.check_if_news_text)
        graph_builder.add_node("invoke_metadata_extract_agent", self.invoke_metadata_extract_agent)
        graph_builder.add_node("extract_check_point", self.extract_check_point)
        graph_builder.add_node("invoke_search_agent", self.invoke_search_agent)
        graph_builder.add_node("evaluate_search_result", self.evaluate_search_result)
        graph_builder.add_node("write_fact_check_report", self.write_fact_check_report)

        graph_builder.set_entry_point("check_if_news_text")
        graph_builder.add_conditional_edges(
            "check_if_news_text",
            self.should_continue_to_metadata_extract,
            ["invoke_metadata_extract_agent", END]
        )
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
                "continue": "invoke_search_agent",
                "force_continue": "invoke_search_agent",
                "finish": "write_fact_check_report"
            }
        )
        graph_builder.set_finish_point("write_fact_check_report")

        return graph_builder.compile(
            checkpointer=MemorySaver(),
        )
    
    def check_if_news_text(self, state: FactCheckPlanState):
        """检查用户提供的文本是否为新闻文本"""
        response = self.metadata_extract_model.invoke([
            check_if_news_text_prompt_template.format(
                news_text=state.news_text
            )
        ])
        is_news_text: IsNewsText = check_if_news_text_output_parser.invoke(response)

        return {"is_news_text": is_news_text}
    
    def should_continue_to_metadata_extract(self, state: FactCheckPlanState):
        """
        决定是否继续执行元数据提取
        如果文本不是新闻文本，则结束图的执行
        """
        if not state.is_news_text or not state.is_news_text.result:
            return END
        
        return "invoke_metadata_extract_agent"
        
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
        current_task = self._get_current_retrieval_task(state)
        if not current_task:
            raise AgentExecutionException(
                agent_type="main",
                message="无法找到检索任务",
            )
        
        self.retries += 1
        
        result = self.search_agent.graph.invoke(
            current_task, 
            config={"recursion_limit": 30}
        )
        
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
        if not verification_result.verified and (verification_result.updated_purpose or verification_result.updated_expected_source):
            update_data = {
                "purpose": verification_result.updated_purpose,
                "expected_source": verification_result.updated_expected_source,
            }
            updates.append({"id": current_step.id, "data": update_data})

        updated_check_points = self._batch_update_retrieval_steps(state, updates)
        
        return {"check_points": updated_check_points}

    def should_retry_or_continue(
        self, 
        state: FactCheckPlanState
    ) -> Literal["retry", "continue", "force_continue", "finish"]:        
        """
        根据评估结果决定是重试当前检索任务、继续下一个任务还是完成检索
        """
        # 检查是否已经处理完所有任务
        if self.current_retrieval_task_index >= self.total_retrieval_tasks_nums - 1:
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
            return "retry"

        # 重置重试计数器和更新当前检索任务索引，准备处理下一个任务
        self.retries = 0
        self.current_retrieval_task_index += 1
        
        # 无论主模型是否认可当前检索结果，只要 search agent 重试次数超过最大重试次数，继续下一个任务
        if self.retries > self.max_retries:
            return "force_continue"

        return "continue"
    
    def write_fact_check_report(self, state: FactCheckPlanState):
        """将核查结果写为核查报告"""
        response = self.model.invoke([
            write_fact_check_report_prompt_template.format(
                news_text=state.news_text, 
                check_points=state.check_points
            )
        ])
        result: Result = write_fact_check_report_output_parser.invoke(response)
        
        return {"result": result}
    
    def _get_current_retrieval_task(self, state: FactCheckPlanState) -> SearchAgentState:
        """获取要执行的检索任务"""
        retrieval_tasks = [
            SearchAgentState(
                basic_metadata=state.metadata.basic_metadata, # type: ignore BasicMetadata 不存在的情况已经在前置节点处理
                check_point_id=check_point.id,
                retrieval_step_id=retrieval_step.id,
                content=check_point.content,
                purpose=retrieval_step.purpose,
                expected_source=retrieval_step.expected_source,
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
            if not check_point.retrieval_step:
                raise AgentExecutionException(
                    agent_type="main",
                    message=f"核查点下找不到指定 id 为 {retrieval_step_id} 的检索步骤",
                )
            
            for step in check_point.retrieval_step:
                if step.id == retrieval_step_id:
                    return step
        return None
