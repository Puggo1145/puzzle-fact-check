from typing import List, Optional, TYPE_CHECKING
from neomodel import db
from neomodel.exceptions import DoesNotExist

from .schema import (
    NewsText,
    BasicMetadata,
    Knowledge,
    CheckPoint,
    RetrievalStep,
    SearchResult,
    Evidence
)

# 使用TYPE_CHECKING条件导入来避免循环导入
if TYPE_CHECKING:
    from agents.metadata_extractor.states import MetadataState
    from agents.main.states import CheckPoint as CheckPointState
    from agents.searcher.states import SearchAgentState


class DatabaseService:
    """
    处理具体数据库操作的 Database service layer .
    """
    
    @staticmethod
    def create_news_text(content: str) -> NewsText:
        return NewsText(content=content).save()
    
    @staticmethod
    def store_metadata(news_text_node, metadata_state: "MetadataState") -> Optional[BasicMetadata]:
        if not metadata_state.basic_metadata:
            return None
           
        # Basic Metadata Node 
        basic_metadata_node = BasicMetadata(
            news_type=metadata_state.basic_metadata.news_type,
            who=metadata_state.basic_metadata.who,
            when=metadata_state.basic_metadata.when,
            where=metadata_state.basic_metadata.where,
            what=metadata_state.basic_metadata.what,
            why=metadata_state.basic_metadata.why,
            how=metadata_state.basic_metadata.how,
        ).save()
        
        news_text_node.has_basic_metadata.connect(basic_metadata_node)
        
        # Knowledge Nodes
        for knowledge_item in metadata_state.retrieved_knowledges:
            knowledge_node = Knowledge(
                term=knowledge_item.term,
                category=knowledge_item.category,
                description=knowledge_item.description,
                source=knowledge_item.source
            ).save()
            
            news_text_node.has_knowledge.connect(knowledge_node)
            
        return basic_metadata_node
    
    @staticmethod
    def store_check_points(news_text_node, check_points: List["CheckPointState"]) -> List[CheckPoint]:
        db_check_points = []
        
        for check_point in check_points:
            check_point_node = CheckPoint(
                content=check_point.content,
                is_verification_point=check_point.is_verification_point,
                importance=check_point.importance
            ).save()
            
            news_text_node.has_check_point.connect(check_point_node)
            
            # 分离 CheckPoint 下的 RetrievalStep
            if check_point.retrieval_step:
                for step in check_point.retrieval_step:
                    retrieval_step = RetrievalStep(
                        purpose=step.purpose,
                        expected_sources=step.expected_sources
                    ).save()
                    
                    check_point_node.verified_by.connect(retrieval_step)
            
            db_check_points.append(check_point)
            
        return db_check_points
    
    @staticmethod
    def store_search_results(
        retrieval_step_node, 
        search_state: "SearchAgentState"
    ) -> Optional[SearchResult]:
        if not search_state.result:
            return None
            
        # Search Result Nodes
        search_result_node = SearchResult(
            summary=search_state.result.summary,
            conclusion=search_state.result.conclusion,
            confidence=search_state.result.confidence,
            sources=search_state.result.sources
        ).save()
        
        retrieval_step_node.has_result.connect(search_result_node)
        
        # Evidence Nodes
        for evidence in search_state.evidences:
            evidence_node = Evidence(
                content=evidence.content,
                source=evidence.source,
                relationship=evidence.relationship,
                reasoning=evidence.reasoning
            ).save()
            
            if evidence.relationship.lower() == "support":
                retrieval_step_node.supports_by.connect(evidence_node)
            elif evidence.relationship.lower() == "contradict":
                retrieval_step_node.contradicts_with.connect(evidence_node)
                
        return search_result_node
    
    @staticmethod
    def find_news_text_by_content(content: str) -> Optional[NewsText]:
        try:
            return NewsText.nodes.filter(content=content).first()
        except DoesNotExist:
            return None
    
    @staticmethod
    def find_retrieval_step_by_purpose(check_point_node: CheckPoint, purpose: str) -> Optional[RetrievalStep]:
        try:
            retrieval_steps = list(RetrievalStep.nodes.filter(verified_by=check_point_node))
            
            for step in retrieval_steps:
                if step.purpose == purpose:
                    return step
        except Exception:
            pass
                
        return None
    
    @staticmethod
    # 你妈的，直接用 Cypher 暴力查了
    def get_retrieval_steps_for_check_point(check_point: CheckPoint) -> List[RetrievalStep]:
       """Get all retrieval steps for a check point"""
       try:
           # 使用 Cypher 查询来获取与 check_point 相关联的 RetrievalStep 节点
           # 通过 check_point 的 content 属性来匹配
           query = """
           MATCH (c:CheckPoint {content: $content})<-[:VERIFIED_BY]-(r:RetrievalStep)
           RETURN r
           """
           
           # 执行查询
           results, _ = db.cypher_query(
               query, 
               {"content": check_point.content}
            )
           
           # 将结果转换为 RetrievalStep 对象
           retrieval_steps = [RetrievalStep.inflate(row[0]) for row in results]
           
           return retrieval_steps
       except Exception as e:
           print(f"Error getting retrieval steps: {e}")
           return []
    
    @staticmethod
    def transaction(func):
        """Decorator to wrap database operations in a transaction."""
        def wrapper(*args, **kwargs):
            with db.transaction:
                return func(*args, **kwargs)
        return wrapper 