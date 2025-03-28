from typing import Dict, Any, List, Optional, Union
from queue import Queue
import uuid
import threading
import traceback
import time
import json
import pubsub.pub as pub

from agents.main.graph import MainAgent
from agents.main.events import MainAgentEvents
from agents.main.states import CheckPoints, RetrievalResultVerification
from agents.metadata_extractor.events import MetadataExtractAgentEvents
from agents.searcher.events import SearchAgentEvents

# 定义一个模拟客户端类
class MockClient:
    def create(self, *args, **kwargs):
        raise RuntimeError("Agent已被中断")
    
    def close(self, *args, **kwargs):
        pass

class SSEModeEvents:
    """
    与 CLIModeEvents 类似，但输出为 SSE 事件流，用于前端实时显示
    """
    def __init__(self, event_queue: Queue):
        self.event_queue = event_queue
        self.start_time = None
        self.token_usage = 0
        self.has_thinking_started = False
        self.has_content_started = False
        self.current_node = None
        
        self.setup_subscribers()

    def setup_subscribers(self):
        # LLM 开始事件
        pub.subscribe(
            self.on_extract_check_point_start,
            MainAgentEvents.EXTRACT_CHECK_POINT_START.value,
        )
        pub.subscribe(
            self.on_evaluate_search_result_start,
            MainAgentEvents.EVALUATE_SEARCH_RESULT_START.value,
        )
        pub.subscribe(
            self.on_write_report_start,
            MainAgentEvents.WRITE_FACT_CHECKING_REPORT_START.value,
        )
        
        # LLM 结束事件
        pub.subscribe(
            self.on_extract_check_point_end,
            MainAgentEvents.EXTRACT_CHECK_POINT_END.value,
        )
        pub.subscribe(
            self.on_evaluate_search_result_end,
            MainAgentEvents.EVALUATE_SEARCH_RESULT_END.value,
        )
        pub.subscribe(
            self.on_write_report_end,
            MainAgentEvents.WRITE_FACT_CHECKING_REPORT_END.value,
        )
        
        # LLM 决策
        pub.subscribe(
            self.on_llm_decision,
            MainAgentEvents.LLM_DECISION.value,
        )
        
        # 元数据提取代理事件
        pub.subscribe(
            self.on_extract_basic_metadata_start,
            MetadataExtractAgentEvents.PRINT_EXTRACT_BASIC_METADATA_START.value,
        )
        pub.subscribe(
            self.on_extract_basic_metadata_end,
            MetadataExtractAgentEvents.PRINT_EXTRACT_BASIC_METADATA_END.value,
        )
        pub.subscribe(
            self.on_extract_knowledge_start,
            MetadataExtractAgentEvents.PRINT_EXTRACT_KNOWLEDGE_START.value,
        )
        pub.subscribe(
            self.on_extract_knowledge_end,
            MetadataExtractAgentEvents.PRINT_EXTRACT_KNOWLEDGE_END.value,
        )
        pub.subscribe(
            self.on_retrieve_knowledge_start,
            MetadataExtractAgentEvents.PRINT_RETRIEVE_KNOWLEDGE_START.value,
        )
        pub.subscribe(
            self.on_retrieve_knowledge_end,
            MetadataExtractAgentEvents.PRINT_RETRIEVE_KNOWLEDGE_END.value,
        )
        
        # 搜索代理事件
        pub.subscribe(
            self.on_search_agent_start,
            SearchAgentEvents.PRINT_SEARCH_AGENT_START.value,
        )
        pub.subscribe(
            self.on_evaluate_status_start,
            SearchAgentEvents.PRINT_EVALUATE_STATUS_START.value,
        )
        pub.subscribe(
            self.on_status_evaluation_end,
            SearchAgentEvents.PRINT_STATUS_EVALUATION_END.value,
        )
        pub.subscribe(
            self.on_tool_start,
            SearchAgentEvents.PRINT_TOOL_START.value,
        )
        pub.subscribe(
            self.on_tool_result,
            SearchAgentEvents.PRINT_TOOL_RESULT.value,
        )
        pub.subscribe(
            self.on_generate_answer_start,
            SearchAgentEvents.PRINT_GENERATE_ANSWER_START.value,
        )
        pub.subscribe(
            self.on_generate_answer_end,
            SearchAgentEvents.PRINT_GENERATE_ANSWER_END.value,
        )

    def send_event(self, event_type: str, data: Dict[str, Any]):
        """发送事件到队列"""
        try:
            self.event_queue.put({
                "event": event_type,
                "data": data
            })
        except Exception as e:
            # 输出异常以便调试
            print(f"Error sending event {event_type}: {e}")
            print(traceback.format_exc())
    
    # LLM 开始事件处理
    def on_extract_check_point_start(self):
        self.current_node = "extract_check_point"
        self.send_event("extract_check_point_start", {
            "message": "LLM 开始提取核查点"
        })
    
    def on_evaluate_search_result_start(self):
        self.current_node = "evaluate_search_result"
        self.send_event("evaluate_search_result_start", {
            "message": "LLM 开始评估检索结果"
        })
    
    def on_write_report_start(self):
        self.current_node = "write_fact_checking_report"
        self.send_event("write_fact_checking_report_start", {
            "message": "LLM 开始撰写核查报告"
        })
    
    # LLM 结束事件处理
    def on_extract_check_point_end(self, check_points_result: CheckPoints):
        try:
            self.send_event("extract_check_point_end", {
                "check_points": check_points_result.model_dump()
            })
        except Exception as e:
            print(f"Error in extract_check_point_end: {e}")
            print(traceback.format_exc())
            # 尝试替代方案
            serialized_data = {}
            try:
                serialized_data = {"items": [cp.model_dump() for cp in check_points_result.items]}
            except:
                serialized_data = {"error": "无法序列化核查点数据"}
            
            self.send_event("extract_check_point_end", {
                "check_points": serialized_data
            })
    
    def on_evaluate_search_result_end(self, verification_result: RetrievalResultVerification):
        try:
            self.send_event("evaluate_search_result_end", {
                "verification_result": verification_result.model_dump()
            })
        except Exception as e:
            print(f"Error in evaluate_search_result_end: {e}")
            print(traceback.format_exc())
            # 尝试替代方案
            self.send_event("evaluate_search_result_end", {
                "verification_result": {
                    "reasoning": getattr(verification_result, "reasoning", "无法获取推理过程"),
                    "verified": getattr(verification_result, "verified", False)
                }
            })
    
    def on_write_report_end(self, response_text: str):
        self.send_event("write_fact_checking_report_end", {
            "report": response_text
        })
    
    def on_llm_decision(
        self, 
        decision: str,
        reason: str | None = None
    ):
        self.send_event("llm_decision", {
            "decision": decision,
            "reason": reason
        })

    # 元数据提取代理事件处理器
    def on_extract_basic_metadata_start(self):
        self.send_event("extract_basic_metadata_start", {
            "message": "开始提取新闻基本元数据"
        })
    
    def on_extract_basic_metadata_end(self, basic_metadata):
        self.send_event("extract_basic_metadata_end", {
            "basic_metadata": self._make_serializable(basic_metadata)
        })
    
    def on_extract_knowledge_start(self):
        self.send_event("extract_knowledge_start", {
            "message": "开始提取知识元素"
        })
    
    def on_extract_knowledge_end(self, knowledges):
        self.send_event("extract_knowledge_end", {
            "knowledges": self._make_serializable(knowledges)
        })
    
    def on_retrieve_knowledge_start(self):
        self.send_event("retrieve_knowledge_start", {
            "message": "开始检索知识元素定义"
        })
    
    def on_retrieve_knowledge_end(self, retrieved_knowledge):
        self.send_event("retrieve_knowledge_end", {
            "retrieved_knowledge": self._make_serializable(retrieved_knowledge)
        })
    
    # 搜索代理事件处理器
    def on_search_agent_start(self, content, purpose, expected_sources):
        self.send_event("search_agent_start", {
            "content": content,
            "purpose": purpose,
            "expected_sources": expected_sources
        })
    
    def on_evaluate_status_start(self, model_name):
        self.send_event("evaluate_status_start", {
            "message": f"搜索代理({model_name})开始评估搜索状态"
        })
    
    def on_status_evaluation_end(self, status):
        self.send_event("status_evaluation_end", {
            "status": self._make_serializable(status)
        })
    
    def on_tool_start(self, tool_name, input_str):
        self.send_event("tool_start", {
            "tool_name": tool_name,
            "input": input_str
        })
    
    def on_tool_result(self, output):
        self.send_event("tool_result", {
            "output": str(output)[:1000] + ("..." if len(str(output)) > 1000 else "")
        })
    
    def on_generate_answer_start(self, model_name):
        self.send_event("generate_answer_start", {
            "message": f"搜索代理({model_name})开始生成答案"
        })
    
    def on_generate_answer_end(self, result):
        self.send_event("generate_answer_end", {
            "result": self._make_serializable(result)
        })

    def _make_serializable(self, obj: Any) -> Union[Dict[str, Any], List[Any], str, int, float, bool, None]:
        """将对象转换为可JSON序列化的格式"""
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        elif hasattr(obj, "__dict__"):
            return {k: self._make_serializable(v) for k, v in obj.__dict__.items() if not k.startswith("_")}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            return str(obj)


