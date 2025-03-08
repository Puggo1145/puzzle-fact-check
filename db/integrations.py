from typing import Dict, List, Optional, TYPE_CHECKING

from .repository import (
    NewsTextRepository,
    MetadataRepository,
    CheckPointRepository,
    SearchRepository
)
from .schema import (
    NewsText,
    BasicMetadata,
    CheckPoint,
    RetrievalStep,
    SearchResult,
)
from .services import DatabaseService


# 使用TYPE_CHECKING条件导入来避免循环导入
if TYPE_CHECKING:
    from agents.metadata_extractor.states import MetadataState
    from agents.main.states import CheckPoint as CheckPointState
    from agents.searcher.states import SearchAgentState


class AgentDatabaseIntegration:
    """
    位于 Agent 和 database operations 之间的 Integration layer
    该类用于提供向数据库存储 agent 状态到方法
    """
    
    def __init__(self):
        # 将 nodes 全部按需提取到 runtime 方便追踪对应层级的 node 对其操作
        self.news_text_node = None
        self.check_point_nodes: Dict[str, CheckPoint] = {}
        self.retrieval_step_nodes: Dict[str, RetrievalStep] = {}
    
    def initialize_with_news_text(self, news_text: str) -> NewsText:
        self.news_text_node = NewsTextRepository.create_or_find(news_text)
        return self.news_text_node
    
    def store_metadata_state(
        self, 
        metadata_state: "MetadataState"
    ) -> Optional[BasicMetadata]:
        if not self.news_text_node:
            raise ValueError("News text node not initialized. Call initialize_with_news_text first.")
        
        return MetadataRepository.store_metadata_from_state(self.news_text_node, metadata_state)
    
    def store_check_points(
        self, 
        check_points: List["CheckPointState"]
    ) -> Dict[str, CheckPoint]:
        if not self.news_text_node:
            raise ValueError("News text node not initialized. Call initialize_with_news_text first.")
        
        CheckPointRepository.store_check_points_from_state(self.news_text_node, check_points)
        
        # 从 db 创建好的 nodes 中，将 check point nodes 和 retrieval step nodes 存入内存以供后续操作
        for check_point in CheckPoint.nodes.all():
            self.check_point_nodes[check_point.content] = check_point
            
        for step in RetrievalStep.nodes.all():
            self.retrieval_step_nodes[step.purpose] = step
        
        return self.check_point_nodes
    
    def store_search_results(
        self, 
        search_state: "SearchAgentState"
    ) -> Optional[SearchResult]:
        if not self.retrieval_step_nodes:
            raise ValueError("No retrieval steps found. Store check points first.")
        
        # 找到对应的 retrieval step node
        retrieval_step_node = self.get_retrieval_step_node(search_state.purpose)
        if not retrieval_step_node:
            raise ValueError(f"Retrieval step with purpose '{search_state.purpose}' not found.")
        
        return SearchRepository.store_search_results_from_state(retrieval_step_node, search_state)
    
    def get_check_point_node(self, content: str) -> Optional[CheckPoint]:
        return self.check_point_nodes.get(content)
    
    def get_retrieval_step_node(self, purpose: str) -> Optional[RetrievalStep]:
        return self.retrieval_step_nodes.get(purpose)