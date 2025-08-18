import operator
from typing import List, Union, Literal, Optional, Dict, Annotated
from langchain_core.messages import ToolCall
from pydantic import BaseModel, Field
from ..metadata_extractor.states import BasicMetadata


class Evidence(BaseModel):
    """Supporting or contradicting evidence fragments for the fact-checking goal"""
    content: str = Field(description="The original fragment of evidence highly relevant to the fact-checking goal")
    source: Dict[str, str] = Field(
        description="The source of the evidence",
        examples=[{"xx新闻": "https://www.example_news.com"}]
    )
    reasoning: str = Field(description="The reasoning for the relationship between the evidence and the fact-checking goal")
    relationship: Literal["support", "contradict"] = Field(
        description="The relationship between the evidence and the fact-checking goal",
    )


class Status(BaseModel):
    new_evidence: Optional[List[Evidence]] = Field(
        description="The evidence fragments extracted from the current retrieval result",
        default=None
    )
    evaluation: str = Field(
        description="Simple evaluation of whether the retrieval result meets the goal of the previous step"
    )
    missing_information: Optional[str] = Field(
        description="The missing evidence information or logical relationship between the fact-checking goal and the current retrieval result",
        default=None
    )
    next_step: str = Field(description="The next step based on the existing information")
    action: Union[ToolCall, Literal["answer"]] = Field(
        description="Call tool or answer",
        json_schema_extra={
            "options": [
                "If you want to call a tool, output the tool call information here",
                "If you think the existing information already meets the expected goal, output: 'answer'",
            ]
        },
    )


class SearchResult(BaseModel):
    """The fact-checking conclusion of the search"""
    summary: str = Field(description="The summary of all retrieval results")
    conclusion: str = Field(description="The conclusion of the fact-checking goal")


class SearchAgentState(BaseModel):
    check_point_id: str
    retrieval_step_id: str
    basic_metadata: BasicMetadata
    content: str = Field(description="The fact statement extracted from the news")
    purpose: str = Field(description="Your retrieval goal")
    expected_source: str = Field(description="The expected information source type")
    statuses: Annotated[List[Status], operator.add] = Field(
        description="All executed operations", 
        default=[]
    )
    latest_tool_result: Optional[str] = Field(
        description="The result of the latest tool call", 
        default=None
    )
    evidences: Annotated[List[Evidence], operator.add] = Field(
        description="The evidence fragments collected during retrieval, which are important to the fact-checking goal",
        default_factory=list
    )
    result: Optional[SearchResult] = Field(
        description="The final retrieval result and conclusion", 
        default=None
    )
