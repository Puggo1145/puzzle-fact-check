from typing import List, Optional, Any
from agents.base import BaseAgent
from langchain_core.runnables import RunnableConfig
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
from .callback import MainAgentCallback
from ..searcher.states import SearchAgentState
from ..searcher.graph import SearchAgentGraph
from ..metadata_extractor.graph import MetadataExtractAgentGraph


class MainAgent(BaseAgent[ChatDeepSeek | ChatQwen]):
    def __init__(
        self,
        model: ChatDeepSeek | ChatQwen,
        metadata_extract_model: ChatQwen,
        search_model: ChatQwen,
        cli_mode: bool = True
    ):
        """初始化 plan agent 参数"""
        super().__init__(
            model=model,
            default_config={"callbacks": [MainAgentCallback()]},
            cli_mode=cli_mode
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

        # graph_builder.add_edge(START, "invoke_metadata_extract_agent")
        graph_builder.add_edge(START, "extract_check_point")
        graph_builder.add_edge("extract_check_point", "human_verification")
        
        # graph_builder.add_conditional_edges(
        #     "human_verification",
        #     self.should_continue_to_parallel_retrieval,
        #     ["extract_check_point", END, "invoke_search_agent"]
        # )
        
        # graph_builder.set_finish_point("invoke_search_agent")

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
                AIMessage(str(state.check_points)),
                human_feedback_prompt,
            ]
            messages.extend(messages_with_feedback)

        response = self.model.invoke(messages)
        check_points = fact_check_plan_output_parser.invoke(response)
        
        # 更新核查点并清除上一次反馈
        return {
            "check_points": check_points["items"],
            "human_feedback": ""
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
        
            
    def invoke_metadata_extract_agent(self, state: FactCheckPlanState):
        """调用知识元检索 agent 补充"""
        metadata_extract_agent = MetadataExtractAgentGraph(model=self.metadata_extract_model)
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
            retrieval_steps = []
            for check_point in state.check_points:
                if not check_point.retrieval_step:
                    continue

                for retrieval_step in check_point.retrieval_step:
                    retrieval_steps.append(
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
                    
            if retrieval_steps:
                return retrieval_steps
        
        return END

    def invoke_search_agent(self, state: SearchAgentState):
        """根据检索规划调用子检索模型执行深度检索"""
        search_agent = SearchAgentGraph(model=self.search_model, max_tokens=12000)
        search_agent.invoke(state)
        
    def evaluate_search_result(self, state: SearchAgentState):
        """主模型对 search agent 的检索结论进行复核推理"""
        pass

    # 重写 invoke 方法以支持 CLI 模式，令 Main Agent 能够在内部处理 human-in-the-loop 流程
    def invoke(
        self, 
        initial_state: Any,
        config: Optional[RunnableConfig] = None
    ):
        if not config or not config.get("configurable"):
            raise ValueError("Agent 缺少 thread_id 配置")
        
        result = super().invoke(initial_state, config)
        
        if self.cli_mode:
            thread_config = config.get("configurable", {})
            while True:
                states = self.graph.get_state({"configurable": thread_config})
                interrupts = states.tasks[0].interrupts if len(states.tasks) > 0 else False
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