class AgentService:
    def __init__(self):
        self.agent_instances: Dict[str, MainAgent] = {}
        self.event_queues: Dict[str, Queue] = {}
        self.agent_threads: Dict[str, threading.Thread] = {}
        self.agent_states: Dict[str, Dict[str, Any]] = {}
        self.sse_events: Dict[str, SSEModeEvents] = {}
        self.interruption_flags: Dict[str, bool] = {}
        self.session_active: Dict[str, bool] = {}
        # Add a dictionary to store thread cancellation events
        self.cancellation_events: Dict[str, threading.Event] = {}
    
    def create_agent(self, config: Dict[str, Any]) -> str:
        """创建一个新的 Agent 实例，返回唯一标识符"""
        session_id = str(uuid.uuid4())
        event_queue = Queue()
        
        # 从配置中获取模型，如果没有则使用默认配置
        from models import ChatQwen, ChatGemini
        from langchain_openai import ChatOpenAI
        
        model_name = config.get("model_name", "chatgpt-4o-latest")
        model_provider = config.get("model_provider", "openai")
        
        if model_provider == "openai":
            model = ChatOpenAI(
                model=model_name,
                temperature=0,
                streaming=True
            )
            metadata_model = ChatOpenAI(
                model="gpt-4o-mini", 
                temperature=0
            )
            search_model = ChatOpenAI(
                model=model_name,
                temperature=0,
                streaming=True
            )
        elif model_provider == "qwen":
            model = ChatQwen(
                model=model_name,
                streaming=True
            )
            metadata_model = ChatQwen(
                model=model_name
            )
            search_model = ChatQwen(
                model=model_name,
                streaming=True
            )
        elif model_provider == "gemini":
            model = ChatGemini(
                model=model_name,
                temperature=0
            )
            metadata_model = ChatGemini(
                model=model_name,
                temperature=0
            )
            search_model = ChatGemini(
                model=model_name,
                temperature=0
            )
        else:
            # 默认使用 OpenAI
            model = ChatOpenAI(
                model="gpt-4o",
                temperature=0,
                streaming=True
            )
            metadata_model = ChatOpenAI(
                model="gpt-4o-mini", 
                temperature=0
            )
            search_model = ChatOpenAI(
                model="gpt-4o",
                temperature=0,
                streaming=True
            )
        
        agent = MainAgent(
            model=model,
            metadata_extract_model=metadata_model,
            search_model=search_model,
            mode="API",
            max_search_tokens=config.get("searcher", {}).get("max_search_tokens", 10000),
            max_retries=config.get("main_agent", {}).get("max_retries", 1),
        )
        
        # 注册 SSE 事件处理
        sse_events = SSEModeEvents(event_queue)
        
        self.agent_instances[session_id] = agent
        self.event_queues[session_id] = event_queue
        self.agent_states[session_id] = {}
        self.sse_events[session_id] = sse_events
        self.interruption_flags[session_id] = False
        self.session_active[session_id] = True
        # Initialize cancellation event for this session
        self.cancellation_events[session_id] = threading.Event()
        
        return session_id
    
    def run_agent(self, session_id: str, news_text: str, config: Dict[str, Any] | None = None):
        """在后台线程运行 agent"""
        if session_id not in self.agent_instances:
            raise ValueError(f"Agent with session_id {session_id} not found")
        
        # 重置中断标志
        self.interruption_flags[session_id] = False
        # Reset cancellation event
        self.cancellation_events[session_id].clear()
        
        # 向前端发送任务开始的事件
        self.event_queues[session_id].put({
            "event": "task_start",
            "data": {"message": "开始核查任务"}
        })
        
        # 应用配置
        if config:
            self._apply_agent_config(session_id, config)
        
        def run_agent_task():
            # 捕获会话ID，防止在Thread中丢失引用
            local_session_id = session_id
            try:
                # 获取agent实例
                agent = self.agent_instances.get(local_session_id)
                if agent is None:
                    print(f"Agent instance for session {local_session_id} not found, task aborted")
                    return
                    
                cancellation_event = self.cancellation_events.get(local_session_id)
                if cancellation_event is None:
                    # 如果找不到取消事件，创建一个新的并立即将其设置为已触发状态
                    cancellation_event = threading.Event()
                    cancellation_event.set()
                    print(f"Cancellation event for session {local_session_id} not found, creating a new one and setting it")
                
                # 执行前检查连接是否中断
                should_interrupt = (
                    local_session_id not in self.session_active or 
                    not self.session_active.get(local_session_id, False) or
                    (local_session_id in self.interruption_flags and self.interruption_flags[local_session_id]) or
                    cancellation_event.is_set()
                )
                
                if should_interrupt:
                    if local_session_id in self.event_queues:
                        self.event_queues[local_session_id].put({
                            "event": "task_interrupted",
                            "data": {"message": "任务被中断"}
                        })
                    return
                
                # 使用轮询方式检查中断状态
                def should_continue():
                    # 安全检查 - 如果会话已不存在，返回False
                    if (local_session_id not in self.interruption_flags or 
                        local_session_id not in self.session_active):
                        return False
                        
                    return not (self.interruption_flags[local_session_id] or 
                               not self.session_active[local_session_id] or 
                               cancellation_event.is_set())
                
                # 直接执行 Agent，无需人类反馈
                # 传递 should_continue 回调函数给 agent 以便定期检查是否应该中断
                result = agent.invoke(
                    {"news_text": news_text},
                    {"configurable": {"thread_id": local_session_id, "should_continue": should_continue}}
                )
                
                # 执行后检查是否需要中断
                should_interrupt = (
                    local_session_id not in self.session_active or 
                    not self.session_active.get(local_session_id, False) or
                    (local_session_id in self.interruption_flags and self.interruption_flags[local_session_id]) or
                    cancellation_event.is_set()
                )
                
                if should_interrupt:
                    if local_session_id in self.event_queues:
                        self.event_queues[local_session_id].put({
                            "event": "task_interrupted",
                            "data": {"message": "任务已被中断"}
                        })
                    return
                
                # 完成后发送事件 - 先检查会话是否仍然存在
                if local_session_id in self.event_queues:
                    self.event_queues[local_session_id].put({
                        "event": "task_complete",
                        "data": {
                            "message": "核查任务完成",
                            "result": self._make_serializable(result)
                        }
                    })
                
                # 清理相关资源 - 先检查会话是否仍然存在
                if local_session_id in self.agent_instances:
                    self.cleanup_resources(local_session_id)
            except RuntimeError as e:
                # 特别处理中断错误，不作为真正的错误处理
                if str(e) == "Agent已被中断":
                    if local_session_id in self.event_queues:
                        self.event_queues[local_session_id].put({
                            "event": "task_interrupted",
                            "data": {"message": "任务已被中断"}
                        })
                else:
                    print(f"Error in agent thread: {e}")
                    print(traceback.format_exc())
                    # 发送错误事件
                    if local_session_id in self.event_queues:
                        self.event_queues[local_session_id].put({
                            "event": "error",
                            "data": {"message": f"执行错误: {str(e)}"}
                        })
            except KeyError as e:
                # 专门处理会话已被删除的情况
                print(f"Session key error in agent thread: {e} - The session may have been destroyed")
                print(traceback.format_exc())
            except Exception as e:
                print(f"Error in agent thread: {e}")
                print(traceback.format_exc())
                # 发送错误事件
                if local_session_id in self.event_queues:
                    self.event_queues[local_session_id].put({
                        "event": "error",
                        "data": {"message": f"执行错误: {str(e)}"}
                    })
        
        # 启动线程
        thread = threading.Thread(target=run_agent_task)
        thread.daemon = True
        thread.start()
        self.agent_threads[session_id] = thread
    
    def _apply_agent_config(self, session_id: str, config: Dict[str, Any]):
        """应用从前端传递的配置"""
        try:
            agent = self.agent_instances[session_id]
            
            # 检查是否有主智能体配置
            if "main_agent" in config:
                main_config = config["main_agent"]
                if "max_retries" in main_config:
                    # 主智能体接受 max_retries 配置
                    agent.max_retries = main_config["max_retries"]
            
            # 检查是否有搜索代理配置
            if "searcher" in config:
                searcher_config = config["searcher"]
                if "max_search_tokens" in searcher_config:
                    # 搜索代理接受 max_search_tokens 配置
                    agent.search_agent.max_search_tokens = searcher_config["max_search_tokens"]
            
        except Exception as e:
            print(f"Error applying config: {e}")
            print(traceback.format_exc())
    
    def interrupt_agent(self, session_id: str) -> bool:
        """中断正在执行的智能体任务"""
        if session_id not in self.agent_instances:
            return False
        
        # 设置中断标志
        self.interruption_flags[session_id] = True
        
        # 设置取消事件，通知所有等待线程立即退出
        if session_id in self.cancellation_events:
            self.cancellation_events[session_id].set()
        
        # 发送中断事件到事件队列
        try:
            # 首先检查事件队列是否存在
            if session_id in self.event_queues:
                self.event_queues[session_id].put({
                    "event": "task_interrupted",
                    "data": {"message": "任务正在被中断..."}
                })
            
            # 强制停止所有任务
            if session_id in self.agent_instances:
                # 1. 调用取消方法停止正在进行的任务
                try:
                    if hasattr(self.agent_instances[session_id], 'cancel_running_tasks'):
                        self.agent_instances[session_id].cancel_running_tasks()
                except Exception as e:
                    print(f"取消任务时出错: {e}")
                
                # 2. 强制关闭所有API客户端连接
                agent = self.agent_instances[session_id]
                
                # 关闭主模型客户端
                try:
                    if hasattr(agent, 'model') and hasattr(agent.model, 'client'):
                        if agent.model.client is not None and hasattr(agent.model.client, 'close'):
                            agent.model.client.close()
                        # 使用预定义的MockClient类替代None
                        agent.model.client = MockClient()
                except Exception as e:
                    print(f"关闭主模型客户端失败: {e}")
                
                # 关闭元数据提取模型客户端
                try:
                    if hasattr(agent, 'metadata_extract_agent') and hasattr(agent.metadata_extract_agent, 'model') and hasattr(agent.metadata_extract_agent.model, 'client'):
                        if agent.metadata_extract_agent.model.client is not None and hasattr(agent.metadata_extract_agent.model.client, 'close'):
                            agent.metadata_extract_agent.model.client.close()
                        agent.metadata_extract_agent.model.client = MockClient()
                except Exception as e:
                    print(f"关闭元数据提取模型客户端失败: {e}")
                
                # 关闭搜索模型客户端
                try:
                    if hasattr(agent, 'search_agent') and hasattr(agent.search_agent, 'model') and hasattr(agent.search_agent.model, 'client'):
                        if agent.search_agent.model.client is not None and hasattr(agent.search_agent.model.client, 'close'):
                            agent.search_agent.model.client.close()
                        agent.search_agent.model.client = MockClient()
                except Exception as e:
                    print(f"关闭搜索模型客户端失败: {e}")
            
            # 等待一小段时间确认线程已停止
            timeout = 2  # 缩短等待时间到2秒
            start_time = time.time()
            while session_id in self.agent_threads and self.agent_threads[session_id].is_alive() and time.time() - start_time < timeout:
                time.sleep(0.1)
            
            # 如果线程仍在运行，尝试彻底清理资源
            if session_id in self.agent_threads and self.agent_threads[session_id].is_alive():
                print(f"线程仍在运行，执行强制清理")
                
                # 清理资源并移除线程引用
                if session_id in self.agent_instances:
                    # 移除事件订阅
                    if session_id in self.sse_events:
                        # 尝试取消所有事件订阅
                        try:
                            # 直接使用全局的unsubAll方法取消所有订阅，不需要指定具体主题
                            pub.unsubAll()
                        except Exception as e:
                            print(f"移除所有事件订阅失败: {e}")
            
            # 发送最终中断确认
            if session_id in self.event_queues:
                self.event_queues[session_id].put({
                    "event": "task_interrupted",
                    "data": {"message": "任务已成功中断"}
                })
            
            return True
        except Exception as e:
            print(f"Error interrupting agent: {e}")
            print(traceback.format_exc())
            return False
    
    def handle_client_disconnect(self, session_id: str) -> bool:
        """处理客户端断开连接的情况"""
        if session_id not in self.agent_instances:
            return False
        
        print(f"Client disconnected, immediately destroying session {session_id}")
        
        # 标记会话不再活跃
        self.session_active[session_id] = False
        
        # 设置取消事件
        if session_id in self.cancellation_events:
            self.cancellation_events[session_id].set()
        
        # 立即中断所有相关任务
        self.interrupt_agent(session_id)
        
        # 强制清理所有与该会话相关的资源
        try:
            # 移除事件订阅
            if session_id in self.sse_events:
                try:
                    # 直接使用全局的unsubAll方法取消所有订阅，不需要指定具体主题
                    pub.unsubAll()
                except Exception as e:
                    print(f"移除所有事件订阅失败: {e}")
            
            # 清除代理实例的引用，允许垃圾回收
            if session_id in self.agent_instances:
                # 清理主代理中的所有模型客户端
                agent = self.agent_instances[session_id]
                
                # 关闭所有可能的客户端连接
                try:
                    # 关闭主模型客户端
                    if hasattr(agent, 'model') and hasattr(agent.model, 'client'):
                        if hasattr(agent.model.client, 'close'):
                            agent.model.client.close()
                    
                    # 关闭元数据提取模型客户端
                    if hasattr(agent, 'metadata_extract_agent') and hasattr(agent.metadata_extract_agent, 'model') and hasattr(agent.metadata_extract_agent.model, 'client'):
                        if hasattr(agent.metadata_extract_agent.model.client, 'close'):
                            agent.metadata_extract_agent.model.client.close()
                    
                    # 关闭搜索模型客户端
                    if hasattr(agent, 'search_agent') and hasattr(agent.search_agent, 'model') and hasattr(agent.search_agent.model, 'client'):
                        if hasattr(agent.search_agent.model.client, 'close'):
                            agent.search_agent.model.client.close()
                except Exception as e:
                    print(f"关闭客户端连接失败: {e}")
                
                # 从字典中删除而不是设置None
                del self.agent_instances[session_id]
            
            # 清理其他相关资源
            if session_id in self.agent_threads:
                del self.agent_threads[session_id]
            
            if session_id in self.event_queues:
                # 清空事件队列
                while not self.event_queues[session_id].empty():
                    try:
                        self.event_queues[session_id].get_nowait()
                    except:
                        pass
                del self.event_queues[session_id]
            
            if session_id in self.agent_states:
                del self.agent_states[session_id]
            
            if session_id in self.sse_events:
                del self.sse_events[session_id]
            
            if session_id in self.cancellation_events:
                del self.cancellation_events[session_id]
            
            if session_id in self.interruption_flags:
                del self.interruption_flags[session_id]
            
            if session_id in self.session_active:
                del self.session_active[session_id]
            
            print(f"Successfully destroyed all resources for session {session_id}")
            return True
        
        except Exception as e:
            print(f"Error destroying agent resources: {e}")
            print(traceback.format_exc())
            return False
    
    def _make_serializable(self, obj: Any) -> Union[Dict[str, Any], List[Any], str, int, float, bool, None]:
        """
        将对象转换为可JSON序列化的类型
        解决 Pydantic 模型和自定义类型的JSON序列化问题
        """
        try:
            # 如果对象有 model_dump 方法 (Pydantic v2+)
            if hasattr(obj, 'model_dump'):
                return obj.model_dump()
            # 如果对象有 dict 方法 (Pydantic v1)
            elif hasattr(obj, 'dict'):
                return obj.dict()
            # 如果对象是字典，递归处理其值
            elif isinstance(obj, dict):
                return {k: self._make_serializable(v) for k, v in obj.items()}
            # 如果对象是列表，递归处理其元素
            elif isinstance(obj, list):
                return [self._make_serializable(item) for item in obj]
            # 基本类型直接返回
            elif isinstance(obj, (str, int, float, bool, type(None))):
                return obj
            # 其他类型尝试转为字符串
            else:
                return str(obj)
        except Exception as e:
            # 如果无法序列化，返回错误信息
            return f"<不可序列化对象: {type(obj).__name__}, 错误: {str(e)}>"
    
    def get_events(self, session_id: str) -> Optional[Dict[str, Any]]:
        """从队列中获取事件"""
        if session_id not in self.event_queues:
            return None
        
        try:
            # 非阻塞获取
            event = self.event_queues[session_id].get_nowait()
            return event
        except Exception:
            return None

    def cleanup_resources(self, session_id: str) -> bool:
        """清理任务相关资源但保留会话"""
        if session_id not in self.agent_instances:
            return False
        
        try:
            agent = self.agent_instances[session_id]
            
            # 关闭所有模型客户端连接
            # 关闭主模型客户端
            try:
                if hasattr(agent.model, 'client'):
                    if hasattr(agent.model.client, 'close'):
                        agent.model.client.close()
                    # 替换客户端对象，防止后续使用
                    agent.model.client = MockClient()
            except Exception as e:
                print(f"关闭主模型客户端失败: {e}")
            
            # 关闭元数据提取模型客户端
            try:
                if hasattr(agent.metadata_extract_agent, 'model') and hasattr(agent.metadata_extract_agent.model, 'client'):
                    if hasattr(agent.metadata_extract_agent.model.client, 'close'):
                        agent.metadata_extract_agent.model.client.close()
                    agent.metadata_extract_agent.model.client = MockClient()
            except Exception as e:
                print(f"关闭元数据提取模型客户端失败: {e}")
            
            # 关闭搜索模型客户端
            try:
                if hasattr(agent.search_agent, 'model') and hasattr(agent.search_agent.model, 'client'):
                    if hasattr(agent.search_agent.model.client, 'close'):
                        agent.search_agent.model.client.close()
                    agent.search_agent.model.client = MockClient()
            except Exception as e:
                print(f"关闭搜索模型客户端失败: {e}")
            
            print(f"Successfully cleaned up resources for session {session_id} while keeping the session.")
            return True
        
        except Exception as e:
            print(f"Error cleaning up resources: {e}")
            print(traceback.format_exc())
            return False

# 创建全局的服务实例
agent_service = AgentService()
