import operator
from typing import Optional, List, Annotated, Dict, Any
from pydantic import BaseModel, Field

class BasicMetadata(BaseModel):
    news_type: str = Field(description="News type")
    who: Optional[List[Optional[str]]] = Field(description="The main subjects in the news", default=None)
    when: Optional[List[Optional[str]]] = Field(description="The time of the event", default=None)
    where: Optional[List[Optional[str]]] = Field(description="The location of the event", default=None)
    what: Optional[List[Optional[str]]] = Field(description="The main event", default=None)
    why: Optional[List[Optional[str]]] = Field(description="The reason", default=None)
    how: Optional[List[Optional[str]]] = Field(description="The process", default=None)
    
    def serialize_for_llm(self) -> Dict[str, Any]:
        """将 BasicMetadata 序列化为 LLM 友好的字典格式"""
        return {
            "News type": self.news_type,
            "Who": self.who,
            "When": self.when,
            "Where": self.where,
            "What": self.what,
            "Why": self.why,
            "How": self.how,
        }


class Knowledge(BaseModel):
    term: str = Field(description="The name or term of the knowledge element")
    category: str = Field(description="The category of the knowledge element")
    description: Optional[str] = Field(
        description="The brief definition or explanation of the retrieved knowledge element, if the definition cannot be retrieved, please output 'None'", 
        default=None
    )
    source: Optional[str] = Field(description="The source link of the knowledge element definition", default=None)
    
    def serialize(self) -> Dict[str, Any]:
        """将 Knowledge 序列化为 LLM 友好的字典格式"""
        return {
            "Name": self.term,
            "Category": self.category,
            "Definition": self.description,
            "Source": self.source
        }


class Knowledges(BaseModel):
    items: List[Knowledge] = Field(description="The knowledge elements in the news text", default_factory=list)


class MetadataState(BaseModel):
    news_text: str = Field(description="The news text to be analyzed")
    basic_metadata: Optional[BasicMetadata] = Field(default=None)
    knowledges: List[Knowledge] = Field(description="The knowledge elements in the news text", default_factory=list)
    retrieved_knowledges: Annotated[List[Knowledge], operator.add] = Field(description="The knowledge elements after retrieval", default_factory=list)
    
    def serialize_retrieved_knowledges_for_llm(self) -> List[Dict[str, Any]]:
        """将检索完成的知识元列表序列化为 LLM 友好的字典列表"""
        return [knowledge.serialize() for knowledge in self.retrieved_knowledges]
    
