from .states import Status, SearchAgentResult
from langchain_core.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.output_parsers import JsonOutputParser

system_prompt_template = SystemMessagePromptTemplate.from_template(
    """
你正在执行一个新闻事实核查任务，你被分配到一个核查点，你需要检索互联网，检验核查点的真实性

你正在核查的新闻的类型和六要素有：
<metadata>
{news_metadata}
</metadata>
你要确保核查证据和这些新闻要素高度保持高度一致：

你的核查点是：
<Content>
{content}
</Content>

你的核查目标是：
<Purpose>
{purpose}
</Purpose>

尝试寻找这些类型的证据，其有助于验证核查点的真实性：
<Expected Results>
{expected_results}
</Expected Results>

<Task>
1. 使用工具检索信息
2. 推理和评估检索到的信息能否支撑给定的陈述，并规划下一步操作
3. 如果你找到了足以支持核查目标的证据，请停止检索，开始生成回答
</Task>

在检索时，请遵守以下策略！！！
<Strategies>
1. 多语言检索：
    - 尝试使用核查目标的当地语言构造检索关键词，提高找到原始信息的可能性
    - 不要只使用一种语言检索，尝试多语言检索以获得更多信息角度
    - 如果检索后没有获得理想的结果，尝试更换语言进行检索！！！
2. 避免重复检索：如果连续 3 次使用相同的检索方法但没有获得新信息，请尝试:
    - 更换搜索引擎
    - 修改搜索关键词
    - 尝试阅读已找到的网页
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
请根据[检索到的结果]和[检索操作的历史记录]进行推理和自我评估，判断是否满足目标，并规划下一步操作
注意，每一次操作都必须只专注于一个目标！

回答时机：
- 如果你已经找到足够的信息能够支撑核查目标和预期，请直接生成回答。

上一次工具调用的结果：
<Retrieved information>
{retrieved_information}
</Retrieved information>

检索操作的历史记录：
<statuses>
{statuses}
<statuses>

如果你发现了能够支持核查目标的重要证据，请按照格式提取这些证据的原文。
注意：不要重复提取已经收集过的证据。仔细查看 "supporting_evidence"，确保你提取的是新的、与之前不同的证据。
这是你在先前的检索过程中所摘取的，能够支撑核查目标的证据：
<supporting_evidence>
{supporting_evidence}
</supporting_evidence>


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
现在你已经收集了足够的信息，请基于所有检索到的信息，给出该核查点的核查结论。

以下是你最后一次工具调用获取的所有信息：
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

请提供一个全面的总结，明确的结论，支持你结论的信息来源，以及你对结论的置信度评估
在回答中，请充分利用收集到的证据片段，确保你的结论有坚实的事实基础

{format_instructions}
""",
    partial_variables={
        "format_instructions": generate_answer_output_parser.get_format_instructions()
    },
)
