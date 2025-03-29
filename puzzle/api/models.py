from pydantic import BaseModel, Field, field_validator
from config.model_configs import AVAILABLE_MODELS, MODEL_RESTRICTIONS


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
    max_search_tokens: int = Field(gt=5000, lt=100000, description="最大搜索token数")
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

        if model_provider not in AVAILABLE_MODELS:
            raise ValueError(f"{field_name} 使用了不支持的模型提供商: {model_provider}")

        if model_name not in AVAILABLE_MODELS[model_provider]:
            raise ValueError(
                f"{field_name} 使用的模型 {model_name} 不在 {model_provider} 提供商的支持列表中"
            )

        if model_name in MODEL_RESTRICTIONS[field_name]["excluded"]:
            raise ValueError(f"模型 {model_name} 不能用于 {field_name}")

        return v


class FactCheckRequest(BaseModel):
    news_text: str = Field(..., description="News text to fact check")
    config: CreateAgentConfig = Field(
        description="Optional configuration for the agent"
    )
