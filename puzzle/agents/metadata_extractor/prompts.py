from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from .states import Knowledges
from utils import SafeParse

# Define metadata extractor model role and ability
METADATA_EXTRACTOR_SYSTEM_PROMPT = SystemMessage(
    """
You are a professional news analyst. Your tasks are:

1. Identify the type of news.
2. Extract the six key elements of the news (5W1H: Who, What, When, Where, Why, How).
3. Extract the knowledge items (key factual units from the text).

Requirements:
- Remain objective and accurate.
- Do not add any information that is not explicitly stated in the original text.
"""
)

# basic metadata prompts
basic_metadata_extractor_prompt_template_string = """
Please analyze the following news text and extract its basic metadata:

1. News Type:
   - Political News: government, policies, elections, international relations, etc.
   - Economic News: economic development, financial markets, corporate dynamics, trade, etc.
   - Social News: social phenomena, livelihood, education, culture, etc.
   - Technology News: scientific discoveries, technological innovation, digital products, etc.
   - Sports News: sports events, athletes, sports industry, etc.
   - Entertainment News: film, television, music, celebrities, etc.
   - Environmental News: climate change, environmental protection, natural disasters, etc.
   - Health News: healthcare, diseases, healthy living, etc.
   - Other: if none of the above categories fit, specify the exact type.

2. Six Key Elements of the News (5W1H) [! Note: Each element may have multiple values]:
   - Who: the main people or organizations involved
   - When: the time of the event, including date, time, or period
   - Where: the location of the event, which may include country, city, or specific place
   - What: what happened, the event or action
   - Why: the cause, motivation, or background of the event
   - How: how the event happened or was carried out, including means, methods, or processes

<news_text>
{news_text}
</news_text>
"""
basic_metadata_extractor_prompt_template = ChatPromptTemplate.from_messages(
    [
        METADATA_EXTRACTOR_SYSTEM_PROMPT,
        HumanMessagePromptTemplate.from_template(
            template=basic_metadata_extractor_prompt_template_string,
        ),
    ]
)

# knowledge prompts
knowledge_extraction_output_parser = SafeParse(PydanticOutputParser(pydantic_object=Knowledges))
knowledge_extraction_prompt_template_string = """
# Role
Name: Professional Knowledge-Element Extraction Expert  
Main Task: From the input news text, identify professional terms and concepts that can provide additional background information for fact-checking.

# Definition of Knowledge Elements
A knowledge element refers to a static, well-established concept, term, or historical event that requires specific domain knowledge to fully understand. They usually:
1. Possess professional or academic value  
2. Have relatively stable definitions  
3. Have clear explanations in their respective fields  
4. Require specific background knowledge for full comprehension  

# Content That Should NOT Be Considered Knowledge Elements
1. Common everyday words and phrases likely to appear in daily conversation  
2. Specific people mentioned in the news (e.g., "Zhang San", "President Biden")  
3. Specific locations in the news event (e.g., "Haidian District, Beijing")  
4. Specific events described in the news (e.g., "yesterday’s press conference")  
5. Organizations or institutions (e.g., "a company", "a university")  
6. Emotional words or subjective evaluations  
7. Ordinary nouns that can be easily understood without special background knowledge  

# Extraction Criteria
- Extract only terms that truly require professional background knowledge to understand.  
- Ask: "Would an average reader need additional explanation to understand this concept?"  
- If a word is used only as a common word in context rather than a professional concept, do not extract it.  

You only need to extract the **term name** and its **category**; definitions will be determined in later retrieval.  

Please extract knowledge elements from the following text:  
<news_text>  
{news_text}  
</news_text>
"""
knowledge_extraction_prompt_template = ChatPromptTemplate.from_messages(
    [
        HumanMessagePromptTemplate.from_template(
            template=knowledge_extraction_prompt_template_string,
        )
    ]
)

knowledge_retrieve_prompt = f"""
You are a multilingual knowledge retrieval expert. The user will provide a knowledge element. 
Your task is to search Wikipedia to find the definition of that knowledge element.

# Retrieval Requirements
- If the retrieved Wikipedia entry is a synonym of the knowledge element, explain the synonym relationship in the `description` field.
- If the knowledge element cannot be matched precisely, try:
  - Changing the search language
  - Translating the knowledge element into other languages
  - Using alternative search strategies
- Once the definition of the knowledge element is confirmed, output the explanation in the `description` field **using the original language of the knowledge element provided by the user**.

# Output
Return the knowledge element’s definition with the explanation in the same language as the user’s input.
"""
