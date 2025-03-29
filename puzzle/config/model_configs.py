# 定义可用模型列表和限制
AVAILABLE_MODELS = {
    "openai": ["chatgpt-4o-latest", "gpt-4o", "gpt-4o-mini"],
    "qwen": ["qwq-plus-latest", "qwen-plus-latest", "qwen-turbo"],
    "deepseek": ["deepseek-reasoner", "deepseek-chat"]
}

# 定义不同Agent类型的模型限制
MODEL_RESTRICTIONS = {
    "main_agent": {
        # main agent 不支持轻量级模型
        "excluded": ["gpt-4o-mini", "qwen-turbo"]
    },
    "metadata_extractor": {
        # metadata extractor 不支持使用推理模型
        "excluded": ["qwq-plus-latest", "deepseek-reasoner"] 
    },
    "searcher": {
        # search agent 不支持轻量级模型
        "excluded": ["gpt-4o-mini", "qwen-turbo"]
    }
}
