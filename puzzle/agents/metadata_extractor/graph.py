from agents.base import BaseAgent
from langgraph.graph.state import StateGraph, END
from langgraph.prebuilt import create_react_agent
from langgraph.types import Send
from .prompts import (
    basic_metadata_extractor_prompt_template,
    knowledge_extraction_prompt_template,
    knowledge_retrieve_prompt
)
from tools import SearchWikipediaTool

from .states import MetadataState, BasicMetadata, Knowledge, Knowledges
from langchain_openai.chat_models.base import BaseChatOpenAI
from langgraph.graph.state import CompiledStateGraph


class MetadataExtractAgentGraph(BaseAgent):
    """
    Metadata Extrct Agent: 负责提取新闻文本的类型和要素
    """
    def __init__(
        self, 
        model: BaseChatOpenAI,
    ):
        super().__init__(model=model)
        
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
            ["retrieve_knowledge", END]
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
        prompt = basic_metadata_extractor_prompt_template.format(news_text=state.news_text)
        basic_metadata = self.model.with_structured_output(BasicMetadata).invoke(prompt)
        
        return {"basic_metadata": basic_metadata}

    def extract_knowledge(self, state: MetadataState):
        """
        从文本中提取知识元素，包括专业术语、关键概念等

        Returns:
            包含知识元素的字典
        """
        prompt = knowledge_extraction_prompt_template.format(news_text=state.news_text)
        knowledges = self.model.with_structured_output(Knowledges).invoke(prompt)
        
        return {"knowledges": knowledges.items}

    # 并行执行知识元检索：使用 Send 一次性拓展出多个并发的边，每个边复制一份独立的 state
    def should_continue_to_retrieval(self, state: MetadataState):
        if state.knowledges and len(state.knowledges) > 0:
            return [
                Send("retrieve_knowledge", knowledge)
                for knowledge in state.knowledges
            ]
        else:
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
            f"The knowledge element you need to retrieve is: {sub_state.term}. The category of the knowledge element is: {sub_state.category}"
        )
        response = sub_graph.invoke({"messages": [retrieve_message]})
        retrieved_knowledge: Knowledge = response["structured_response"]
        
        # 返回检索到的知识元
        return {"retrieved_knowledges": [retrieved_knowledge]}
    