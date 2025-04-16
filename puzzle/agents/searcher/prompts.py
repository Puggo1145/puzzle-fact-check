from .states import Status, SearchResult
from langchain_core.prompts import HumanMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from utils import SafeParse
from tools import get_current_time
from knowledge.retrieve import search_engine_advanced_query_usage
from knowledge.source import source_evaluation_prompt

current_time = get_current_time.invoke({"timezone": "UTC"})

evaluate_current_status_output_parser = SafeParse(parser=PydanticOutputParser(pydantic_object=Status))
search_method_prompt_template = HumanMessagePromptTemplate.from_template(
    """
现在时间是：{current_time}

你正在对一则新闻进行事实核查，请使用工具，对你被分配到的核查点进行核查

# 新闻元数据：
确保找到的证据和新闻元数据保持高度一致：
{basic_metadata}

# 核查点：
{content}

# 核查目标：
{purpose}

# 期望目标信源类型：
{expected_source}

# 可用工具：
{tools_schema}

# 任务：
1. 对比核查目标和检索到的信息，提取出能够支持核查目标的证据和缺失的信息
 - 如果检索结果存在能够支持或反对核查目标的部分重要证据，将其更新到 new_evidence 中
 - 如果检索结果存在缺失的证据或逻辑关系，将其更新在 missing_information 中，并作为下一次检索的子目标
2. 如果检索到的信息足以支撑核查目标，停止检索，开始回答
3. 如果检索到的信息不能充分满足核查目标，继续检索

# 检索策略：
以下策略有助于提高你的检索效率
1. 使用高级检索词
当你需要聚焦特点类型的信息时，使用高级检索词构造检索关键词
{search_engine_advanced_query_usage}

2. 多语言检索：
- 使用英语检索可以获得更广泛和高质量的信息
- 使用核查目标的地方语言构造检索关键词，提高找到原始信息的可能性
    
3. 社交网络检索
- 部分新闻的主体会在社交网络上发布信息，其本人/本账号发布信息的原文可以被作为一手资料
- 如果要使用搜索引擎搜索社交网络信息，使用 site 高级检索词让结果限定在目标社交网络中
- 如果确定主体社交网络链接，可以直接尝试阅读网页

4. 证据信源的标准
{source_evaluation_prompt}

# 限制：
1. 你目前无法阅读视频、图片、音频等非文本信息，只能阅读文本信息
2. 禁止重复提取已存在的证据。确保你提取的是新的、不同的证据！

# 响应格式：
{format_instructions}
""",
    partial_variables={
        "current_time": current_time,
        "format_instructions": evaluate_current_status_output_parser.get_format_instructions(),
        "search_engine_advanced_query_usage": search_engine_advanced_query_usage,
        "source_evaluation_prompt": source_evaluation_prompt,
    },
)

evaluate_current_status_prompt_template = HumanMessagePromptTemplate.from_template(
    template="""
# 检索历史记录：
{statuses}

# 上一次工具调用结果：
{retrieved_information}

# 重要证据：
这是在先前的检索过程中摘取的重要证据：
{evidences}
"""
)

generate_answer_output_parser = SafeParse(parser=PydanticOutputParser(pydantic_object=SearchResult))
generate_answer_prompt_template = HumanMessagePromptTemplate.from_template(
    template="""
现在时间是：{current_time}

你正在对一则新闻进行事实核查，你已经对其中一个核查点进行了事实核查，现在需要基于检索到的信息，给出核查结论。

# 新闻元数据：
{basic_metadata}

# 核查点：
{content}

# 核查目标：
{purpose}

# 期望目标信源类型：
{expected_source}

# 你的检索历史记录：
{statuses}

# 你在检索过程中收集到的重要证据片段：
{evidences}

# 任务：
- 请提供一个全面、充分的核查结论
- 充分利用收集到的证据片段，确保你的结论有坚实的事实基础

# 响应格式：
{format_instructions}
""",
    partial_variables={
        "format_instructions": generate_answer_output_parser.get_format_instructions(),
        "current_time": current_time,
    },
)
