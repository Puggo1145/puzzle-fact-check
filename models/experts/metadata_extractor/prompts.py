# Metadata Extractor Model Prompts
from typing import List, Optional
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser


# Define metadata extractor model role and ability
METADATA_EXTRACTOR_SYSTEM_PROMPT = SystemMessage(content=
    """
你是一名专业的新闻分析师。你的任务是分析新闻文本，识别新闻类型并提取新闻的六要素（5W1H）。
你需要客观、准确地分析，不添加任何不在原文中的信息。
"""
)


# News metadata structure
class NewsMetadata(BaseModel):
    news_type: str = Field(description="新闻类型，如政治新闻、经济新闻、社会新闻、科技新闻、体育新闻等")
    who: Optional[List[str]] = Field(description="新闻中的主要人物或组织", default=None)
    what: Optional[List[str]] = Field(description="新闻中发生的主要事件或行动", default=None)
    when: Optional[List[str]] = Field(description="事件发生的时间", default=None)
    where: Optional[List[str]] = Field(description="事件发生的地点", default=None)
    why: Optional[List[str]] = Field(description="事件发生的原因或背景", default=None)
    how: Optional[List[str]] = Field(description="事件发生的方式或过程", default=None)


metadata_extractor_parser = JsonOutputParser(pydantic_object=NewsMetadata)

metadata_extractor_template = """
请对以下新闻文本进行分析，提取关键元数据：

1. 确定新闻类型：
   - 政治新闻：涉及政府、政策、选举、国际关系等
   - 经济新闻：涉及经济发展、金融市场、企业动态、贸易等
   - 社会新闻：涉及社会现象、民生、教育、文化等
   - 科技新闻：涉及科学发现、技术创新、数字产品等
   - 体育新闻：涉及体育赛事、运动员、体育产业等
   - 娱乐新闻：涉及影视、音乐、名人等
   - 环境新闻：涉及气候变化、环保、自然灾害等
   - 健康新闻：涉及医疗、疾病、健康生活等
   - 其他类型：如果不属于以上类别，请指明具体类型

2. 提取新闻六要素（5W1H）：
   - Who（谁）：新闻中的主要人物或组织，可能有多个
   - What（什么）：发生了什么事件或行动，可能有多个关键事件
   - When（何时）：事件发生的时间，包括日期、时间点或时间段
   - Where（何地）：事件发生的地点，可能包括国家、城市、具体场所等
   - Why（为何）：事件发生的原因、动机或背景
   - How（如何）：事件是如何发生或进行的，包括方式、手段、过程等

请确保你的分析基于新闻文本中明确提及的信息，不要添加推测或不在文本中的内容。对于文本中未明确提及的要素，可以标记为空列表。

新闻文本：
{news_text}

{format_instructions}
"""

metadata_extractor_prompt = ChatPromptTemplate.from_messages([
    METADATA_EXTRACTOR_SYSTEM_PROMPT,
    HumanMessagePromptTemplate.from_template(
        template=metadata_extractor_template,
        partial_variables={
            "format_instructions": metadata_extractor_parser.get_format_instructions()
        }
    )
]) 