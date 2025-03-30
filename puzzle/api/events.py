"""
Agent SSE Event Models
"""
import re
from pydantic import BaseModel
from agents.main.states import CheckPoint, RetrievalResultVerification
from agents.metadata_extractor.states import BasicMetadata, Knowledge
from agents.searcher.states import Status, SearchResult

from typing import Optional, Any, List


def convert_name_to_event(name: str) -> str:
    """
    example:
    OnExtractCheckPointStart -> on_extract_check_point_start
    """
    # 将驼峰式命名转换为下划线式命名
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    # 转换为小写并返回
    return s2.lower()


class BaseEvent(BaseModel):
    event: Optional[str] = None
    data: Any
    
    def __init__(self, **data):
        if "event" not in data:
            data["event"] = convert_name_to_event(self.__class__.__name__)
        super().__init__(**data)


# invoke_metadata_extract_agent
class OnExtractBasicMetadataStart(BaseEvent):
    data: None = None


class OnExtractBasicMetadataEnd(BaseEvent):
    data: BasicMetadata


class OnExtractKnowledgeStart(BaseEvent):
    data: None = None


class OnExtractKnowledgeEnd(BaseEvent):
    data: List[Knowledge]


class OnRetrieveKnowledgeStart(BaseEvent):
    data: None = None


class OnRetrieveKnowledgeEnd(BaseEvent):
    data: Knowledge


class OnExtractCheckPointStart(BaseEvent):
    data: None = None


class OnExtractCheckPointEnd(BaseEvent):
    data: List[CheckPoint]


# invoke_search_agent
class SearchAgentInput(BaseModel):
    content: str
    purpose: str
    expected_sources: List[str]

class OnSearchAgentStart(BaseEvent):
    data: SearchAgentInput


class OnEvaluateCurrentStatusStart(BaseEvent):
    data: None = None


class OnEvaluateCurrentStatusEnd(BaseEvent):
    data: Status


class ToolStartData(BaseModel):
    tool_name: str
    input_str: str

class OnToolStart(BaseEvent):
    data: ToolStartData


class ToolEndData(BaseModel):
    tool_name: str
    output_str: str

class OnToolEnd(BaseEvent):
    data: ToolEndData


class OnGenerateAnswerStart(BaseEvent):
    data: None = None


class OnGenerateAnswerEnd(BaseEvent):
    data: SearchResult


class OnEvaluateSearchResultStart(BaseEvent):
    data: None = None


class OnEvaluateSearchResultEnd(BaseEvent):
    data: RetrievalResultVerification


class LLMDecisionData(BaseModel):
    decision: str


class OnLLMDecision(BaseEvent):
    data: LLMDecisionData


class OnWriteFactCheckReportStart(BaseEvent):
    data: None = None


class FactCheckReportData(BaseModel):
    report: str


class OnWriteFactCheckReportEnd(BaseEvent):
    data: FactCheckReportData
