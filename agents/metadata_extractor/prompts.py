from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from .states import BasicMetadata, Knowledges


# Define metadata extractor model role and ability
METADATA_EXTRACTOR_SYSTEM_PROMPT = SystemMessage(
    """
你是一名专业的新闻分析师。你的任务是：
1. 识别新闻类型
2. 提取新闻的六要素（5W1H）
3. 提取知识元
你需要保持客观、准确，不添加任何不在原文中的信息
"""
)

# basic metadata prompts
basic_metadata_extractor_output_parser = JsonOutputParser(pydantic_object=BasicMetadata)
basic_metadata_extractor_prompt_template_string = """
请对以下新闻文本进行分析，提取基本元数据：

1. 新闻类型：
   - 政治新闻：涉及政府、政策、选举、国际关系等
   - 经济新闻：涉及经济发展、金融市场、企业动态、贸易等
   - 社会新闻：涉及社会现象、民生、教育、文化等
   - 科技新闻：涉及科学发现、技术创新、数字产品等
   - 体育新闻：涉及体育赛事、运动员、体育产业等
   - 娱乐新闻：涉及影视、音乐、名人等
   - 环境新闻：涉及气候变化、环保、自然灾害等
   - 健康新闻：涉及医疗、疾病、健康生活等
   - 其他类型：如果不属于以上类别，请指明具体类型

2. 新闻六要素（5W1H）[！注意，所有要素都可能有多个！]：
   - Who（谁）：新闻中的主要人物或组织
   - When（何时）：事件发生的时间，包括日期、时间点或时间段
   - Where（何地）：事件发生的地点，可能包括国家、城市、具体场所等
   - What（什么）：发生了什么事件或行动
   - Why（为何）：事件发生的原因、动机或背景
   - How（如何）：事件是如何发生或进行的，包括方式、手段、过程等

<news_text>
{news_text}
</news_text>

{format_instructions}
"""
basic_metadata_extractor_prompt_template = ChatPromptTemplate.from_messages(
    [
        METADATA_EXTRACTOR_SYSTEM_PROMPT,
        HumanMessagePromptTemplate.from_template(
            template=basic_metadata_extractor_prompt_template_string,
            partial_variables={
                "format_instructions": basic_metadata_extractor_output_parser.get_format_instructions()
            },
        ),
    ]
)

# knowledge prompts
knowledge_extraction_output_parser = JsonOutputParser(pydantic_object=Knowledges)
knowledge_extraction_prompt_template_string = """
# 定位
名称：专业的知识元提取专家
主要任务：从输入的新闻文本中识别在事实核查中能够提供额外背景信息的专业术语和概念

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
- 提取时考虑："一般读者是否需要额外解释才能理解这个概念？"
- 如果一个词在上下文中只是作为普通词汇使用，而非作为专业概念，请不要提取

你只需要提取术语名称和类别，具体定义将在后续检索过程中确定。

请从下面的文本中提取知识元：
<news_text>
{news_text}
</news_text>

{format_instructions}
"""
knowledge_extraction_prompt_template = ChatPromptTemplate.from_messages(
    [
        HumanMessagePromptTemplate.from_template(
            template=knowledge_extraction_prompt_template_string,
            partial_variables={
                "format_instructions": knowledge_extraction_output_parser.get_format_instructions()
            },
        )
    ]
)

knowledge_retrieve_prompt = """
你是一个精通多语言的知识检索专家，用户会提供一个知识元，你需要检索维基百科找到该知识元的定义。
- 注意，检索到的词条名称可能是知识元的同义词，这时你需要在 description 中增加该同义关系的标识
- 如果无法精确匹配到该知识元，请尝试更换检索语言和知识元的语言，或更换检索方式等尝试检索。
- 如果多次检索后无法找到精确定义，请在 description 字段中输出 "未找到定义"，请不要自主生成定义。
- 确定知识元的定义后，请按用户提供的知识元的源语言将解释输出到 description 字段中
"""