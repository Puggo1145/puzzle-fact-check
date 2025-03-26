from utils import view_graph

from typing import Any, Literal
from langchain_openai.chat_models.base import BaseChatOpenAI
from langgraph.graph.state import CompiledStateGraph


class BaseAgent:
    model: BaseChatOpenAI
    
    def __init__(
        self,
        model: BaseChatOpenAI,
        mode: Literal["CLI", "API"] = "CLI",
    ) -> None:
        
        self.mode = mode
        self.model = model
        self.graph = self._build_graph()
        
        view_graph(self.graph) # 运行时携带参数 --view-graph 输出 agent 的 graph 并停止运行
    
    def _build_graph(self) -> CompiledStateGraph | Any:
        """ 在该方法内构建 agent graph """
        raise NotImplementedError("子类必须实现 _build_graph 方法")
        