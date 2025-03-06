from typing import List
from agents.base import BaseAgent
from langchain_core.messages import AIMessage, BaseMessage
from langchain_deepseek import ChatDeepSeek
from models import ChatQwen
from langgraph.graph.state import CompiledStateGraph, StateGraph, END, START
from langgraph.types import interrupt, Command, Send
from .states import FactCheckPlanState
from .prompts import (
    fact_check_plan_prompt_template,
    fact_check_plan_output_parser,
    human_feedback_prompt_template,
)
from .callback import PlanAgentCallback


class PlanAgentGraph(BaseAgent[ChatDeepSeek]):
    def __init__(
        self,
        model: ChatDeepSeek,
        metadata_extract_model: ChatQwen,
        search_model: ChatQwen,
        verbose: bool = True,
    ):
        """初始化 plan agent 参数"""
        super().__init__(
            model=model,
            default_config={"callbacks": [PlanAgentCallback(verbose=verbose)]},
        )

        """初始化子 agent 模型"""
        self.metadata_extract_model = metadata_extract_model
        self.search_model = search_model
        
    def _build_graph(self) -> CompiledStateGraph:
        graph_builder = StateGraph(FactCheckPlanState)

        graph_builder.add_node("extract_check_point", self.extract_check_point)
        graph_builder.add_node("invoke_metadata_extract_agent", self.invoke_metadata_extract_agent)
        graph_builder.add_node("invoke_search_agent", self.invoke_search_agent)
        graph_builder.add_node("human_verification", self.human_verification)

        graph_builder.add_edge(START, "invoke_metadata_extract_agent")
        graph_builder.add_edge(START, "extract_check_point")
        graph_builder.add_edge("extract_check_point", "human_verification")
        
        graph_builder.add_conditional_edges(
            "human_verification",
            self.should_continue_to_parallel_retrieval,
            ["extract_check_point", END, "invoke_search_agent"]
        )
        
        graph_builder.set_finish_point("invoke_search_agent")

        return graph_builder.compile(
            checkpointer=self.memory_saver,
        )

    # nodes
    def extract_check_point(self, state: FactCheckPlanState):
        """
        对新闻文本进行核查前规划：
        1. 提取陈述
        2. 评估每个陈述，确定核查点
        3. 规划检索方案

        Returns:
            核查方案 JSON
        """
        messages = [fact_check_plan_prompt_template.format(news_text=state.news_text)]
        # 如果存在人类反馈，将人类反馈嵌入此处
        if state.human_feedback and state.check_points:
            human_feedback_prompt = human_feedback_prompt_template.format(
                human_feedback=state.human_feedback
            )
            messages_with_feedback: List[BaseMessage] = [
                AIMessage(state.check_points.model_dump_json()),
                human_feedback_prompt,
            ]
            messages.extend(messages_with_feedback)

        response = self.model.invoke(messages)
        check_points = fact_check_plan_output_parser.invoke(response)

        # 更新核查点并清除上一次反馈
        return {
            "check_points": check_points,
            "human_feedback": ""
        }

    def human_verification(self, state: FactCheckPlanState):
        """
        Human-in-the-loop
        将检索方案交给人类进行核验，根据反馈开始核查或更新检索方案
        """
        # 中断图的执行，等待人类输入
        result =  interrupt(
            {
                "question": "根据您提供的新闻文本，我规划了以下事实核查方案:\n\n"
                + f"{state.check_points.model_dump_json(indent=4) if state.check_points else 'LLM outputed nothing'}\n"
                + "选择 'continue' 开始核查，或输入修改建议",
            }
        )
        
        if result == "revise":
            return Command(goto="extract_check_point")
        else:
            return Command(resume="")
        
            
    def invoke_metadata_extract_agent(self, state: FactCheckPlanState):
        """调用知识元检索 agent 补充"""
        from agents import MetadataExtractAgentGraph
        
        metadata_extract_agent = MetadataExtractAgentGraph(
            model=self.metadata_extract_model,
            verbose=False
        )
        result = metadata_extract_agent.invoke({"news_text": state.news_text})

        return {"metadata": result}
    
    def should_continue_to_parallel_retrieval(self, state: FactCheckPlanState):
        """
        决定是否继续执行并行检索
        如果有检查点和基本元数据，则创建并行检索任务
        如果没有，则结束图的执行
        """
        if state.human_feedback:
            return "extract_check_point"
        
        if (
            state.check_points and 
            state.metadata and 
            state.metadata.basic_metadata
        ):
            from agents.searcher.states import SearchAgentState
            
            retrieval_plans = []
            for check_point in state.check_points.items:
                if not check_point.retrieval_plan:
                    continue

                for retrieval_step in check_point.retrieval_plan:
                    retrieval_plans.append(
                        Send(
                            "invoke_search_agent",
                            SearchAgentState(
                                basic_metadata=state.metadata.basic_metadata,
                                content=check_point.content,
                                purpose=retrieval_step.purpose,
                                expected_sources=retrieval_step.expected_sources,
                            ),
                        )
                    )
                    
            if retrieval_plans:
                return retrieval_plans
        
        return END

    def invoke_search_agent(self, state):
        """根据检索规划调用子检索模型执行深度检索"""
        from agents import SearchAgentGraph

        search_agent = SearchAgentGraph(model=self.search_model, max_tokens=12000)
        search_agent.invoke(state)
