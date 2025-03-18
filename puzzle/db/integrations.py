from __future__ import annotations

from .repository import (
    NewsTextRepository,
    MetadataRepository,
    CheckPointRepository,
    SearchRepository
)
from .schema import (
    NewsText as NewsTextNode,
    BasicMetadata as BasicMetadataNode,
    RetrievalStep as RetrievalStepNode,
)
from utils import singleton
from utils.exceptions import AgentExecutionException

from typing import List, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from agents.metadata_extractor.states import BasicMetadata, Knowledge
    from agents.main.states import CheckPoint as CheckPointState
    from agents.searcher.states import SearchResult, Evidence


@singleton
class AgentDatabaseIntegration:
    """
    位于 Agent 和 database operations 之间的 Integration layer
    该类用于提供向数据库存储 agent 状态到方法
    """
    
    def __init__(self):
        # 全局共享 nodes 状态
        self.news_text_node = None
    
    def initialize_with_news_text(self, news_text: str) -> NewsTextNode:
        self.news_text_node = NewsTextRepository.create(news_text)
        return self.news_text_node
    
    def store_basic_metadata(
        self, 
        metadata_state: BasicMetadata
    ) -> Optional[BasicMetadataNode]:
        if not self.news_text_node:
            raise ValueError("News text node not initialized. Call initialize_with_news_text first.")
        
        return MetadataRepository.store_basic_metadata(self.news_text_node, metadata_state)
    
    def store_retrieved_knowledge(
        self,
        knowledge: Knowledge
    ):
        if not self.news_text_node:
            raise ValueError("News text node not initialized. Call initialize_with_news_text first.")
        
        return MetadataRepository.store_retrieved_knowledge(self.news_text_node, knowledge)
    
    def store_check_points(
        self, 
        check_points: List[CheckPointState]
    ):
        if not self.news_text_node:
            raise ValueError("News text node not initialized. Call initialize_with_news_text first.")
        
        CheckPointRepository.store_check_points(self.news_text_node, check_points)
    
    def store_search_evidences(
        self,
        retrieval_step_purpose: str,
        evidences: List[Evidence]
    ) -> None:
        retrieval_step_node = RetrievalStepNode.nodes.get(purpose=retrieval_step_purpose)
        if not retrieval_step_node:
            raise AgentExecutionException(
                agent_type="searcher",
                message=f"Retrieval step with purpose '{retrieval_step_purpose}' not found."
            )
        
        return SearchRepository.store_search_evidences(retrieval_step_node, evidences)
    
    def store_search_results(
        self, 
        retrieval_step_purpose: str,
        search_result: SearchResult
    ) -> None:
        retrieval_step_node = RetrievalStepNode.nodes.get(purpose=retrieval_step_purpose)
        if not retrieval_step_node:
            raise AgentExecutionException(
                agent_type="searcher",
                message=f"Retrieval step with purpose '{retrieval_step_purpose}' not found."
            )
        
        return SearchRepository.store_search_result(retrieval_step_node, search_result)
