import json
from typing import Any, Dict, List
from langchain_core.callbacks import BaseCallbackHandler


class AgentStateCallback(BaseCallbackHandler):
    """
    Callback function，用于跟踪和显示 Search Agent 执行过程中的状态变化
    """

    def __init__(self):
        """
        初始化回调处理器

        Args:
            verbose: 是否显示详细信息
        """
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
        
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
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
        
    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        tool_name = serialized.get("name", "Unknown Tool")
        self._print_colored(f"\n🔨 开始执行工具: {tool_name}", "purple")
        self._print_colored(f"📥 输入: {input_str}", "purple")

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        self._print_colored(f"📤 工具执行结果:", "green")
        # 如果输出太长，截断显示
        if len(output) > 500:
            self._print_colored(f"{output[:497]}...", "green")
        else:
            self._print_colored(output, "green")

    def on_tool_error(self, error: BaseException, **kwargs: Any) -> None:
        self._print_colored(f"\n❌ 工具执行错误:", "red", True)
        self._print_colored(f"{str(error)}", "red")
        self._print_colored(f"{'-'*50}", "red")

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """当LLM开始生成时调用"""
        self.llm_call_count += 1  # 增加LLM调用计数

        model_name = serialized.get("name", "Unknown Model")
        self._print_colored(
            f"🧠 LLM 开始生成 (调用 #{self.llm_call_count}, {model_name})",
            "purple",
            True,
        )
        # 如果需要查看提示词，可以取消下面的注释
        # self._print_colored(f"提示词: {prompts}", "purple")

    def on_llm_end(self, response, **kwargs: Any) -> None:
        """当LLM生成结束时调用"""
        # 打印模型输出内容
        if hasattr(response, "generations") and response.generations:
            for _, generation in enumerate(response.generations):
                if generation:
                    for g_idx, g in enumerate(generation):
                        if hasattr(g, "message") and g.message:
                            self._print_colored(
                                f"LLM 输出 #{self.llm_call_count}.{g_idx}:",
                                "cyan",
                                True,
                            )
                            content = (
                                g.message.content
                                if hasattr(g.message, "content")
                                else str(g.message)
                            )

                            # 尝试解析JSON格式的输出
                            try:
                                parsed_content = json.loads(content)
                                # 优化打印格式，使用emoji分行
                                self._print_formatted_output(parsed_content)
                            except:
                                self._print_colored(content, "cyan")
                                
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
                        # 对于复杂对象，转换为紧凑的单行JSON
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
            self._print_colored(
                f"📄 内容: {json.dumps(content, ensure_ascii=False)}", "cyan"
            )

    def _get_emoji_for_key(self, key):
        """为不同类型的字段选择合适的emoji"""
        emoji_map = {
            "evaluation": "🔍",
            "memory": "🧠",
            "next_step": "👣",
            "action": "🛠️",
            "new_evidence": "📋",
            "summary": "📊",
            "conclusion": "🏁",
            "sources": "📚",
            "confidence": "⭐",
            "content": "📝",
            "source": "🔗",
            "relevance": "🎯",
            # 添加更多字段和对应的emoji
        }
        return emoji_map.get(key, "📌")
