from langgraph.checkpoint.memory import MemorySaver
from utils import view_graph

from typing import (
    Dict, 
    Any, 
    Optional, 
    TypeVar, 
    Generic, 
    Literal,
)
from langchain.chat_models.base import BaseChatModel
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph


ModelT = TypeVar("ModelT", bound=BaseChatModel)

class BaseAgent(Generic[ModelT]):
    model: ModelT
    memory_saver: MemorySaver
    
    def __init__(
        self,
        model: ModelT,
        mode: Literal["CLI", "API"] = "CLI",
        default_config: RunnableConfig = {},
    ) -> None:
        self.default_config = default_config
        
        self.mode = mode
        self.model = model
        self.memory_saver = MemorySaver()
        self.graph = self._build_graph()
        
        view_graph(self.graph) # 运行时携带参数 --view-graph 输出 agent 的 graph 并停止运行
    
    def _build_graph(self) -> CompiledStateGraph | Any:
        """ 在该方法内构建 agent graph """
        raise NotImplementedError("子类必须实现 _build_graph 方法")
        
    def invoke(
        self, 
        initial_state: Any,
        config: Optional[RunnableConfig] = None
    ) -> Dict[str, Any] | Any:
        """agent 调用方法"""
        if config is not None:
            self.default_config.update(config)
        
        return self.graph.invoke(
            initial_state,
            config=self.default_config
        )
        