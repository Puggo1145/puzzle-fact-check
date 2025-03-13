import operator
from typing import List, Union, Literal, Optional, Dict, Annotated
from langchain_core.messages import ToolCall
from pydantic import BaseModel, Field
from ..metadata_extractor.states import BasicMetadata


class Evidence(BaseModel):
    """支持或反对核查目标的重要证据片段"""
    content: str = Field(description="与核查目标高度相关的证据原文片段")
    source: Dict[str, str] = Field(
        description="证据来源",
        examples=[{"xx新闻": "https://www.example_news.com"}]
    )
    relationship: Literal["support", "contradict"] = Field(
        description="该证据与核查目标的关系",
        examples=[
            {"support": "该证据支持核查目标"},
            {"contradict": "该证据反对核查目标"},
        ]
    )
    reasoning: str = Field(description="该证据与核查目标之间关系的推理说明")


class Status(BaseModel):
    evaluation: str = Field(
        description="评估上一次检索结果是否达到上一个步骤的目标"
    )
    missing_information: Optional[str] = Field(
        description="核查目标和当前步骤所获取的信息之间缺失的证据信息和逻辑关系",
        default=None
    )
    new_evidence: Optional[List[Evidence]] = Field(
        description="从当前检索信息中提取的证据片段",
        default=None
    )
    memory: str = Field(description="对上一个步骤的检索结果的总结")
    next_step: str = Field(description="基于已有信息规划的下一步目标")
    action: Union[List[ToolCall], Literal["answer"]] = Field(
        description="调用工具或回答",
        json_schema_extra={
            "options": [
                "如果你希望调用工具，请在以[数组]的形式此处输出工具调用信息",
                "如果你认为现有信息已经满足预期目标，请在此处输出：'answer'",
            ]
        },
        default=[],
    )


class SearchResult(BaseModel):
    """ search 的核查结论"""
    summary: str = Field(description="对检索到的信息的总结")
    conclusion: str = Field(description="基于检索到的信息得出的核查点真实性的结论")
    confidence: str = Field(description="对结论的置信度评估")


class SearchAgentState(BaseModel):
    basic_metadata: BasicMetadata
    content: str = Field(description="从新闻中提取的事实陈述")
    purpose: str = Field(description="你的检索目标")
    expected_sources: List[str] = Field(
        description="期望找到的信息来源类型，如官方网站、新闻报道、学术论文等。只需要满足其中一项即可"
    )
    statuses: Annotated[List[Status], operator.add] = Field(
        description="所有已执行的操作", 
        default=[]
    )
    latest_tool_messages: List[str] = Field(
        description="最近一次工具调用的结果", 
        default=[]
    )
    evidences: Annotated[List[Evidence], operator.add] = Field(
        description="检索中收集的，与核查目标构成重要关系的证据片段",
        default_factory=list
    )
    result: Optional[SearchResult] = Field(
        description="最终的检索结果和结论", 
        default=None
    )
    token_usage: int = Field(
        description="模型推理消耗的 token 总量",
        default=0
    )
