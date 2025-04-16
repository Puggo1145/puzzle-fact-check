from pydantic import BaseModel, Field, field_validator
from config import MODEL_CONFIGS


class BaseModelConfig(BaseModel):
    model_name: str = Field(..., description="模型名称")
    model_provider: str = Field(..., description="模型提供商")
    temperature: float = Field(default=0, description="温度")
    streaming: bool = Field(default=True, description="是否流式输出")


class MainAgentConfig(BaseModelConfig):
    max_retries: int = Field(ge=0, le=10, description="最大重试次数")


class MetadataExtractorConfig(BaseModelConfig):
    pass


class SearcherConfig(BaseModelConfig):
    max_search_tokens: int = Field(ge=5000, lt=50000, description="最大搜索token数")
    selected_tools: list[str] = Field(..., description="选中的工具")


class CreateAgentConfig(BaseModel):
    main_agent: MainAgentConfig
    metadata_extractor: MetadataExtractorConfig
    searcher: SearcherConfig

    @field_validator("main_agent", "metadata_extractor", "searcher")
    @classmethod
    def validate_agent_config(cls, v, info, **kwargs):
        if not v:
            return v

        # Get the field name from the info object
        field_name = info.field_name

        model_name = v.model_name
        model_provider = v.model_provider

        # Load provider configuration from the new model config
        providers = MODEL_CONFIGS.get("providers", {})
        if model_provider not in providers:
            raise ValueError(f"{field_name} 使用了不支持的模型提供商: {model_provider}")

        available_models = providers[model_provider].get("reasoning_models", []) + \
                           providers[model_provider].get("non_reasoning_models", []) + \
                           providers[model_provider].get("light_models", [])

        if model_name not in available_models:
            raise ValueError(f"{field_name} 使用的模型 {model_name} 不在 {model_provider} 提供商的支持列表中")

        # Load agent restrictions
        agent_restrictions = MODEL_CONFIGS.get("agent_restrictions", {})
        if model_name in agent_restrictions.get(field_name, {}).get("excluded", []):
            raise ValueError(f"模型 {model_name} 不能用于 {field_name}")

        return v


class FactCheckRequest(BaseModel):
    news_text: str = Field(..., description="News text to fact check")
    config: CreateAgentConfig = Field(
        description="Optional configuration for the agent"
    )
