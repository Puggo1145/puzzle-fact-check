import json
import time
from typing import Any, Dict, List, Optional, Union, cast
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.outputs import ChatGenerationChunk, GenerationChunk, ChatGeneration
from .states import CheckPoints
from .prompts import fact_check_plan_output_parser


class PlanAgentCallback(BaseCallbackHandler):
    """
    Callback handler for PlanAgent to track and display the agent's reasoning process,
    output tokens, and planning results during execution.
    """

    def __init__(self, verbose=True):
        """
        Initialize the callback handler

        Args:
            verbose: Whether to display detailed information
        """
        self.verbose = verbose
        self.step_count = 0
        self.llm_call_count = 0
        self.start_time = None
        self.token_usage = 0
        self.has_thinking_started = False
        self.has_content_started = False

        # ANSI color codes
        self.colors = {
            "blue": "\033[94m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "red": "\033[91m",
            "purple": "\033[95m",
            "cyan": "\033[96m",
            "gray": "\033[90m",
            "bold": "\033[1m",
            "reset": "\033[0m",
        }

    def _print_colored(self, text, color="blue", bold=False):
        """Print colored text"""
        if not self.verbose:
            return

        prefix = ""
        if bold:
            prefix += self.colors["bold"]

        if color in self.colors:
            prefix += self.colors[color]

        print(f"{prefix}{text}{self.colors['reset']}")

    def _format_json(self, data):
        """Format JSON data as readable string"""
        if isinstance(data, str):
            try:
                # Try to parse JSON string
                parsed_data = json.loads(data)
                return json.dumps(parsed_data, indent=2, ensure_ascii=False)
            except:
                return data
        elif isinstance(data, (dict, list)):
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            return str(data)

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Called when LLM starts generating"""
        if not self.verbose:
            return

        try:
            self.llm_call_count += 1
            self.start_time = time.time()
            self.has_thinking_started = False
            self.has_content_started = False

            model_name = "Unknown Model"
            if serialized is not None and isinstance(serialized, dict):
                model_name = serialized.get("name", "Unknown Model")

            self._print_colored(
                f"\n🧠 LLM 开始推理 (调用 #{self.llm_call_count}, {model_name})",
                "purple",
                True,
            )
        except Exception as e:
            self._print_colored(f"Error in on_llm_start: {str(e)}", "red")

    def on_llm_new_token(
        self,
        token: str,
        *,
        chunk: Optional[Union[GenerationChunk, ChatGenerationChunk]] = None,
        **kwargs: Any,
    ) -> None:
        """Process streaming tokens from LLM, handling reasoning and content separately"""
        if not self.verbose:
            return

        try:
            if chunk is None:
                print(token, end="", flush=True)
                return

            chunk_message = cast(ChatGenerationChunk, chunk).message
            # Handle reasoning content (thinking process)
            if hasattr(chunk, "message") and hasattr(
                chunk_message, "additional_kwargs"
            ):
                if "reasoning_content" in chunk_message.additional_kwargs:
                    if not self.has_thinking_started:
                        self._print_colored("💭 思考:", "gray", True)
                        self.has_thinking_started = True

                    reasoning = chunk_message.additional_kwargs["reasoning_content"]
                    print(
                        f"{self.colors['gray']}{reasoning}{self.colors['reset']}",
                        end="",
                        flush=True,
                    )

                # Handle regular content (final output)
                elif hasattr(chunk_message, "content") and chunk_message.content:
                    if not self.has_content_started:
                        self._print_colored(
                            "\n🔄 思考完成，LLM 正在规划核查方案...", "cyan", True
                        )
                        self.has_content_started = True
            else:
                # Fallback for simple token streaming
                print(token, end="", flush=True)
        except Exception as e:
            self._print_colored(f"Error in on_llm_new_token: {str(e)}", "red")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Called when LLM generation ends"""
        if not self.verbose:
            return

        try:
            # 生成耗时
            if self.start_time:
                generation_time = time.time() - self.start_time
                self._print_colored(f"\n⏱️ 推理耗时: {generation_time:.2f}秒", "blue")

            # 控制台格式化输出
            self._print_colored("\n📋 规划结果:", "cyan", True)

            parsed_result = fact_check_plan_output_parser.parse(
                response.generations[0][0].text
            )
            check_points = parsed_result["check_points"]
            selected_check_points = [
                check_point
                for check_point in check_points
                if check_point["is_verification_point"]
            ]
            for check_point in selected_check_points:
                print(f"\n第 {check_point['id']} 条陈述")
                print(f"陈述内容：{check_point['content']}")
                print(f"核查理由：{check_point['importance']}")
                if isinstance(check_point["retrieval_plan"], list):
                    for idx, plan in enumerate(check_point["retrieval_plan"]):
                        print(f"核查计划 {idx+1}：")
                        print(f"- 核查目标：{plan['purpose']}")
                        print(f"- 目标信源类型：{plan['expected_sources']}")

        except Exception as e:
            self._print_colored(f"Error in on_llm_end: {str(e)}", "red")

    def _print_formatted_plan(self, plan_data):
        """Format and print the planning results with appropriate emojis"""
        try:
            if not isinstance(plan_data, dict):
                self._print_colored(str(plan_data), "cyan")
                return

            # Print check points
            if "check_points" in plan_data and isinstance(
                plan_data["check_points"], list
            ):
                for i, point in enumerate(plan_data["check_points"]):
                    is_verification = point.get("is_verification_point", False)
                    emoji = "🔍" if is_verification else "📌"

                    self._print_colored(
                        f"\n{emoji} 陈述 #{point.get('id', i+1)}: {point.get('content', '无内容')}",
                        "cyan",
                        is_verification,
                    )

                    if is_verification:
                        if "importance" in point and point["importance"]:
                            self._print_colored(
                                f"⭐ 重要性: {point['importance']}", "cyan"
                            )

                        if "retrieval_plan" in point and point["retrieval_plan"]:
                            self._print_colored(f"🔎 检索方案:", "cyan")
                            for j, step in enumerate(point["retrieval_plan"]):
                                self._print_colored(
                                    f"  {j+1}. 目的: {step.get('purpose', '无目的')}",
                                    "cyan",
                                )
                                if (
                                    "expected_sources" in step
                                    and step["expected_sources"]
                                ):
                                    sources = ", ".join(step["expected_sources"])
                                    self._print_colored(
                                        f"     预期来源: {sources}", "cyan"
                                    )
        except Exception as e:
            self._print_colored(f"Error in _print_formatted_plan: {str(e)}", "red")

    def on_agent_action(self, action, **kwargs: Any) -> Any:
        """Called when agent takes an action"""
        if not self.verbose:
            return

        try:
            self._print_colored(f"\n🛠️ 执行动作: {action.tool}", "purple", True)
            self._print_colored(f"📥 输入: {action.tool_input}", "purple")
        except Exception as e:
            self._print_colored(f"Error in on_agent_action: {str(e)}", "red")

    def on_agent_finish(self, finish, **kwargs: Any) -> None:
        """Called when agent finishes"""
        if not self.verbose:
            return

        try:
            self._print_colored(f"\n✅ 代理完成: {finish.return_values}", "green", True)
        except Exception as e:
            self._print_colored(f"Error in on_agent_finish: {str(e)}", "red")

    def on_tool_error(self, error: BaseException, **kwargs: Any) -> None:
        """Called when a tool errors"""
        if not self.verbose:
            return

        try:
            self._print_colored(f"\n❌ 工具执行错误:", "red", True)
            self._print_colored(f"{str(error)}", "red")
            self._print_colored(f"{'-'*50}", "red")
        except Exception as e:
            self._print_colored(f"Error in on_tool_error: {str(e)}", "red")
