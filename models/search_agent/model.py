from typing import Optional, Any
from base import Base, ModelConfig
from langchain_openai import ChatOpenAI

class SearchAgent(Base):
    default_config = ModelConfig(
        model_name="qwen-plus",
        temperature=0.0,
        api_key_name="ALI_API_KEY",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    
    def __init__(
        self, 
        config: Optional[ModelConfig] = None, 
        dev_mode: bool = False, 
        # stream: bool = False
    ):
        super().__init__(config, dev_mode)
        
        self.llm = ChatOpenAI(
            model=self.config.model_name,
            temperature=self.config.temperature,
            base_url=self.config.base_url,
            api_key=self.api_key,
        )

    def build_search_query(self, statement: Any):
        """Build a search query based on a statement context data"""
        pass

    def search(self, query: str):
        """Determine complexity of search target and pick a tool to search expected evidence. """
        pass
