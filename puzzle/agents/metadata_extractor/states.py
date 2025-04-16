import operator
from typing import Optional, List, Annotated, Dict, Any
from pydantic import BaseModel, Field

class BasicMetadata(BaseModel):
    news_type: str = Field(description="新闻类型")
    who: Optional[List[Optional[str]]] = Field(description="新闻中的主要主体", default=None)
    when: Optional[List[Optional[str]]] = Field(description="发生时间", default=None)
    where: Optional[List[Optional[str]]] = Field(description="发生地点", default=None)
    what: Optional[List[Optional[str]]] = Field(description="主要事件", default=None)
    why: Optional[List[Optional[str]]] = Field(description="原因", default=None)
    how: Optional[List[Optional[str]]] = Field(description="过程", default=None)
    
    def serialize_for_llm(self) -> Dict[str, Any]:
        """将 BasicMetadata 序列化为 LLM 友好的字典格式"""
        return {
            "新闻类型": self.news_type,
            "人物": self.who,
            "时间": self.when,
            "地点": self.where,
            "事件": self.what,
            "原因": self.why,
            "过程": self.how,
        }


class Knowledge(BaseModel):
    term: str = Field(description="知识元素的名称或术语")
    category: str = Field(description="知识元的类别")
    description: Optional[str] = Field(
        description="检索到的知识元的简要定义或解释，如果无法检索到明确的定义，请输出'无'", 
        default=None
    )
    source: Optional[str] = Field(description="知识元定义的来源链接", default=None)
    
    def serialize(self) -> Dict[str, Any]:
        """将 Knowledge 序列化为 LLM 友好的字典格式"""
        return {
            "名称": self.term,
            "类别": self.category,
            "定义": self.description,
            "来源": self.source
        }


class Knowledges(BaseModel):
    items: List[Knowledge] = Field(description="新闻文本中的知识元", default_factory=list)


class MetadataState(BaseModel):
    news_text: str = Field(description="待分析的新闻文本")
    basic_metadata: Optional[BasicMetadata] = Field(default=None)
    knowledges: List[Knowledge] = Field(description="新闻文本中的知识元", default_factory=list)
    retrieved_knowledges: Annotated[List[Knowledge], operator.add] = Field(description="检索完成后的知识元", default_factory=list)
    
    def serialize_retrieved_knowledges_for_llm(self) -> List[Dict[str, Any]]:
        """将检索完成的知识元列表序列化为 LLM 友好的字典列表"""
        return [knowledge.serialize() for knowledge in self.retrieved_knowledges]
    
