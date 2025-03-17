from langgraph.checkpoint.memory import MemorySaver
from langchain_core.callbacks import BaseCallbackHandler
from utils import view_graph
from db import db_integration

from typing import (
    List, 
    Dict, 
    Any, 
    Optional, 
    TypeVar, 
    Generic, 
    Literal,
    Callable,
    Union,
    Tuple,
)
from enum import Enum
from uuid import UUID
from langchain.chat_models.base import BaseChatModel
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from langchain_core.outputs import GenerationChunk, ChatGenerationChunk, LLMResult
    

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
        

class NodeEventTiming(Enum):
    """node 事件触发时机"""
    ON_LLM_START = "on_llm_start"
    ON_LLM_NEW_TOKEN = "on_llm_new_token"
    ON_LLM_END = "on_llm_end"
    ON_LLM_ERROR = "on_llm_error"
    ON_CHAIN_START = "on_chain_start"
    ON_CHAIN_END = "on_chain_end"
    ON_TOOL_START = "on_tool_start"
    ON_TOOL_END = "on_tool_end"
    ON_TOOL_ERROR = "on_tool_error"

EventHandlers = Dict[str, Dict[NodeEventTiming, List[Tuple[Callable, Optional[Callable]]]]]


class NodeEventManager:
    """Graph 节点事件管理器，基于 Graph node 执行阶段触发事件"""
    
    def __init__(self):
        # 存储格式: {node_name: {timing: [callbacks]}}
        self._event_handlers: EventHandlers = {}
    
    def register(
        self, 
        node_name: Optional[str], 
        callback: Callable, 
        timing: NodeEventTiming = NodeEventTiming.ON_CHAIN_END,
        condition: Optional[Callable] = None
    ) -> None:
        """
        注册 node 事件回调
        
        Args:
            node_name: 节点名称
            callback: 回调函数
            timing: 触发时机，默认为节点结束时
            condition: 可选的条件函数，返回True时才执行回调
        """
        
        # 如果 node_name 为 None，则事件在所有 node 上都触发
        if node_name is None:
            node_name = "ALL"

        # 对应 node_name 事件触发器初始化
        if node_name not in self._event_handlers:
            self._event_handlers[node_name] = {
                NodeEventTiming.ON_LLM_START: [],
                NodeEventTiming.ON_LLM_NEW_TOKEN: [],
                NodeEventTiming.ON_LLM_END: [],
                NodeEventTiming.ON_LLM_ERROR: [],
                NodeEventTiming.ON_TOOL_START: [],
                NodeEventTiming.ON_TOOL_END: [],
                NodeEventTiming.ON_TOOL_ERROR: [],
                NodeEventTiming.ON_CHAIN_START: [],
                NodeEventTiming.ON_CHAIN_END: [],
            }

        self._event_handlers[node_name][timing].append((callback, condition))
    
    def trigger(
        self, 
        current_node: str, 
        timing: NodeEventTiming,
        context: Dict[str, Any]
    ) -> None:
        """
        触发 node 事件
        
        Args:
            node_name: 节点名称
            timing: 触发时机
            context: 上下文信息，将传递给回调函数
        """
        # 先执行 ALL node 事件
        handlers_exec_all = self._event_handlers["ALL"][timing]
        for callback, condition in handlers_exec_all:
            if condition is None or condition(context):
                callback(context)
        
        # 再执行当前 node 事件
        if current_node not in self._event_handlers:
            return
        
        handlers = self._event_handlers[current_node][timing]
        for callback, condition in handlers:
            # 如果有条件函数，先检查条件
            if condition is None or condition(context):
                callback(context)


