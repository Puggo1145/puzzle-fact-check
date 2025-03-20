from __future__ import annotations

from neomodel import db
from neomodel.exceptions import DoesNotExist
from .schema import (
    NewsText as NewsTextNode,
    BasicMetadata as BasicMetadataNode,
    Knowledge as KnowledgeNode,
    CheckPoint as CheckPointNode,
    RetrievalStep as RetrievalStepNode,
    SearchResult as SearchResultNode,
    Evidence as EvidenceNode
)

from typing import List, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from agents.metadata_extractor.states import BasicMetadata, Knowledge
    from agents.searcher.states import Evidence, SearchResult


class DatabaseService:
    """
    处理具体数据库操作的 Database service layer .
    """
    
    @staticmethod
    def create_news_text(content: str) -> NewsTextNode:
        return NewsTextNode(content=content).save()
    
    @staticmethod
    def store_basic_metadata(
        news_text_node, 
        basic_metadata: BasicMetadata
    ) -> Optional[BasicMetadataNode]:
        if not basic_metadata:
            return None
           
        basic_metadata_node = BasicMetadataNode(
            news_type=basic_metadata.news_type,
            who=basic_metadata.who,
            when=basic_metadata.when,
            where=basic_metadata.where,
            what=basic_metadata.what,
            why=basic_metadata.why,
            how=basic_metadata.how,
        ).save()
        news_text_node.has_basic_metadata.connect(basic_metadata_node)
        
        return basic_metadata_node
    
    @staticmethod
    def store_retrieved_knowledge(
        news_text_node, 
        knowledge: Knowledge
    ) -> None:
        knowledge_node = KnowledgeNode(
            term=knowledge.term,
            category=knowledge.category,
            description=knowledge.description,
            source=knowledge.source
        ).save()
        news_text_node.has_knowledge.connect(knowledge_node)
        
    
    @staticmethod
    def store_check_point(
        news_text_node, 
        check_point_content: str, 
        retrieval_step_purpose: str,
        retrieval_step_expected_sources: List[str]
    ) -> None:
        check_point_node = CheckPointNode.nodes.first_or_none(content=check_point_content)
        if not check_point_node:
            check_point_node = CheckPointNode(
                content=check_point_content,
            ).save()
        news_text_node.has_check_point.connect(check_point_node)
            
        retrieval_step_node = RetrievalStepNode(
            purpose=retrieval_step_purpose,
            expected_sources=retrieval_step_expected_sources
        ).save()
        check_point_node.verified_by.connect(retrieval_step_node)
        
    
    @staticmethod
    def store_search_evidences(
        retrieval_step_node,
        evidences: List[Evidence]
    ) -> None:
        for evidence in evidences:
            evidence_node = EvidenceNode(
                content=evidence.content,
                source=evidence.source,
                relationship=evidence.relationship,
                reasoning=evidence.reasoning
            ).save()
            
            if evidence.relationship.lower() == "support":
                retrieval_step_node.supports_by.connect(evidence_node)
            elif evidence.relationship.lower() == "contradict":
                retrieval_step_node.contradicts_with.connect(evidence_node)
                
    @staticmethod
    def store_search_results(
        retrieval_step_node, 
        search_result: SearchResult
    ) -> None:
        # Search Result Nodes
        search_result_node = SearchResultNode(
            summary=search_result.summary,
            conclusion=search_result.conclusion,
            confidence=search_result.confidence,
        ).save()
        retrieval_step_node.has_result.connect(search_result_node)
        
    @staticmethod
    def find_news_text_by_content(content: str) -> Optional[NewsTextNode]:
        try:
            return NewsTextNode.nodes.filter(content=content).first()
        except DoesNotExist:
            return None
    
    @staticmethod
    def find_retrieval_step_by_purpose(check_point_node: CheckPointNode, purpose: str) -> Optional[RetrievalStepNode]:
        try:
            retrieval_steps = list(RetrievalStepNode.nodes.filter(verified_by=check_point_node))
            
            for step in retrieval_steps:
                if step.purpose == purpose:
                    return step
        except Exception:
            pass
                
        return None
    
    @staticmethod
    def transaction(func):
        """Decorator to wrap database operations in a transaction."""
        def wrapper(*args, **kwargs):
            with db.transaction:
                return func(*args, **kwargs)
        return wrapper 