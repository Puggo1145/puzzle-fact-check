from typing import Optional, List, Annotated, Dict, Any
from pydantic import BaseModel, Field, model_validator
import operator

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


class MetadataState(BaseModel):
    news_text: str = Field(description="待分析的新闻文本")
    basic_metadata: Optional[BasicMetadata] = Field(default=None)
    knowledges: List[Knowledge] = Field(description="新闻文本中的知识元", default_factory=list)
    
    @model_validator(mode='before')
    @classmethod
    def merge_knowledges(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """合并新传入的知识和已有的知识"""
        if not isinstance(data, dict):
            return data
            
        # 如果有新的知识元素要添加
        if 'knowledges' in data and isinstance(data['knowledges'], list):
            new_knowledges = data['knowledges']
            
            # 获取当前状态中已有的知识元素
            current_state = data.get('__langgraph_state__', {})
            current_knowledges = current_state.get('knowledges', []) if isinstance(current_state, dict) else []
            
            # 创建一个字典来存储已有的知识元素，以term为键
            knowledge_dict = {k.term if isinstance(k, Knowledge) else k.get('term'): k 
                             for k in current_knowledges if k}
            
            # 合并新的知识元素，如果term相同则更新
            for k in new_knowledges:
                if not k:
                    continue
                    
                term = k.term if isinstance(k, Knowledge) else k.get('term')
                if term in knowledge_dict:
                    # 如果新知识有description或source而旧知识没有，则更新
                    old_k = knowledge_dict[term]
                    if isinstance(k, dict) and isinstance(old_k, dict):
                        if k.get('description') and not old_k.get('description'):
                            old_k['description'] = k['description']
                        if k.get('source') and not old_k.get('source'):
                            old_k['source'] = k['source']
                    elif isinstance(k, Knowledge) and isinstance(old_k, Knowledge):
                        if k.description and not old_k.description:
                            old_k.description = k.description
                        if k.source and not old_k.source:
                            old_k.source = k.source
                    elif isinstance(k, dict) and isinstance(old_k, Knowledge):
                        if k.get('description') and not old_k.description:
                            old_k.description = k['description']
                        if k.get('source') and not old_k.source:
                            old_k.source = k['source']
                    elif isinstance(k, Knowledge) and isinstance(old_k, dict):
                        if k.description and not old_k.get('description'):
                            old_k['description'] = k.description
                        if k.source and not old_k.get('source'):
                            old_k['source'] = k.source
                else:
                    # 如果是新的知识元素，则添加
                    knowledge_dict[term] = k
            
            # 更新知识元素列表
            data['knowledges'] = list(knowledge_dict.values())
            
        return data
    