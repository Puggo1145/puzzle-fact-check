import uuid
from typing import Any, List
from agents.base import BaseAgent
from langchain_core.messages import AIMessage, BaseMessage
from langchain_deepseek import ChatDeepSeek
from langgraph.graph.state import CompiledStateGraph, StateGraph, END, START
from langgraph.types import interrupt, Command
from .states import FactCheckPlanState
from .prompts import (
    fact_check_plan_prompt_template,
    fact_check_plan_output_parser,
    human_feedback_prompt_template,
)


class PlanAgentGraph(BaseAgent[ChatDeepSeek]):
    def __init__(
        self,
        model: ChatDeepSeek,
    ):
        """初始化 plan agent 参数"""
        super().__init__(model=model, default_config={"callbacks": []})

    def _build_graph(self) -> CompiledStateGraph | Any:
        graph_builder = StateGraph(FactCheckPlanState)

        graph_builder.add_node("extract_check_point", self.extract_check_point)
        graph_builder.add_node("human_verification", self.human_verification)

        graph_builder.set_entry_point("extract_check_point")
        graph_builder.add_edge("extract_check_point", "human_verification")
        graph_builder.set_finish_point("human_verification")

        return graph_builder.compile(
            checkpointer=self.memory_saver,
        )

    # 节点
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
            fact_check_plan_prompt_template.format(news_text=state.news_text)
        ]
        # 如果存在人类反馈，将人类反馈嵌入此处
        if state.human_feedback and state.check_points:
            human_feedback_prompt = human_feedback_prompt_template.format(
                human_feedback=state.human_feedback
            )
            messages_with_feedback: List[BaseMessage] = [
                AIMessage(state.check_points.model_dump_json()),
                human_feedback_prompt
            ]
            messages.extend(messages_with_feedback)

        response = self.model.invoke(messages)
        check_points = fact_check_plan_output_parser.invoke(response)

        # 更新状态
        return {"check_points": check_points}

    def human_verification(self, state: FactCheckPlanState):
        """
        Human-in-the-loop
        将检索方案交给人类进行核验，根据反馈开始核查或更新检索方案
        """
        # 中断图的执行，等待人类输入
        result = interrupt({
            "question": "根据您提供的新闻文本，我规划了以下事实核查方案:\n\n"
            + f"{state.check_points.model_dump_json(indent=4) if state.check_points else 'LLM outputed nothing'}\n"
            + "选择 'continue' 开始核查，或输入修改建议",
        })
        
        if result["action"] == "continue":
            return Command(resume="")
        else:
            return Command(
                goto="extract_check_point",
                update={
                    "human_feedback": result["feedback"],
                },
            )
