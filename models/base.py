from typing import Optional
from pydantic import BaseModel
from utils import check_env

class ModelConfig(BaseModel):
    model_name: str
    api_key_name: str
    temperature: Optional[float] = None
    base_url: Optional[str] = None
    

class Base:
    """
    所有模型类的基类，处理模型配置
    """
    
    default_config: ModelConfig
    
    def __init__(
        self, 
        model_config: Optional[ModelConfig] = None, 
        dev_mode: bool = False,
        stream: bool = False
    ):
        """
        所有模型类的基类
        
        Args:
            model_config: 可选的模型配置，如果不提供则使用默认配置
            dev_mode: 是否开启开发模式，开启后会打印配置信息
        """
        
        self.config = model_config if model_config is not None else self.default_config
        if self.config is None:
            raise ValueError("必须提供模型配置或设置默认配置")
        
        self.api_key = check_env(self.config.api_key_name)
        self.stream = stream
        
        self.dev_mode = dev_mode
        if self.dev_mode:
            print(f"[DEV MODE] 正在调用模型: {self.config.model_name}")
            print(f"  - temperature: {self.config.temperature}\n")
