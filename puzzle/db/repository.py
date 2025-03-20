from __future__ import annotations

from .schema import (
    NewsText as NewsTextNode,
    CheckPoint as CheckPointNode,
    RetrievalStep as RetrievalStepNode,
)
from .services import DatabaseService

from typing import Optional, List, TYPE_CHECKING
if TYPE_CHECKING:
    from agents.metadata_extractor.states import BasicMetadata, Knowledge
    from agents.searcher.states import SearchResult, Evidence


class NewsTextRepository:
    @staticmethod
    def create(content: str) -> NewsTextNode:
        """创建一个 NewsText node"""
        return DatabaseService.create_news_text(content)


class MetadataRepository:
    @staticmethod
    @DatabaseService.transaction
    def store_basic_metadata(
        news_text_node: NewsTextNode, 
        basic_metadata: BasicMetadata
    ):
        return DatabaseService.store_basic_metadata(news_text_node, basic_metadata)

    @staticmethod
    @DatabaseService.transaction
    def store_retrieved_knowledge(
        news_text_node: NewsTextNode, 
        knowledge: Knowledge
    ):
        return DatabaseService.store_retrieved_knowledge(news_text_node, knowledge)
    

class CheckPointRepository:
    @staticmethod
    @DatabaseService.transaction
    def store_check_point(
        news_text_node: NewsTextNode, 
        check_point_content: str, 
        retrieval_step_purpose: str,
        retrieval_step_expected_sources: List[str]
    ):
        return DatabaseService.store_check_point(news_text_node, check_point_content, retrieval_step_purpose, retrieval_step_expected_sources)


class SearchRepository:
    @staticmethod
    @DatabaseService.transaction
    def store_search_result(
        retrieval_step_node: RetrievalStepNode, 
        search_result: SearchResult
    ):
        return DatabaseService.store_search_results(retrieval_step_node, search_result)
    
    @staticmethod
    @DatabaseService.transaction
    def store_search_evidences(
        retrieval_step_node: RetrievalStepNode,
        evidences: List[Evidence]
    ):
        return DatabaseService.store_search_evidences(retrieval_step_node, evidences)
    
    @staticmethod
    def find_retrieval_step(
        check_point_node: CheckPointNode, 
        purpose: str
    ) -> Optional[RetrievalStepNode]:
        return DatabaseService.find_retrieval_step_by_purpose(check_point_node, purpose) 