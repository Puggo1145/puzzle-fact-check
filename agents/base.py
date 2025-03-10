from langgraph.checkpoint.memory import MemorySaver
from utils import view_graph
from db import db_integration

from typing import Dict, Any, Optional, TypeVar, Generic
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
        default_config: RunnableConfig = {},
        cli_mode: bool = True,
    ) -> None:
        self.default_config = default_config
        if not cli_mode: # 非 cli_mode 下不在 terminal 追踪模型信息
            self.default_config["callbacks"] = []
        
        self.model = model
        self.memory_saver = MemorySaver()
        self.graph = self._build_graph()
        self.cli_mode = cli_mode
        self.db_integration = db_integration
        
        view_graph(self.graph) # 运行时使用 --view-graph 输出 agent 的 graph 并停止运行
    
    def _build_graph(self) -> CompiledStateGraph | Any:
        """ 在该方法内构建 agent graph """
        
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