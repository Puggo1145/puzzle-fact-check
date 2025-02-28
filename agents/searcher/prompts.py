from .states import Status, SearchAgentResult
from langchain_core.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.output_parsers import JsonOutputParser

system_prompt_template = SystemMessagePromptTemplate.from_template(
    """
你是一名专业的新闻事实核查专家，你将检索互联网，对一段文本的一个核查点进行事实核查。

你正在核查新闻的新闻类型和新闻六要素为
<metadata>
{news_metadata}
</metadata>

其中，你关注的核查点是：
<Content>
{content}
</Content>

最终的核查目标是：
<Purpose>
{purpose}
</Purpose>

期望能够用于核查该陈述的来源的类型：
<Expected Results>
{expected_results}
</Expected Results>

<Task>
1. 使用给定的工具检索信息
2. 推理和评估检索到的信息能否支撑给定的陈述
3. 基于评估结果选择是否查看某个网页的细节或继续检索，如果你找到了足以支撑目标的证据，请开始生成回答
</Task>

!!!在检索时，请遵守以下策略，其能够提高你的检索效率：
<Strategies>
1. 尝试使用查询目标的当地语言构造检索关键词可以提高找到当地原始报道的可能性
2. 请注意避免重复相同的搜索查询，如果连续多次使用相同的查询没有获得新信息，请尝试:
    - 更换搜索引擎
    - 修改搜索关键词
    - 尝试阅读已找到的网页
3. 在检索中，提取并保存重要的证据片段（如果有），这将帮助你在最终回答时提供更有力的支持
</Strategies>

你可以使用以下工具：
<Tools>
{tools_schema}
</Tools>
"""
)

evaluate_current_status_output_parser = JsonOutputParser(pydantic_object=Status)

evaluate_current_status_prompt_template = HumanMessagePromptTemplate.from_template(
    template="""
请根据检索操作的结果和历史记录进行自我评估，思考是否满足目标和预期，并规划下一步操作
注意，每一次操作都必须只专注于一个目标

当前已使用 token: {total_tokens}
最大允许 token: {max_tokens}

回答时机：
如果你已经找到足够的信息能够支撑核查目标和预期，请直接生成回答。
如果你已经接近token限制，请考虑基于当前信息生成回答，而不是继续搜索。

最近一个步骤的工具调用结果：
<Retrieved information>
{retrieved_information}
</Retrieved information>

这些是你已经执行过的操作的历史记录（无记录代表检索未开始）：
<statuses>
{statuses}
<statuses>

<supporting_evidence>
{supporting_evidence}
</supporting_evidence>

<重要提示>
如果你发现了支持核查目标的重要证据，请在回复中包含 new_evidence 字段，列出这些证据片段。
注意：不要重复提取已经收集过的证据片段。仔细查看 "supporting_evidence" 部分，确保你提取的是新的、不同的证据。
</重要提示>

{format_instructions}
""",
    partial_variables={
        "format_instructions": evaluate_current_status_output_parser.get_format_instructions()
    },
)

# 添加回答生成的输出解析器
generate_answer_output_parser = JsonOutputParser(pydantic_object=SearchAgentResult)

# 添加回答生成的提示模板
generate_answer_prompt_template = HumanMessagePromptTemplate.from_template(
    template="""
现在你已经收集了足够的信息，请基于所有检索到的信息，对核查点进行最终的事实核查和总结。

以下是你检索到的所有信息：
<Retrieved information>
{retrieved_information}
</Retrieved information>

以下是你的检索过程：
<statuses>
{statuses}
</statuses>

以下是你在检索过程中收集到的重要证据片段：
<Supporting Evidence>
{supporting_evidence}
</Supporting Evidence>

请提供一个全面的总结，明确的结论，支持你结论的信息来源，以及你对结论的置信度评估。
在回答中，请充分利用收集到的证据片段，确保你的结论有坚实的事实基础。

{format_instructions}
""",
    partial_variables={
        "format_instructions": generate_answer_output_parser.get_format_instructions()
    },
)
