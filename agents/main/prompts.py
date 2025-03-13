from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import HumanMessagePromptTemplate
from .states import CheckPoints, RetrievalResultVerifications
from typing import List

fact_check_plan_output_parser = JsonOutputParser(pydantic_object=CheckPoints)

# 根据 DeepSeek 官方说法，不建议使用 SystemPrompt，这可能会限制模型的推理表现，这里替换为常规的 HumanMessage
fact_check_plan_prompt_template = HumanMessagePromptTemplate.from_template(
    template="""
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
   - 说明每个检索步骤的目的（请详细描述，至少 50 个字符）
   - 建议合适的信息来源类型

新闻文本：
{news_text}

{format_instructions}
""",
    partial_variables={
        "format_instructions": fact_check_plan_output_parser.get_format_instructions()
    },
)

human_feedback_prompt_template = HumanMessagePromptTemplate.from_template("""
用户对你给出的核查方案提出了反馈，请你基于用户的反馈修改：
{human_feedback}
"""
)

evaluate_search_result_output_parser = JsonOutputParser(pydantic_object=RetrievalResultVerifications)
evaluate_search_result_prompt_template = HumanMessagePromptTemplate.from_template("""
你是一名专业的新闻事实核查员，你的任务是对下面的新闻文本进行事实核查：
{news_text}

你先前已经基于该新闻文本给出了一个核查方案，search agent 根据你的检索方案执行了检索，并给出了以下检索结果：
{check_points}

# 任务
 - 仔细复核每个核查点检索步骤的结论，检查证据是否充分，结论与推理是否一致
 - 在每个核查点下的检索步骤中，对 search agent 的核查结论进行推理，并给出是否认可其核查结论

# 输出格式
{format_instructions}
""",
    partial_variables={
        "format_instructions": evaluate_search_result_output_parser.get_format_instructions()
    },
)

write_fact_checking_report_prompt_template = HumanMessagePromptTemplate.from_template("""
你是一名专业的新闻事实核查员，你的任务是对下面的新闻文本进行事实核查并撰写正式报告：
{news_text}

你先前已经基于该新闻文本给出了一个核查方案，main agent 根据你的检索方案执行了检索，且你已经对所有检索结果进行了复核：
{check_points}

# 任务
请你根据你的核查方案、search agent 的检索结果和你的复核结论，撰写一份专业的事实核查报告。

## 报告结构要求
1. **报告摘要**：简要概述核查的新闻内容和总体核查结论
2. **核查方法说明**：简述你采用的核查方法和信息来源
3. **核查发现**：
   - 按照核查点逐一展示核查结果
   - 每个核查点需包含：原始陈述、核查证据、推理过程和核查结论
   - 清晰标注每个陈述的真实性评级（如：完全真实、部分真实、缺乏上下文、误导性、虚假等）
4. **总体评估**：对新闻整体真实性的综合评价
5. **建议**：针对读者如何理解该新闻的建议（如适用）

## 质量要求
- 确保核查结果有充分证据支持，引用具体来源
- 保持客观中立，避免政治倾向或个人观点
- 确保逻辑推理过程清晰、完整，从证据到结论的推导合理
- 使用精确的语言，避免模糊表述
- 区分事实与观点，明确指出新闻中的主观评价部分
- 当证据不足或有矛盾时，诚实说明局限性

请以专业、权威的语气撰写报告，使读者能清晰理解每个核查点的真实性及其依据。
""")
