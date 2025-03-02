from typing import List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import JsonOutputParser


# 定义知识元素的数据模型，只保留 term 和 category
class KnowledgeElement(BaseModel):
    term: str = Field(description="知识元素的名称或术语")
    category: str = Field(
        description="知识元的类别，如'专业术语'、'历史事件'、'科学概念'等"
    )


class KnowledgeElements(BaseModel):
    elements: List[KnowledgeElement] = Field(
        description="所有知识元"
    )


# 创建输出解析器
knowledge_extraction_parser = JsonOutputParser(pydantic_object=KnowledgeElements)

# 系统提示词
KNOWLEDGE_EXTRACTOR_SYSTEM_PROMPT = SystemMessage(
    content="""
# 定位
名称：专业的知识元提取专家
主要任务：从输入的新闻文本中识别需要在事实核查中提供额外背景信息的专业术语和概念

# 知识元的定义
知识元指需要特定领域知识才能完全理解的、静态的、已确立的概念、术语或历史事件，它们通常：
1. 具有专业性或学术价值
2. 有相对稳定的定义
3. 在相关领域有明确的解释
4. 需要特定背景知识才能完全理解

# 不应被视为知识元的内容：
1. 普通日常用语和常见词汇
2. 新闻中提到的特定人物（如"张三"、"拜登总统"）
3. 新闻事件中的具体地点（如"北京市海淀区"）
4. 新闻中描述的具体事件（如"昨天的记者会"）
5. 组织机构（如"某公司"、"某大学"）
6. 情感词汇或主观评价
7. 无需特殊背景知识即可理解的普通名词

# 提取标准
- 只提取真正需要专业背景知识理解的术语
- 对于边界情况，问自己："一般读者是否需要额外解释才能理解这个概念？"
- 如果一个词在上下文中只是作为普通词汇使用，而非作为专业概念，请不要提取

你只需要提取术语名称和类别，具体定义将在后续检索过程中确定。
"""
)

knowledge_extraction_template = """
请从以下新闻文本中提取知识元：
{text}

{format_instructions}
"""

knowledge_extraction_prompt = ChatPromptTemplate.from_messages(
    [
        KNOWLEDGE_EXTRACTOR_SYSTEM_PROMPT,
        HumanMessagePromptTemplate.from_template(
            template=knowledge_extraction_template,
            partial_variables={
                "format_instructions": knowledge_extraction_parser.get_format_instructions()
            },
        ),
    ]
)
