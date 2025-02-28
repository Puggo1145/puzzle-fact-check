from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import GenerationChunk, ChatGenerationChunk
from typing import Optional, Union, Any, Dict, List
import json
from datetime import datetime


class ReasonerStreamingCallback(BaseCallbackHandler):
    def __init__(self):
        self.has_thinking_started = False
        self.has_content_started = False
        # ANSI escape code for gray color
        self.gray_color = "\033[90m"
        self.reset_color = "\033[0m"

    def on_llm_new_token(
        self,
        token: str,
        *,
        chunk: Optional[Union[GenerationChunk, ChatGenerationChunk]] = None,
        **kwargs: Any,
    ):
        """Run on new LLM token. Only available when streaming is enabled."""

        if "reasoning_content" in chunk.message.additional_kwargs:  # type: ignore
            # Reasoning Content Flag
            if not self.has_thinking_started:
                print("THINKING: \n")
                self.has_thinking_started = True

            print(f"{self.gray_color}{chunk.message.additional_kwargs['reasoning_content']}{self.reset_color}", end="", flush=True)  # type: ignore
        elif chunk.message.content:  # type: ignore
            # Content Flag
            if not self.has_content_started:
                print("\n CONTENT: ", "\n")
                self.has_content_started = True

            print(chunk.message.content, end="", flush=True)  # type: ignore


class NormalStreamingCallback(BaseCallbackHandler):
    def __init__(self):
        self.has_content_started = False

    def on_llm_new_token(
        self,
        token: str,
        **kwargs: Any,
    ):
        """Run on new LLM token. Only available when streaming is enabled."""

        if not self.has_content_started:
            print("\n CONTENT: ", "\n")
            self.has_content_started = True

        print(token, end="", flush=True)


class AgentStateCallback(BaseCallbackHandler):
    """
    回调处理器，用于跟踪和显示 Agent 执行过程中的状态变化
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
        self.last_tokens = 0  # 记录上次的token消耗
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

    def on_agent_action(self, action, **kwargs: Any) -> Any:
        """当 Agent 执行动作时调用"""
        if not self.verbose:
            return

        self.step_count += 1

        self._print_colored(f"\n📋 步骤 {self.step_count}: 执行动作", "yellow", True)
        self._print_colored(f"🔧 工具: {action.tool}", "yellow")
        self._print_colored(f"📝 输入参数:", "yellow")
        self._print_colored(self._format_json(action.tool_input), "yellow")
        self._print_colored(f"{'-'*50}", "yellow")

    def on_agent_finish(self, finish, **kwargs: Any) -> Any:
        """当 Agent 完成执行时调用"""
        if not self.verbose:
            return

        self._print_colored(f"\n🏁 Agent 执行完成", "green", True)
        self._print_colored(f"📊 最终输出:", "green")
        self._print_colored(self._format_json(finish.return_values), "green")
        self._print_colored(f"{'-'*50}", "green")

        # 显示最终token消耗
        if "total_tokens" in finish.return_values:
            total_tokens = finish.return_values["total_tokens"]
            cost_estimate = total_tokens * 0.001 / 1000  # 假设每1K tokens约$0.001
            self._print_colored(
                f"💰 Token消耗: {total_tokens} (估计成本: ${cost_estimate:.4f})",
                "green",
                True,
            )

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        """当工具开始执行时调用"""
        if not self.verbose:
            return

        tool_name = serialized.get("name", "Unknown Tool")
        self._print_colored(f"\n🔨 开始执行工具: {tool_name}", "purple")
        self._print_colored(f"📥 输入: {input_str}", "purple")

    def on_tool_error(self, error: BaseException, **kwargs: Any) -> None:
        """当工具执行出错时调用"""
        if not self.verbose:
            return

        self._print_colored(f"\n❌ 工具执行错误:", "red", True)
        self._print_colored(f"{str(error)}", "red")
        self._print_colored(f"{'-'*50}", "red")

    def on_text(self, text: str, **kwargs: Any) -> None:
        """当有文本输出时调用"""
        if not self.verbose:
            return

        self._print_colored(f"\n💬 文本输出:", "blue")
        self._print_colored(text, "blue")

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """当LLM开始生成时调用"""
        if not self.verbose:
            return

        self.step_count += 1  # 增加步骤计数
        self.llm_call_count += 1  # 增加LLM调用计数

        model_name = serialized.get("name", "Unknown Model")
        self._print_colored(
            f"\n🧠 LLM 开始生成 (步骤 {self.step_count}, {model_name})", "purple", True
        )
        # 如果需要查看提示词，可以取消下面的注释
        # self._print_colored(f"提示词: {prompts}", "purple")

    def on_llm_end(self, response, **kwargs: Any) -> None:
        """当LLM生成结束时调用"""
        if not self.verbose:
            return

        self._print_colored(f"✨ LLM 生成完成", "green", True)

        # 打印模型输出内容
        if hasattr(response, "generations") and response.generations:
            for _, generation in enumerate(response.generations):
                if generation:
                    for g_idx, g in enumerate(generation):
                        if hasattr(g, "message") and g.message:
                            self._print_colored(
                                f"\n📝 模型输出 #{self.llm_call_count}.{g_idx}:",
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
        """优化打印格式，使用emoji分行，所有字段在一行显示"""
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
            self._print_colored(f"📄 内容: {json.dumps(content, ensure_ascii=False)}", "cyan")

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
            # 添加更多字段和对应的emoji
        }
        return emoji_map.get(key, "📌")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """当链结束执行时调用，用于显示token消耗"""
        if not self.verbose:
            return

        # 检查是否有token消耗信息
        if "total_tokens" in outputs:
            current_tokens = outputs["total_tokens"]
            tokens_used = current_tokens - self.last_tokens

            # 只有当token消耗有变化时才显示统计信息
            if tokens_used > 0:
                self.last_tokens = current_tokens

                self._print_colored(
                    f"\n📊 Token消耗统计 (步骤 {self.step_count}):", "blue", True
                )
                self._print_colored(f"   本次消耗: {tokens_used} tokens", "blue")
                self._print_colored(f"   累计消耗: {current_tokens} tokens", "blue")
                self._print_colored(f"{'-'*50}", "blue")
