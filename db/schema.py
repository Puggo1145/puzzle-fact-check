from typing import Required, Optional
from pydantic import BaseModel, Field
from agents.metadata_extractor.states import BasicMetadata, Knowledge
from agents.planner.states import RetrievalStep
from agents.searcher.states import SearchResult, Evidence


class NewsTextNode(BaseModel):
    content: Required[str] = Field(description="带核查的新闻文本")


class BasicMetadataNode(BasicMetadata):
    """Basic Metadata Node"""


class KnowledgeNode(Knowledge):
    """Knowledge Node"""


class CheckPointNode(BaseModel):
    """CheckPoint Node. 和原 CheckPoint State 相比，不继承 retrieval step"""
    id: int = Field(description="陈述 id")
    content: str = Field(description="从新闻中提取的事实陈述")
    is_verification_point: bool = Field(description="该陈述是否被选为核查点")
    importance: Optional[str] = Field(
        description="若被选为核查点，说明其重要性",
        default=None
    )


class RetrievalStepNode(RetrievalStep):
    """RetrievalStep Node"""


class SearchResultNode(SearchResult):
    """SearchResult Node"""


class EvidenceNode(Evidence):
    """Evidence node"""


def create_node():
    """创建 node 的 factor"""
