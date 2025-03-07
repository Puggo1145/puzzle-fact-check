import operator
from typing import Optional, List, Annotated
from pydantic import BaseModel, Field
from agents.metadata_extractor.states import MetadataState


class RetrievalStep(BaseModel):
    purpose: str = Field(
        description="该检索步骤的目的，想要获取什么信息",
    )
    expected_sources: List[str] = Field(
        description="期望找到的信息来源类型，如官方网站、新闻报道、学术论文等",
        default=[],
    )


class CheckPoint(BaseModel):
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
    check_points: Annotated[List[CheckPoint], operator.add]
    human_feedback: Optional[str] = Field(
        description="人类对于核查方案的评估结果",
        default=None
    )
