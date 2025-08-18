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
Current time: {current_time}

You are conducting a fact-check on a news story. Use the available tools to fact-check the checkpoint assigned to you.

# News Metadata
Ensure that the evidence you find is highly consistent with the following news metadata:
{basic_metadata}

# Checkpoint
{content}

# Fact-Checking Goal
{purpose}

# Expected Source Types
{expected_source}

# Available Tools
{tools_schema}

# Tasks
1) Compare the fact-checking goal with the retrieved information and extract evidence and missing information:
   - If the retrieved results contain important evidence that supports or contradicts the fact-checking goal, add it to `new_evidence`.
   - If there is missing evidence or gaps in logical connections, add them to `missing_information`, and treat them as sub-goals for the next retrieval.
2) If the retrieved information is sufficient to support the fact-checking goal, stop retrieval and begin drafting the answer.
3) If the retrieved information is insufficient to meet the fact-checking goal, continue retrieval.

# Retrieval Strategy
The following strategies may improve retrieval efficiency:

1. Use advanced search operators:  
   When you need to focus on a specific type of information, construct search queries with advanced operators.  
   {search_engine_advanced_query_usage}

2. Multilingual search:  
   - Use English queries to access a wider range and higher quality of information.  
   - Use the local language of the fact-checking goal to increase the chance of finding original information.

3. Social media search:  
   - Subjects of news may post original information on social media, and such posts can serve as primary sources.  
   - If using a search engine to find social media content, use the `site:` operator to restrict results to the target platform.  
   - If the subject’s social media link is known, directly attempt to read the webpage.

4. Standards for evaluating sources:  
   {source_evaluation_prompt}

# Constraints
1. You cannot read videos, images, or audio; you can only use text-based information.  
2. Do not duplicate previously extracted evidence. Ensure that you extract only new, distinct evidence.

# Response Format
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
# Retrieval History:
{statuses}

# Result of the Most Recent Tool Call:
{retrieved_information}

# Key Evidence:
These are key evidence snippets extracted during prior retrieval steps:
{evidences}
"""
)

generate_answer_output_parser = SafeParse(parser=PydanticOutputParser(pydantic_object=SearchResult))
generate_answer_prompt_template = HumanMessagePromptTemplate.from_template(
    template="""
Current time: {current_time}

You are conducting a fact-check on a news story. You have already verified one checkpoint. Now, based on the retrieved information, you must provide a fact-checking conclusion.

# News Metadata
{basic_metadata}

# Checkpoint
{content}

# Fact-Checking Goal
{purpose}

# Expected Source Types
{expected_source}

# Your Retrieval History
{statuses}

# Important Evidence Snippets Collected During Retrieval
{evidences}

# Tasks
- Provide a comprehensive and well-substantiated fact-checking conclusion.
- Make full use of the collected evidence snippets to ensure your conclusion rests on a solid factual basis.

# Response Format
{format_instructions}
""",
    partial_variables={
        "format_instructions": generate_answer_output_parser.get_format_instructions(),
        "current_time": current_time,
    },
)
