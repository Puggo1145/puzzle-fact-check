"""
Agent SSE Event Models
"""

import re
from pydantic import BaseModel
from agents.main.states import CheckPoint, RetrievalResultVerification, IsNewsText, Result
from agents.metadata_extractor.states import BasicMetadata, Knowledge
from agents.searcher.states import Status, SearchResult

from typing import Optional, Any, List


def convert_name_to_event(name: str) -> str:
    """
    example:
    OnExtractCheckPointStart -> on_extract_check_point_start
    """
    # 将驼峰式命名转换为下划线式命名
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
    # 转换为小写并返回
    return s2.lower()


class BaseEvent(BaseModel):
    event: Optional[str] = None
    data: Any

    def __init__(self, **data):
        if "event" not in data:
            data["event"] = convert_name_to_event(self.__class__.__name__)
        super().__init__(**data)


class OnAgentStart(BaseEvent):
    data: None = None


# check_if_news_text
class CheckIfNewsTextStart(BaseEvent):
    data: None = None


class CheckIfNewsTextEnd(BaseEvent):
    data: IsNewsText


# invoke_metadata_extract_agent
class ExtractBasicMetadataStart(BaseEvent):
    data: None = None


class ExtractBasicMetadataEnd(BaseEvent):
    data: BasicMetadata


class ExtractKnowledgeStart(BaseEvent):
    data: None = None


class ExtractKnowledgeEnd(BaseEvent):
    data: List[Knowledge]


class RetrieveKnowledgeStart(BaseEvent):
    data: None = None


class RetrieveKnowledgeEnd(BaseEvent):
    data: Knowledge


class ExtractCheckPointStart(BaseEvent):
    data: None = None


class ExtractCheckPointEnd(BaseEvent):
    data: List[CheckPoint]


# invoke_search_agent
class SearchAgentInput(BaseModel):
    content: str
    purpose: str
    expected_source: str


class SearchAgentStart(BaseEvent):
    data: SearchAgentInput


class EvaluateCurrentStatusStart(BaseEvent):
    data: None = None


class EvaluateCurrentStatusEnd(BaseEvent):
    data: Status


class GenerateAnswerStart(BaseEvent):
    data: None = None


class GenerateAnswerEnd(BaseEvent):
    data: SearchResult


class EvaluateSearchResultStart(BaseEvent):
    data: None = None


class EvaluateSearchResultEnd(BaseEvent):
    data: RetrievalResultVerification


class LLMDecisionData(BaseModel):
    decision: str


class LLMDecision(BaseEvent):
    data: LLMDecisionData


class WriteFactCheckReportStart(BaseEvent):
    data: None = None


class FactCheckResultData(BaseModel):
    report: str
    verdict: str


class WriteFactCheckReportEnd(BaseEvent):
    data: FactCheckResultData


class ToolStartData(BaseModel):
    tool_name: str
    input_str: str


class ToolStart(BaseEvent):
    data: ToolStartData


class ToolEndData(BaseModel):
    tool_name: str
    output_str: str


class ToolEnd(BaseEvent):
    data: ToolEndData


class TaskComplete(BaseEvent):
    data: None = None


class InterruptData(BaseModel):
    message: str


class TaskInterrupted(BaseEvent):
    data: InterruptData


class ErrorData(BaseModel):
    message: str


class Error(BaseEvent):
    data: ErrorData
