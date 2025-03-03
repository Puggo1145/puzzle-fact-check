from agents.base import BaseAgent
from langgraph.graph.state import CompiledStateGraph, StateGraph
from langchain.chat_models.base import BaseChatModel
from .states import MetadataState
from .prompts import (
    basic_metadata_extractor_prompt_template,
    basic_metadata_extractor_output_parser,
    knowledge_extraction_prompt_template,
    knowledge_extraction_output_parser
)


class MetadataExtractorAgent(BaseAgent):
    def __init__(
        self, 
        model: BaseChatModel, 
        verbose: bool = True
    ):
        super().__init__(
            model=model, 
            default_config={"callbacks": []}
        )

    def _build_graph(self) -> CompiledStateGraph:
        graph_builder = StateGraph(MetadataState)
        graph_builder.add_node("extract_basic_metadata", self.extract_basic_metadata)
        graph_builder.add_node("extract_knowledge", self.extract_knowledge)
        
        graph_builder.set_entry_point("extract_basic_metadata")
        graph_builder.add_edge("extract_basic_metadata", "extract_knowledge")
        graph_builder.set_finish_point("extract_knowledge")

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
        
        return {"knowledges": knowledges["items"]}
    