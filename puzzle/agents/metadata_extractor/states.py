import operator
from typing import Optional, List, Annotated
from pydantic import BaseModel, Field

class BasicMetadata(BaseModel):
    news_type: str = Field(description="新闻类型")
    who: Optional[List[str]] = Field(description="新闻中的主要人物或组织", default=None)
    when: Optional[List[str]] = Field(description="事件发生时间", default=None)
    where: Optional[List[str]] = Field(description="事件发生地点", default=None)
    what: Optional[List[str]] = Field(description="新闻中发生的主要事件", default=None)
    why: Optional[List[str]] = Field(description="事件发生原因", default=None)
    how: Optional[List[str]] = Field(description="事件发生过程", default=None)


class Knowledge(BaseModel):
    term: str = Field(description="知识元素的名称或术语")
    category: str = Field(
        description="知识元的类别，如'专业术语'、'历史事件'、'科学概念'等"
    )
    description: Optional[str] = Field(description="检索到的知识元的简要定义或解释", default=None)
    source: Optional[str] = Field(description="知识元定义或解释的来源链接", default=None)


class Knowledges(BaseModel):
    items: List[Knowledge] = Field(description="新闻文本中的知识元", default_factory=list)


class MetadataState(BaseModel):
    news_text: str = Field(description="待分析的新闻文本")
    basic_metadata: Optional[BasicMetadata] = Field(default=None)
    knowledges: List[Knowledge] = Field(description="新闻文本中的知识元", default_factory=list)
    retrieved_knowledges: Annotated[List[Knowledge], operator.add] = Field(description="检索完成后的知识元", default_factory=list)
    