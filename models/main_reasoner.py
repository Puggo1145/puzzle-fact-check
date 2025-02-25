from typing import Optional, Dict, Any, Union
from .base import ModelConfig, Base
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from .prompts import (
    fact_check_plan_prompt,
    fact_check_plan_parser,
)

class MainReasoner(Base):
    """
    主推理模型，使用 deepseek R1
    负责全局事实陈述提取、任务规划和推理
    """

    default_config = ModelConfig(
        model_name="deepseek-r1",
        api_key_name="ALI_API_KEY",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        # api_key_name="DEEPSEEK_API_KEY",
    )

    def __init__(
        self, 
        model_config: Optional[ModelConfig] = None, 
        dev_mode: bool = False,
        stream: bool = False
    ):
        """
        初始化主推理模型
        """
        super().__init__(model_config, dev_mode, stream)

        self.model = ChatOpenAI(
            model=self.config.model_name,
            api_key=self.api_key,
            temperature=self.config.temperature,
            base_url=self.config.base_url,
            streaming=self.stream,
        )

    def plan_fact_check(self, news_text: str) -> Union[Dict[str, Any], str]:
        """
        对新闻文本进行核查前规划：
        1. 提取陈述
        2. 评估每个陈述，确定核查点
        3. 规划相应的检索方案

        Args:
            news_text: 新闻文本
            stream: 是否使用流式输出，默认为False

        Returns:
            如果stream=False，返回Dict: 包含陈述列表和选定核查点的完整分析结果
            如果stream=True，返回str: 完整的输出文本
        """
        if self.stream:
            # 执行链
            chain = fact_check_plan_prompt | self.model | StrOutputParser()
            chain_on_stream = chain.stream({"news_text": news_text})
            
            results = ""
            for chunk in chain_on_stream:
                results += chunk
                print(chunk, end="", flush=True)
            
            # 返回累积的文本
            return results
        else:
            # 非流式模式，返回解析后的结构化数据
            chain = fact_check_plan_prompt | self.model | fact_check_plan_parser
            response = chain.invoke({"news_text": news_text})
            return response
