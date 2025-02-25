from langchain_core.prompts import ChatPromptTemplate

extract_structured_data_prompt = ChatPromptTemplate.from_template(
    """
    请根据以下 JSON schema 从文本中提取结构化数据:
    {schema_str}

    文本内容:
    {text}

    请仅返回符合上述模式的JSON数据，不要包含任何其他解释。
    """
)
