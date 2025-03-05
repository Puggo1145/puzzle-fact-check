import json
from typing import Any, Dict, List, Optional, Sequence
from uuid import UUID
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.documents import Document
from langchain_core.agents import AgentAction
from langchain_core.outputs import LLMResult


class MetadataExtractorCallback(BaseCallbackHandler):
    """
    Callback function，用于跟踪和显示 Metadata Extractor Agent 执行过程中的状态变化
    """

    def __init__(self, verbose=True):
        """
        初始化回调处理器

        Args:
            verbose: 是否显示详细信息
        """
        self.verbose = verbose
        self.step_count = 0  # 总步骤计数
        self.llm_call_count = 0  # LLM调用计数
        self.start_time = None
        self.last_tokens = 0
        # ANSI 颜色代码
        self.colors = {
            "blue": "\033[94m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "red": "\033[91m",
            "purple": "\033[95m",
            "cyan": "\033[96m",
            "bold": "\033[1m",
            "reset": "\033[0m",
        }

    def _print_colored(self, text, color="blue", bold=False):
        """打印彩色文本"""
        if not self.verbose:
            return

        prefix = ""
        if bold:
            prefix += self.colors["bold"]

        if color in self.colors:
            prefix += self.colors[color]

        print(f"{prefix}{text}{self.colors['reset']}")

    def _format_json(self, data):
        """格式化 JSON 数据为可读字符串"""
        if isinstance(data, str):
            try:
                # 尝试解析 JSON 字符串
                parsed_data = json.loads(data)
                return json.dumps(parsed_data, indent=2, ensure_ascii=False)
            except:
                return data
        elif isinstance(data, (dict, list)):
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            return str(data)
        
    def on_chain_end(self, outputs, **kwargs):
        if not self.verbose:
            return

        # 检查outputs是否为布尔值或不是字典
        if not isinstance(outputs, dict):
            return

        # 统计 token 消耗
        if "token_usage" in outputs:
            current_tokens = int(outputs["token_usage"])
            tokens_used = current_tokens - self.last_tokens

            # 只有当token消耗有变化时才显示统计信息
            if tokens_used > 0:
                self.last_tokens = current_tokens

                self._print_colored(
                    f"\n📊 Token消耗统计: ", "blue", True
                )
                self._print_colored(f"   本次消耗: {tokens_used} tokens", "blue")
                self._print_colored(f"   累计消耗: {current_tokens} tokens", "blue")
                self._print_colored(f"{'-'*50}", "blue")
    
    def on_agent_action(
        self, 
        action: AgentAction, 
        *, 
        run_id: UUID, 
        parent_run_id: Optional[UUID] = None, 
        **kwargs: Any
    ) -> Any:
        """当Agent执行动作时调用"""
        if not self.verbose:
            return
        
        self.step_count += 1
        action_name = action.tool if hasattr(action, "tool") else "Unknown Action"
        self._print_colored(f"\n🔄 执行动作 #{self.step_count}: {action_name}", "yellow", True)
        
        # 显示动作输入
        if hasattr(action, "tool_input"):
            input_str = (
                action.tool_input if isinstance(action.tool_input, str) 
                else self._format_json(action.tool_input)
            )
            self._print_colored(f"📥 输入: {input_str}", "yellow")
        
    def on_tool_start(self, serialized, input_str, **kwargs):
        if not self.verbose:
            return

        tool_name = serialized.get("name", "Unknown Tool")
        self._print_colored(f"\n🔨 开始执行工具: {tool_name}", "purple")
        self._print_colored(f"📥 输入: {input_str}", "purple")

    def on_tool_end(self, output, **kwargs):
        if not self.verbose:
            return

        self._print_colored(f"📤 工具执行结果:", "green")
        
        # 处理不同类型的输出
        try:
            # 如果是字符串类型，检查长度并可能截断
            if isinstance(output, str):
                if len(output) > 500:
                    self._print_colored(f"{output[:497]}...", "green")
                else:
                    self._print_colored(output, "green")
            # 处理ToolMessage或其他对象类型
            else:
                # 尝试获取内容属性
                if hasattr(output, "content"):
                    content = output.content
                    if isinstance(content, str) and len(content) > 500:
                        self._print_colored(f"{content[:497]}...", "green")
                    else:
                        self._print_colored(str(content), "green")
                else:
                    # 如果没有content属性，使用字符串表示
                    self._print_colored(str(output), "green")
        except Exception as e:
            # 捕获任何错误，确保回调不会中断主程序
            self._print_colored(f"输出处理错误: {str(e)}", "red")

    def on_tool_error(self, error, **kwargs):
        if not self.verbose:
            return

        self._print_colored(f"\n❌ 工具执行错误:", "red", True)
        self._print_colored(f"{str(error)}", "red")
        self._print_colored(f"{'-'*50}", "red")

    def on_llm_start(self, serialized, prompts, **kwargs):
        """当LLM开始生成时调用"""
        if not self.verbose:
            return

        self.llm_call_count += 1  # 增加LLM调用计数

        model_name = serialized.get("name", "Unknown Model")
        self._print_colored(
            f"\n🧠 LLM 开始生成 (调用 #{self.llm_call_count}, {model_name})",
            "purple",
            True,
        )
        # 如果需要查看提示词，可以取消下面的注释
        # self._print_colored(f"提示词: {prompts}", "purple")

    def on_llm_end(self, response, **kwargs):
        """当LLM生成结束时调用"""
        if not self.verbose:
            return

        # 打印模型输出内容
        if hasattr(response, "generations") and response.generations:
            for _, generation_list in enumerate(response.generations):
                if generation_list:
                    for g_idx, g in enumerate(generation_list):
                        self._print_colored(
                            f"LLM 输出 #{self.llm_call_count}.{g_idx}:",
                            "cyan",
                            True,
                        )
                        
                        # 获取生成内容，处理不同类型的生成对象
                        if hasattr(g, "text") and g.text:
                            content = g.text
                        elif hasattr(g, "message"):
                            if hasattr(g.message, "content"):
                                content = g.message.content
                            else:
                                content = str(g.message)
                        else:
                            content = str(g)

                        # 尝试解析JSON格式的输出
                        if isinstance(content, str):
                            try:
                                parsed_content = json.loads(content)
                                # 优化打印格式，使用emoji分行
                                self._print_formatted_output(parsed_content)
                            except (json.JSONDecodeError, TypeError):
                                self._print_colored(content, "cyan")
                        else:
                            self._print_colored(str(content), "cyan")
    
    def on_retriever_start(
        self, 
        serialized: Dict[str, Any], 
        query: str, 
        *, 
        run_id: UUID, 
        parent_run_id: Optional[UUID] = None, 
        tags: Optional[List[str]] = None, 
        metadata: Optional[Dict[str, Any]] = None, 
        **kwargs: Any
    ) -> None:
        """当检索开始时调用"""
        if not self.verbose:
            return
        
        self._print_colored(f"\n🔍 开始检索知识元", "yellow", True)
        self._print_colored(f"查询: {query}", "yellow")
    
    def on_retriever_end(
        self, 
        documents: Sequence[Document], 
        *, 
        run_id: UUID, 
        parent_run_id: Optional[UUID] = None, 
        **kwargs: Any
    ) -> None:
        """当检索结束时调用"""
        if not self.verbose:
            return
        
        self._print_colored(f"📚 检索到 {len(documents)} 条知识元", "green", True)
        for i, doc in enumerate(documents[:3]):  # 只显示前3条
            self._print_colored(f"知识元 #{i+1}: {str(doc)[:100]}...", "green")
        
        if len(documents) > 3:
            self._print_colored(f"... 还有 {len(documents)-3} 条知识元", "green")

    def _print_formatted_output(self, content):
        """优化打印格式，使用emoji分行"""
        if isinstance(content, dict):
            for key, value in content.items():
                # 为不同类型的字段选择不同的emoji
                emoji = self._get_emoji_for_key(key)

                # 将所有字段都压缩为单行显示
                if value is None:
                    self._print_colored(f"{emoji} {key}: None", "cyan")
                else:
                    # 根据值的类型选择不同的格式化方式
                    if isinstance(value, (dict, list)):
                        # 对于复杂对象，使用更友好的格式
                        if key == "items" and isinstance(value, list):
                            # 对于知识元列表，每个元素单独一行显示
                            self._print_colored(f"{emoji} {key}:", "cyan")
                            for i, item in enumerate(value):
                                if isinstance(item, dict):
                                    self._print_colored(f"  {i+1}. {item.get('term', '未知术语')} - {item.get('category', '未知类别')}", "cyan")
                                else:
                                    self._print_colored(f"  {i+1}. {str(item)}", "cyan")
                        elif key in ["who", "what", "when", "where", "why", "how"] and isinstance(value, list):
                            # 对于新闻要素，列表项分行显示
                            self._print_colored(f"{emoji} {key}:", "cyan")
                            for item in value:
                                self._print_colored(f"  • {item}", "cyan")
                        else:
                            # 其他复杂对象，转换为紧凑的单行JSON
                            compact_value = json.dumps(value, ensure_ascii=False)
                            # 如果太长，截断显示
                            if len(compact_value) > 100:
                                compact_value = compact_value[:97] + "..."
                            self._print_colored(f"{emoji} {key}: {compact_value}", "cyan")
                    else:
                        # 对于简单值，直接显示
                        str_value = str(value)
                        # 如果值太长，截断显示
                        if len(str_value) > 100:
                            str_value = str_value[:97] + "..."
                        self._print_colored(f"{emoji} {key}: {str_value}", "cyan")
        else:
            # 如果不是字典，直接打印
            try:
                # 尝试解析为JSON并格式化显示
                if isinstance(content, str):
                    parsed = json.loads(content)
                    self._print_formatted_output(parsed)
                else:
                    self._print_colored(f"📄 内容: {str(content)}", "cyan")
            except (json.JSONDecodeError, TypeError):
                self._print_colored(f"📄 内容: {str(content)}", "cyan")

    def _get_emoji_for_key(self, key):
        """为不同类型的字段选择合适的emoji"""
        emoji_map = {
            "basic_metadata": "📋",
            "knowledges": "🧩",
            "term": "📝",
            "category": "🏷️",
            "definition": "📚",
            "importance": "⭐",
            "source": "🔗",
            "retrieved_knowledges": "🔍",
            "news_text": "📰",
            "who": "👤",
            "what": "📌",
            "when": "🕒",
            "where": "📍",
            "why": "❓",
            "how": "🛠️",
            "news_type": "📰",
            # 添加更多字段和对应的emoji
        }
        return emoji_map.get(key, "📌")