class BaseAgentCallback(BaseCallbackHandler):
    def __init__(self):
        super().__init__()
        self.current_node: str | None = None
        self.event_manager = NodeEventManager()
        
    def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        if self.current_node:
            context = {
                "serialized": serialized,
                "prompts": prompts,
                "run_id": run_id,
                "parent_run_id": parent_run_id,
                "tags": tags,
                "metadata": metadata,
                "kwargs": kwargs
            }
            self.event_manager.trigger(
                self.current_node, 
                NodeEventTiming.ON_LLM_START, 
                context
            )
            
    def on_llm_new_token(
        self,
        token: str,
        *,
        chunk: Optional[Union[GenerationChunk, ChatGenerationChunk]] = None,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> None:
        if self.current_node:
            context = {
                "token": token,
                "chunk": chunk,
                "run_id": run_id,
                "parent_run_id": parent_run_id,
                "tags": tags,
                "kwargs": kwargs
            }
            self.event_manager.trigger(
                self.current_node, 
                NodeEventTiming.ON_LLM_NEW_TOKEN, 
                context
            )
            
    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        if self.current_node:
            context = {
                "response": response,
                "run_id": run_id,
                "parent_run_id": parent_run_id,
                "kwargs": kwargs
            }
            self.event_manager.trigger(
                self.current_node, 
                NodeEventTiming.ON_LLM_END, 
                context
            )
            
    def on_llm_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        if self.current_node:
            context = {
                "error": error,
                "run_id": run_id,
                "parent_run_id": parent_run_id,
                "kwargs": kwargs
            }
            self.event_manager.trigger(
                self.current_node, 
                NodeEventTiming.ON_LLM_ERROR, 
                context
            )
            
    def on_tool_start(
        self,
        serialized: dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        inputs: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        if self.current_node:
            context = {
                "serialized": serialized,
                "input_str": input_str,
                "run_id": run_id,
                "parent_run_id": parent_run_id,
                "tags": tags,
                "metadata": metadata,
                "inputs": inputs,
                "kwargs": kwargs
            }
            self.event_manager.trigger(
                self.current_node, 
                NodeEventTiming.ON_TOOL_START, 
                context
            )
            
    def on_tool_end(
        self,
        output: Any,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        if self.current_node:
            context = {
                "output": output,
                "run_id": run_id,
                "parent_run_id": parent_run_id,
                "kwargs": kwargs
            }
            self.event_manager.trigger(
                self.current_node, 
                NodeEventTiming.ON_TOOL_END, 
                context
            )
            
    def on_tool_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        if self.current_node:
            context = {
                "error": error,
                "run_id": run_id,
                "parent_run_id": parent_run_id,
                "kwargs": kwargs
            }
            self.event_manager.trigger(
                self.current_node, 
                NodeEventTiming.ON_TOOL_ERROR, 
                context
            )
            
    def on_chain_start(
        self, 
        serialized: Dict[str, Any], 
        inputs: Dict[str, Any], 
        **kwargs: Any
    ) -> None:
        if kwargs and "metadata" in kwargs and isinstance(kwargs["metadata"], dict):
            self.current_node = kwargs["metadata"].get("langgraph_node", None)
            
            # 如果有当前节点，触发节点开始事件
            if self.current_node:
                context = {
                    "serialized": serialized,
                    "inputs": inputs,
                    "kwargs": kwargs
                }
                self.event_manager.trigger(
                    self.current_node, 
                    NodeEventTiming.ON_CHAIN_START, 
                    context
                )
    
    def on_chain_end(
        self,
        outputs: dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> None:
        GRAPH_FINISHED = bool(tags and len(tags) > 0 and "graph" in tags[0])
        
        # 如果有当前节点，触发节点结束事件
        if self.current_node and GRAPH_FINISHED:
            context = {
                "outputs": outputs,
                "run_id": run_id,
                "parent_run_id": parent_run_id,
                "tags": tags,
                "kwargs": kwargs
            }
            self.event_manager.trigger(
                self.current_node, 
                NodeEventTiming.ON_CHAIN_END, 
                context
            )
    
    def register_node_event(
        self,
        callback: Callable,
        node_name: Optional[str] = None,
        timing: Union[NodeEventTiming, str] = NodeEventTiming.ON_CHAIN_END,
        condition: Optional[Callable] = None
    ) -> None:
        """
        注册 node 事件回调
        
        Args:
            node_name: 节点名称
            callback: 回调函数，接收一个context参数
            timing: 触发时机，默认为节点结束时
            condition: 可选的条件函数，返回True时才执行回调
        """
        # 如果timing是字符串，转换为枚举
        if isinstance(timing, str):
            timing = NodeEventTiming(timing)
            
        self.event_manager.register(node_name, callback, timing, condition)
    