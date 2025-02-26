from typing import Optional, Dict, Any, List
from models.base import ModelConfig, Base
from utils import check_env
from langchain_openai import ChatOpenAI
from models.prompts.metadata_extractor import (
    metadata_extractor_prompt,
    metadata_extractor_parser
)
from utils.llm_callbacks import NormalStreamingCallback


class MetadataExtractor(Base):
    """
    新闻元数据提取模型
    负责从新闻文本中提取新闻类型和新闻六要素（5W1H），作为元数据加入到分析结果中
    """
    
    default_config = ModelConfig(
        model_name="qwen-max-latest",
        temperature=0.0,
        api_key_name="ALI_API_KEY",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    def __init__(
        self, 
        model_config: Optional[ModelConfig] = None, 
        dev_mode: bool = False,
        stream: bool = False
    ):
        """
        初始化新闻元数据提取模型
        """
        super().__init__(model_config, dev_mode, stream)
        
        api_key = check_env(self.config.api_key_name)
        
        self.model = ChatOpenAI(
            model=self.config.model_name,
            temperature=self.config.temperature,
            api_key=api_key,
            base_url=self.config.base_url,
            streaming=self.stream,
            callbacks=[NormalStreamingCallback()]
        )

    def extract_metadata(self, news_text: str) -> Dict[str, Any]:
        """
        从新闻文本中提取元数据，包括新闻类型和新闻六要素（5W1H）

        Args:
            news_text: 需要分析的新闻文本内容

        Returns:
            包含新闻元数据的字典，包括新闻类型和六要素
        """
        
        chain = metadata_extractor_prompt | self.model | metadata_extractor_parser
        response = chain.invoke({"news_text": news_text})
        
        return response
