from typing import Any, TypeVar, Generic

from langchain.output_parsers import OutputFixingParser
from langchain_core.output_parsers import BaseOutputParser
from langchain_openai import ChatOpenAI

T = TypeVar('T')

class SafeParse(BaseOutputParser[T], Generic[T]):
    """
    安全解析模型输出 Wrapper
    
    Args:
        parser: 解析器
        error_message: 错误信息
        llm: 模型
        max_retries: 最大重试次数
    """
    
    def __init__(
        self, 
        parser: BaseOutputParser[T], 
        error_message: str = "❌ 模型输出解析失败，正在重试...",
        llm: ChatOpenAI = ChatOpenAI(model="gpt-4o-mini", temperature=0),
        max_retries: int = 3,
    ):  
        super().__init__()
        self._parser = parser
        self._error_message = error_message
        self._llm = llm
        self._max_retries = max_retries

    def parse(self, text: str) -> T:
        try:
            return self._parser.parse(text)
        except Exception:
            print(self._error_message)
            return OutputFixingParser.from_llm(
                parser=self._parser,
                llm=self._llm,
                max_retries=self._max_retries,
            ).parse(text)
    
    def get_format_instructions(self) -> str:
        """Instructions on how the LLM output should be formatted."""
        return self._parser.get_format_instructions()
    
    @property
    def _type(self) -> str:
        """Return the output parser type for serialization."""
        return f"safe_parse_{self._parser._type}"
