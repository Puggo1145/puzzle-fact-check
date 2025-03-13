import operator
from typing import Optional, List, Annotated
from pydantic import BaseModel, Field
from ..metadata_extractor.states import MetadataState
from ..searcher.states import SearchResult, Evidence


# 合并了 SearchResult 和 Evidence 的核查结论
class RetrievalResult(SearchResult):
    evidences: Annotated[List[Evidence], operator.add] = Field(
        description="检索中收集的，与核查目标构成重要关系的证据片段",
        default_factory=list
    )


class RetrievalStep(BaseModel):
    id: str
    purpose: str = Field(
        description="该检索步骤的目的，想要获取什么信息",
    )
    expected_sources: List[str] = Field(
        description="期望找到的信息来源类型，如官方网站、新闻报道、学术论文等",
        default=[],
    )
    result: Optional[RetrievalResult] = Field(
        description="由 search agent 执行检索后返回的核查结论",
        default=None
    )


class CheckPoint(BaseModel):
    id: str
    content: str = Field(description="从新闻中提取的事实陈述")
    is_verification_point: bool = Field(description="该陈述是否被选为核查点")
    importance: Optional[str] = Field(
        description="若被选为核查点，说明其重要性",
        default=None
    )
    retrieval_step: Optional[List[RetrievalStep]] = Field(
        description="若被选为核查点，提供检索方案", 
        default=None
    )

    

class CheckPoints(BaseModel):
    items: List[CheckPoint] = Field(description="从新闻文本中提取的核查点", default_factory=list)


class FactCheckPlanState(BaseModel):
    news_text: str = Field(description="待核查的新闻文本")
    metadata: Optional[MetadataState] = Field(description="新闻元数据", default=None)
    check_points: List[CheckPoint] = Field(default_factory=list)
    human_feedback: Optional[str] = Field(
        description="人类对于核查方案的评估结果",
        default=None
    )
