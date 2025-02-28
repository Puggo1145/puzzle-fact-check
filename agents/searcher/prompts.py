from .states import Status
from langchain_core.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.output_parsers import JsonOutputParser

system_prompt_template = SystemMessagePromptTemplate.from_template(
    """
你是一名专业的新闻事实核查专家，有丰富的新闻行业经验。

你正在对这条新闻陈述进行事实核查：
<Content>
{content}
</Content>

你的目标是：
<Purpose>
{purpose}
</Purpose>

期望能够用于核查该陈述的来源类型
<Expected Results>
{expected_results}
</Expected Results>

<Task>
1. 使用给定工具检索信息
2. 推理和评估检索到的信息能否支撑给定的陈述
3. 基于评估结果继续迭代或给出核查结论
</Task>
"""
)

evaluate_current_status_output_parser = JsonOutputParser(pydantic_object=Status)

evaluate_current_status_prompt_template = HumanMessagePromptTemplate.from_template(
    template="""
评估检索到的信息和已执行的检索操作是否充分满足目标和预期，并规划下一步操作

<Retrieved information>
{retrieved_information}
</Retrieved information>

<statuses>
{statuses}
<statuses>

<format>
{format_instructions}
</format>
""",
    partial_variables={
        "format_instructions": evaluate_current_status_output_parser.get_format_instructions()
    },
)
