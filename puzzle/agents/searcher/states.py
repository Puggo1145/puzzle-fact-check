import operator
from typing import List, Union, Literal, Optional, Dict, Annotated
from langchain_core.messages import ToolCall
from pydantic import BaseModel, Field
from ..metadata_extractor.states import BasicMetadata


class Evidence(BaseModel):
    """支持或反对核查目标的重要证据片段"""
    content: str = Field(description="与核查目标高度相关的证据的原文片段")
    source: Dict[str, str] = Field(
        description="证据来源",
        examples=[{"xx新闻": "https://www.example_news.com"}]
    )
    reasoning: str = Field(description="该证据与核查目标之间关系的推理说明")
    relationship: Literal["support", "contradict"] = Field(
        description="该证据与核查目标的关系",
    )


class Status(BaseModel):
    new_evidence: Optional[List[Evidence]] = Field(
        description="从当前检索结果中提取的证据片段",
        default=None
    )
    evaluation: str = Field(
        description="简单评估检索结果是否达到上一个步骤的目标"
    )
    missing_information: Optional[str] = Field(
        description="核查目标和当前检索结果之间缺失的证据信息或逻辑关系",
        default=None
    )
    next_step: str = Field(description="基于已有信息规划的下一步")
    action: Union[ToolCall, Literal["answer"]] = Field(
        description="调用工具或回答",
        json_schema_extra={
            "options": [
                "如果你希望调用工具，在此输出工具调用信息",
                "如果你认为现有信息已经满足预期目标，在此输出：'answer'",
            ]
        },
    )


class SearchResult(BaseModel):
    """ search 的核查结论"""
    summary: str = Field(description="对所有检索结果的总结")
    conclusion: str = Field(description="对于核查点真实性的结论")


class SearchAgentState(BaseModel):
    check_point_id: str
    retrieval_step_id: str
    basic_metadata: BasicMetadata
    content: str = Field(description="从新闻中提取的事实陈述")
    purpose: str = Field(description="你的检索目标")
    expected_source: str = Field(description="期望找到的信息来源类型")
    statuses: Annotated[List[Status], operator.add] = Field(
        description="所有已执行的操作", 
        default=[]
    )
    latest_tool_result: Optional[str] = Field(
        description="最近一次工具调用的结果", 
        default=None
    )
    evidences: Annotated[List[Evidence], operator.add] = Field(
        description="检索中收集的，与核查目标构成重要关系的证据片段",
        default_factory=list
    )
    result: Optional[SearchResult] = Field(
        description="最终的检索结果和结论", 
        default=None
    )
