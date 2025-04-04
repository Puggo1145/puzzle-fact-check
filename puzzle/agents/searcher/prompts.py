from .states import Status, SearchResult
from langchain_core.prompts import HumanMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from utils import SafeParse
from tools import get_current_time

current_time = get_current_time.invoke({"timezone": "UTC"})

evaluate_current_status_output_parser = SafeParse(parser=PydanticOutputParser(pydantic_object=Status))
search_method_prompt_template = HumanMessagePromptTemplate.from_template(
    """
现在时间是：{current_time}

你正在对一则新闻进行事实核查，你被分配到一个核查点，请检索互联网，对核查点进行事实核查

# 新闻元数据：
确保找到的证据和新闻元数据保持高度一致：
{basic_metadata}

# 核查点：
{content}

# 核查目标：
{purpose}

# 期望目标信源类型：
尝试寻找这些类型的证据，其有助于验证核查点的真实性
{expected_sources}

# 可用工具：
{tools_schema}

# 任务：
1. 评估与推理：对比核查目标和检索到的信息，提取出能够支持核查目标的证据和缺失的信息
 - 如果检索结果存在能够支持或反对核查目标的部分重要证据，将其更新到 new_evidence 中
 - 如果检索结果存在缺失的证据或逻辑关系，将其更新在 missing_information 中，并作为下一次检索的子目标
2. 如果检索到的信息足以支撑核查目标，请停止检索，开始生成回答
3. 如果检索到的信息不能充分满足核查目标，继续检索

# 检索策略：
遵循以下策略有助于提高你的检索效率
1. 多语言检索（扩展检索的广度）：
    - 不要只使用一种语言检索，使用多语言检索以获得更多信息角度
    - 尝试使用核查目标的当地语言构造检索关键词，提高找到原始信息的可能性
2. 高级检索词（提高检索的准度）：
    [注意：仅在必要时选用高级检索词，过度使用可能会影响搜索结果的广度，一般情况下构造普通关键词即可]
    - “site:”: 搜索某个特定网站的内容
    - “fileType:”：搜索特定文件类型
    - 关键词加双引号：搜索引擎会返回和关键词完全一致的搜索结果。在搜索英文人名、地点、引语、歌词、文学作品等比较确定的关键词时比较有用
    - “-”：在搜索中排除词汇。例如使用 “NBA 球星 - 詹姆斯”，搜索结果将不包含詹姆斯
    - “*”：如果不确定要搜索的关键词或者问题，使用通配符，google 会用一系列相关的词汇来替换符号 
    - “OR”：如果希望搜索结果包含两个或多个关键词中的任意一个，使用关键字 OR（OR 必须大写）
    - “..”：搜索数字范围。例如搜索 2000 年到 2022 年之间的诺贝尔奖得主的名单，使用 "nobel prizewinners" 2000..2022
    - “intitle:”：限定在网页标题中搜索网站信息（intitle: 和后面的关键词之间不能出现空格）
    - “related:”：搜索与某个特定网站相关的其他网站
    - “inurl:”：限定关键词必须出现在网站的 url 链接中

# 限制条件：
1. 在输出工具调用信息时，你只能使用 JSON 的合法字符！
2. 禁止重复检索：如果连续 2 次使用相同的检索方法和 query 都没有获得新信息，请尝试:
 - 更换搜索引擎
 - 修改搜索关键词
 - 尝试阅读已找到的网页
3. 如果检索后没有获得理想的结果，尝试更换语言检索
4. 禁止重复提取已存在的证据。确保你提取的是新的、不同的证据！

# 响应格式：
{format_instructions}
""",
    partial_variables={
        "current_time": current_time,
        "format_instructions": evaluate_current_status_output_parser.get_format_instructions()
    },
)


evaluate_current_status_prompt_template = HumanMessagePromptTemplate.from_template(
    template="""
以下是执行过的检索历史（检索未开始时不存在检索记录）：
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

你正在对一则新闻进行事实核查，你被分配到一个核查点，你已经对核查点进行了事实核查，现在需要基于检索到的信息，给出核查结论。

# 新闻元数据：
{basic_metadata}

# 核查点：
{content}

# 核查目标：
{purpose}

# 期望目标信源类型：
{expected_sources}

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
