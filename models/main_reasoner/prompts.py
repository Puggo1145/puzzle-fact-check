# Main Reasoner Model Prompts
from typing import List, Optional
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser


# Retrieval step definition
class RetrievalStep(BaseModel):
    purpose: str = Field(description="该检索步骤的目的，想要获取什么信息")
    expected_sources: Optional[List[str]] = Field(
        description="期望找到的信息来源类型，如官方网站、新闻报道、学术论文等",
        default=None,
    )


# Unified statement and verification point structure
class StatementAnalysis(BaseModel):
    id: int = Field(description="陈述 id")
    content: str = Field(description="从新闻中提取的事实陈述")
    is_verification_point: bool = Field(description="该陈述是否被选为核查点")
    importance: Optional[str] = Field(
        description="若被选为核查点，说明其重要性", default=None
    )
    retrieval_plan: Optional[List[RetrievalStep]] = Field(
        description="若被选为核查点，提供检索方案", default=None
    )


class FactCheckPlanResult(BaseModel):
    statements: List[StatementAnalysis] = Field(
        description="新闻中提取的所有陈述分析结果"
    )


fact_check_plan_output_parser = JsonOutputParser(pydantic_object=FactCheckPlanResult)

# 根据 DeepSeek 官方说法，不建议使用 SystemPrompt，这可能会限制模型的推理表现，这里替换为常规的 HumanMessage
fact_check_plan_prompt_template_string = """
你是一名专业的新闻事实核查员，你现在需要对给定的一段新闻文本进行核查前的思考和规划：
1. 陈述提取：从新闻文本中精确客观的陈述
2. 核查点评估：评估每个陈述的价值，决定哪些陈述值得作为核查点深入验证
3. 检索规划：为选定的核查点设计详细的互联网检索方案，确保检索结果能有效验证核查点真实性
你稍后会获取这些核查点的检索结果，并根据检索结果进一步推理
请对给定的新闻文本进行全面分析，完成以下任务：

1. 提取新闻中的所有客观事实陈述，这些陈述应该：
   - 只包含事实，不含主观评价或观点
   - 含有具体、可验证的信息
   - 清晰、简洁、独立，每个陈述只聚焦一个可核查的事实

2. 评估每个陈述，决定哪些值得作为核查点深入验证：
   - 考虑陈述的重要性、时效性、接近性和显著性
   - 判断该陈述是否可能影响新闻整体真实性的评估

3. 为每个选定的核查点设计详细的检索方案：
   - 提供具体的检索查询词
   - 说明每个检索步骤的目的
   - 建议合适的信息来源类型

新闻文本：
{news_text}

{format_instructions}
"""

fact_check_plan_prompt_template = ChatPromptTemplate.from_template(
    template=fact_check_plan_prompt_template_string,
    partial_variables={
        "format_instructions": fact_check_plan_output_parser.get_format_instructions()
    },
)
