from typing import Optional, Dict, Any, List
from models.base import ModelConfig, Base
from utils import check_env
from langchain_openai import ChatOpenAI
from .prompts import (
    knowledge_extraction_prompt,
    knowledge_extraction_parser
)
from utils.llm_callbacks import NormalStreamingCallback


class KnowledgeExtractor(Base):
    """
    知识元素提取模型
    负责从新闻文本中提取专业领域术语、关键概念和重要知识元素，作为 metadata 加入图谱根节点
    """
    
    default_config = ModelConfig(
        model_name="qwen-plus",
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
        初始化知识元素提取模型
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

    def extract_knowledge_elements(self, text: str) -> Dict[str, Any]:
        """
        从文本中提取知识元素，包括专业术语、关键概念等

        Args:
            text: 需要分析的文本内容

        Returns:
            包含知识元素的字典
        """
        
        chain = knowledge_extraction_prompt | self.model | knowledge_extraction_parser
        response = chain.invoke({"text": text})
        
        return response 