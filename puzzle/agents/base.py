from langgraph.checkpoint.memory import MemorySaver
from langchain_core.callbacks import BaseCallbackHandler
from utils import view_graph
from db import db_integration

from typing import List, Dict, Any, Optional, TypeVar, Generic, Literal
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
        api_callbacks: List[BaseCallbackHandler],
        cli_callbacks: List[BaseCallbackHandler],
        default_config: RunnableConfig = {},
        mode: Literal["CLI", "API"] = "CLI",
    ) -> None:
        self.default_config = default_config
        if mode == "API":
            self.default_config["callbacks"] = api_callbacks
        elif mode == "CLI":
            self.default_config["callbacks"] = cli_callbacks
        
        self.model = model
        self.memory_saver = MemorySaver()
        self.graph = self._build_graph()
        self.mode = mode
        self.db_integration = db_integration
        
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
        

class BaseAgentCallback(BaseCallbackHandler):
    def __init__(self):
        super().__init__()
        
        self.current_node: str | None = None
    
    def on_chain_start(
        self, 
        serialized: Dict[str, Any], 
        inputs: Dict[str, Any], 
        **kwargs: Any
    ) -> None:
        if kwargs and "metadata" in kwargs and isinstance(kwargs["metadata"], dict):
            self.current_node = kwargs["metadata"].get("langgraph_node", None)
    