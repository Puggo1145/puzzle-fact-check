import operator
from typing import List, Union, Literal, Optional, Dict, Annotated
from pydantic import BaseModel, Field
from agents.metadata_extractor.states import BasicMetadata
from langchain_core.messages import ToolCall


class Evidence(BaseModel):
    """存储支持核查目标的重要证据片段"""
    content: str = Field(description="证据内容的原文片段")
    source: Dict[str, str] = Field(
        description="证据来源",
        examples=[{"xx新闻": "https://www.example_news.com"}]
    )
    relevance: str = Field(description="与核查目标的相关性说明")


class Status(BaseModel):
    evaluation: str = Field(
        description="第一人称评估上一次检索结果是否达到上一个步骤的目标"
    )
    memory: str = Field(description="对上一个步骤的检索结果进行总结")
    new_evidence: Optional[List[Evidence]] = Field(
        description="从当前检索信息中提取的新证据片段",
        default=None
    )
    sub_query: Optional[str] = Field(
        description="对比核查目标和当前步骤获取的信息，得出的子检索关键词",
        default=None
    )
    next_step: str = Field(description="使用第一人称基于已有信息规划的下一步目标")
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


class SearchAgentResult(BaseModel):
    """搜索代理的最终结果"""
    summary: str = Field(description="对所有检索到的信息的总结")
    conclusion: str = Field(description="基于检索到的信息对核查点的结论")
    sources: List[str] = Field(description="支持结论的信息来源列表")
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
    supporting_evidence: Annotated[List[Evidence], operator.add] = Field(
        description="收集到的支持核查目标的重要证据片段",
        default_factory=list
    )
    latest_tool_messages: List[str] = Field(
        description="最近一次工具调用的结果", 
        default=[]
    )
    result: Optional[SearchAgentResult] = Field(
        description="最终的检索结果和结论", 
        default=None
    )
    token_usage: int = Field(
        description="模型推理消耗的 token 总量",
        default=0
    )
