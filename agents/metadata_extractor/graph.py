from agents.base import BaseAgent
from langgraph.graph.state import CompiledStateGraph, StateGraph, END
from langgraph.prebuilt import create_react_agent
from langgraph.types import Send
from langchain_openai import ChatOpenAI
from .states import MetadataState, Knowledge
from .prompts import (
    basic_metadata_extractor_prompt_template,
    basic_metadata_extractor_output_parser,
    knowledge_extraction_prompt_template,
    knowledge_extraction_output_parser,
    knowledge_retrieve_prompt
)
from tools import SearchWikipediaTool


class MetadataExtractAgentGraph(BaseAgent[ChatOpenAI]):
    def __init__(
        self, 
        model: ChatOpenAI, 
        verbose: bool = True
    ):
        super().__init__(
            model=model, 
            default_config={"callbacks": []}
        )

        self.tools = [SearchWikipediaTool()]
        self.model_with_tools = self.model.bind_tools(tools=self.tools)

    def _build_graph(self) -> CompiledStateGraph:
        graph_builder = StateGraph(MetadataState)
        graph_builder.add_node("extract_basic_metadata", self.extract_basic_metadata)
        graph_builder.add_node("extract_knowledge", self.extract_knowledge)
        graph_builder.add_node("retrieve_knowledge", self.retrieve_knowledge)

        graph_builder.set_entry_point("extract_basic_metadata")
        graph_builder.add_edge("extract_basic_metadata", "extract_knowledge")
        graph_builder.add_conditional_edges(
            "extract_knowledge",
            self.should_continue_to_retrieval, # type: ignore
            ["retrieve_knowledge"]
        )
        graph_builder.set_finish_point("retrieve_knowledge")

        return graph_builder.compile()

    # nodes
    def extract_basic_metadata(self, state: MetadataState):
        """
        从新闻文本中提取基本元数据，包括新闻类型和新闻六要素（5W1H）

        Returns:
            包含新闻基本元数据的字典，包括新闻类型和六要素
        """
        chain = (
            basic_metadata_extractor_prompt_template
            | self.model
            | basic_metadata_extractor_output_parser
        )
        basic_metadata = chain.invoke({"news_text": state.news_text})

        return {"basic_metadata": basic_metadata}

    def extract_knowledge(self, state: MetadataState):
        """
        从文本中提取知识元素，包括专业术语、关键概念等

        Returns:
            包含知识元素的字典
        """

        chain = (
            knowledge_extraction_prompt_template
            | self.model
            | knowledge_extraction_output_parser
        )
        knowledges = chain.invoke({"news_text": state.news_text})

        return {"knowledges": [knowledges]}

    # 并行执行知识元检索：使用 Send 一次性拓展出多个并发的边，每个边复制一份独立的 state
    def should_continue_to_retrieval(self, state: MetadataState):
        if len(state.knowledges) > 0:
            return [
                Send("retrieve_knowledge", knowledge,)
                for knowledge in state.knowledges
            ]

        return END

    def retrieve_knowledge(self, sub_state: Knowledge):
        """
        使用维基百科检索每个知识元的定义
        """
        sub_graph = create_react_agent(
            model=self.model,
            tools=self.tools,
            prompt=knowledge_retrieve_prompt,
            response_format=Knowledge
        )
        retrieve_message = (
            "user",
            f"你需要检索的知识元是：{sub_state.term}。该知识元的类别是：{sub_state.category}"
        )
        response = sub_graph.invoke({"messages": [retrieve_message]})
        retrieved_knowledge: Knowledge = response["structured_response"]
        
        # 将 Knowledge 对象转换为字典，确保可以正确序列化
        return {"knowledges": [retrieved_knowledge.model_dump()]}
    