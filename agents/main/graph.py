import uuid
from agents.base import BaseAgent
from langchain_core.messages import AIMessage, BaseMessage
from langgraph.graph.state import CompiledStateGraph, StateGraph, END
from langgraph.types import interrupt, Command, Send
from .states import FactCheckPlanState
from .prompts import (
    fact_check_plan_prompt_template,
    fact_check_plan_output_parser,
    human_feedback_prompt_template,
)
from .callback import MainAgentCallback
from ..searcher.states import SearchAgentState
from ..searcher.graph import SearchAgentGraph
from ..metadata_extractor.graph import MetadataExtractAgentGraph

from typing import List, Optional, Any, Dict, TypedDict
from models import ChatQwen
from langchain_deepseek import ChatDeepSeek
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from utils.exceptions import AgentExecutionException


class MainAgentConfig(TypedDict):
    max_search_tokens: int
    cli_mode: bool


class MainAgent(BaseAgent[ChatDeepSeek | ChatQwen]):
    def __init__(
        self,
        model: ChatDeepSeek | ChatQwen,
        metadata_extract_model: ChatOpenAI | ChatQwen,
        search_model: ChatQwen,
        config: MainAgentConfig,
    ):
        super().__init__(
            model=model,
            default_config={"callbacks": [MainAgentCallback()]},
            cli_mode=config["cli_mode"],
        )

        self.metadata_extract_model = metadata_extract_model
        self.search_model = search_model
        self.max_search_tokens = config["max_search_tokens"]

    def _build_graph(self) -> CompiledStateGraph:
        graph_builder = StateGraph(FactCheckPlanState)

        graph_builder.add_node("store_news_text_to_db", self.store_news_text_to_db)
        graph_builder.add_node("invoke_metadata_extract_agent", self.invoke_metadata_extract_agent)
        graph_builder.add_node("extract_check_point", self.extract_check_point)
        graph_builder.add_node("invoke_search_agent", self.invoke_search_agent)
        graph_builder.add_node("human_verification", self.human_verification)
        graph_builder.add_node(
            "store_check_points_to_db", self.store_check_points_to_db
        )
        graph_builder.add_node("evaluate_search_result", self.evaluate_search_result)

        graph_builder.set_entry_point("store_news_text_to_db")
        graph_builder.add_edge("store_news_text_to_db", "invoke_metadata_extract_agent")
        graph_builder.add_edge("invoke_metadata_extract_agent", "extract_check_point")
        graph_builder.add_edge("extract_check_point", "human_verification")
        graph_builder.add_edge("human_verification", "store_check_points_to_db")

        graph_builder.add_conditional_edges(
            "store_check_points_to_db",
            self.should_continue_to_parallel_retrieval,
            ["extract_check_point", END, "invoke_search_agent"],
        )

        graph_builder.add_edge("invoke_search_agent", "evaluate_search_result")
        graph_builder.set_finish_point("evaluate_search_result")

        return graph_builder.compile(
            checkpointer=self.memory_saver,
        )

    # nodes
    def store_news_text_to_db(self, state: FactCheckPlanState):
        self.db_integration.initialize_with_news_text(state.news_text)
        return state

    def invoke_metadata_extract_agent(self, state: FactCheckPlanState):
        metadata_extract_agent = MetadataExtractAgentGraph(
            model=self.metadata_extract_model
        )
        result = metadata_extract_agent.invoke({"news_text": state.news_text})

        return {"metadata": result}

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
                AIMessage(str(state.check_points)),
                human_feedback_prompt,
            ]
            messages.extend(messages_with_feedback)

        response = self.model.invoke(messages)
        check_points = fact_check_plan_output_parser.invoke(response)

        # 只保存需要核查的 check_point
        formatted_check_points = get_formatted_check_points(check_points)

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

    def store_check_points_to_db(self, state: FactCheckPlanState):
        if len(state.check_points) > 0:
            self.db_integration.store_check_points(state.check_points)

        return state

    def should_continue_to_parallel_retrieval(self, state: FactCheckPlanState):
        """
        决定是否继续执行并行检索
        如果有 check point 和 basic_metadata，则创建并行检索任务
        如果没有，则结束图的执行
        """
        if state.human_feedback:
            return "extract_check_point"

        # 没有核查点或元数据，结束图执行
        if (
            len(state.check_points) < 1
            or not state.metadata
            or not state.metadata.basic_metadata
        ):
            print("无法从文本中提取核查点或元数据，请检查文本")
            return END

        print(f"state.check_points: {state.check_points}")

        # 提取 retireval step 分配检索任务
        retrieval_tasks = []
        for check_point in state.check_points:
            if check_point.retrieval_step:
                for retrieval_step in check_point.retrieval_step:
                    retrieval_tasks.append(Send(
                        "invoke_search_agent",
                        {
                            "state": SearchAgentState(
                                basic_metadata=state.metadata.basic_metadata,
                                content=check_point.content,
                                purpose=retrieval_step.purpose,
                                expected_sources=retrieval_step.expected_sources,
                            ),
                            "check_point_id": check_point.id,
                            "retrieval_step_id": retrieval_step.id,
                        },
                    ))

        # 如果有检索任务，开始检索
        if retrieval_tasks:
            return retrieval_tasks

        return END

    def invoke_search_agent(self, args: Dict[str, Any]):
        """根据检索规划调用子检索模型执行深度检索"""
        return Command(goto=END)
        
        # search_agent = SearchAgentGraph(
        #     model=self.search_model,
        #     max_tokens=self.max_search_tokens,
        # )
        # result = search_agent.invoke(args["state"])

        # # 将结论合并到 main state 中对应的 retrieval step 中
        # state = self.graph.get_state(config=self.default_config)
        # if not isinstance(state, FactCheckPlanState):
        #     raise AgentExecutionException(
        #         agent_type="main",
        #         message="无法获取到 Main Agent 的状态",
        #     )

        # updated_check_points = [
        #     (
        #         cp
        #         if cp.id != args["check_point_id"]
        #         else cp.model_copy(
        #             update={
        #                 "retrieval_step": [
        #                     (
        #                         step
        #                         if step.id != args["retrieval_step_id"]
        #                         else step.model_copy(update={"result": result})
        #                     )
        #                     for step in cp.retrieval_step # type: ignore 此处的 retrieval step 必然存在
        #                 ]
        #             }
        #         )
        #     )
        #     for cp in state.check_points
        # ]

        # return {"check_points": updated_check_points}

    def evaluate_search_result(self, state: SearchAgentState):
        """主模型对 search agent 的检索结论进行复核推理"""
        return state

    # 重写 invoke 方法以支持 CLI 模式，令 Main Agent 能够在内部处理 human-in-the-loop 流程
    def invoke(self, initial_state: Any, config: Optional[RunnableConfig] = None):
        if not config or not config.get("configurable"):
            raise ValueError("Agent 缺少 thread_id 配置")

        result = super().invoke(initial_state, config)

        if self.cli_mode:
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


def get_formatted_check_points(check_points: Dict[str, Any]):
    """格式化 check points"""
    formatted_check_points = [
        {
            **check_point,
            "id": str(uuid.uuid4()),  # 为每个 check point 生成唯一 id
            "retrieval_step": [
                {
                    **retrieval_step,
                    "id": str(uuid.uuid4()),  # 为每个 retrieval step 生成唯一 id
                }
                for retrieval_step in check_point["retrieval_step"]
            ],
        }
        for check_point in check_points["items"]
        if check_point["is_verification_point"]
    ]
    
    return formatted_check_points
