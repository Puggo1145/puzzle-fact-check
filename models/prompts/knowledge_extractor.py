from typing import List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import JsonOutputParser


# 定义知识元素的数据模型，只保留 term 和 category
class KnowledgeElement(BaseModel):
    term: str = Field(description="知识元素的名称或术语")
    category: str = Field(description="知识元素的类别，如'专业术语'、'历史事件'、'科学概念'等")


class KnowledgeElements(BaseModel):
    elements: List[KnowledgeElement] = Field(description="从文本中提取的静态知识元素列表")


# 创建输出解析器
knowledge_extraction_parser = JsonOutputParser(pydantic_object=KnowledgeElements)

# 系统提示词
KNOWLEDGE_EXTRACTOR_SYSTEM_PROMPT = SystemMessage(content="""
你是一个专业的知识元提取专家，你的任务是从新闻文本中识别可能需要在事实核查过程中提供额外背景信息的专业术语和概念。

知识元是指那些静态的、已确立的概念、术语或历史事件，它们通常具有固定含义和相对稳定的定义。例如"冷战"、"治外法权"、"量子力学"、"DNA"、"次贷危机"等。

知识元不包括动态信息，例如：
- 新闻中提到的特定人物（如"张三"、"拜登总统"）
- 新闻事件中的具体地点（如"北京市海淀区"）
- 新闻中描述的具体事件（如"昨天的记者会"）
- 组织机构（如"某公司"、"某大学"）

你只需要提取术语名称和类别，具体定义将在后续检索过程中确定。
"""
)

# 人类提示词模板
knowledge_extraction_template = """
请从以下新闻文本中提取可能需要额外背景知识的静态知识元素，这些元素应该是：
文本内容：
{text}

{format_instructions}
"""

# 创建完整的提示词
knowledge_extraction_prompt = ChatPromptTemplate.from_messages([
    KNOWLEDGE_EXTRACTOR_SYSTEM_PROMPT,
    HumanMessagePromptTemplate.from_template(
        template=knowledge_extraction_template,
        partial_variables={
            "format_instructions": knowledge_extraction_parser.get_format_instructions()
        }
    )
]) 