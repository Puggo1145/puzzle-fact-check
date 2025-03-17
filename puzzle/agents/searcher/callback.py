import json
from typing import Any, Dict, List
from ..base import BaseAgentCallback
from .prompts import evaluate_current_status_output_parser, generate_answer_output_parser


class CLIModeCallback(BaseAgentCallback):
    """
    Search Agent CLI Mode 回调，主要用于在 terminal 显示 LLM 的推理过程
    """

    def __init__(self):
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
        
        # 处理不同类型的输出
        try:
            # 如果是字符串类型，检查长度并可能截断
            if isinstance(output, str):
                if len(output) > 500:
                    self._print_colored(f"{output[:497]}...", "green")
                else:
                    self._print_colored(output, "green")
            else:
                # 处理非字符串类型
                self._print_colored(str(output), "green")
        except Exception as e:
            # 捕获任何错误，确保回调不会中断主程序
            self._print_colored(f"输出处理错误: {str(e)}", "red")

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
        
        # 根据当前节点显示不同的开始信息
        if self.current_node == "evaluate_current_status":
            self._print_colored(
                f"🧠 LLM 开始评估当前状态 (调用 #{self.llm_call_count}, {model_name})",
                "purple",
                True,
            )
        elif self.current_node == "generate_answer":
            self._print_colored(
                f"🧠 LLM 开始生成检索结论 (调用 #{self.llm_call_count}, {model_name})",
                "green",
                True,
            )
        else:
            self._print_colored(
                f"🧠 LLM 开始生成 (调用 #{self.llm_call_count}, {model_name})",
                "purple",
                True,
            )
        # 如果需要查看提示词，可以取消下面的注释
        # self._print_colored(f"提示词: {prompts}", "purple")

    def on_llm_end(self, response, **kwargs: Any) -> None:
        """当LLM生成结束时调用"""
        # 控制台格式化输出
        self._print_colored("LLM 输出:", "cyan", True)
        
        # 根据当前节点处理不同的输出
        if not hasattr(response, "generations") or not response.generations:
            return
            
        for _, generation in enumerate(response.generations):
            if generation:
                for g_idx, g in enumerate(generation):
                    if hasattr(g, "message") and g.message:
                        content = (
                            g.message.content
                            if hasattr(g.message, "content")
                            else str(g.message)
                        )
                        
                        if self.current_node == "evaluate_current_status":
                            try:
                                parsed_result = evaluate_current_status_output_parser.parse(content)
                                self._print_status_evaluation(parsed_result)
                            except Exception as e:
                                self._print_colored(f"解析状态评估失败: {str(e)}", "red")
                                self._print_colored(content, "cyan")
                        elif self.current_node == "generate_answer":
                            try:
                                parsed_result = generate_answer_output_parser.parse(content)
                                self._print_search_result(parsed_result)
                            except Exception as e:
                                self._print_colored(f"解析核查结论失败: {str(e)}", "red")
                                self._print_colored(content, "cyan")
                        else:
                            # 默认情况下直接打印输出
                            self._print_colored(content, "cyan")
                                
    def _print_status_evaluation(self, status):
        """打印状态评估信息"""
        # 打印评估结果
        self._print_colored("\n🔍 评估反思:", "yellow", True)
        
        # 打印评估
        if hasattr(status, "evaluation") and status.evaluation:
            self._print_colored(f"📊 评估: {status.evaluation}", "yellow")
            
        # 打印缺失信息
        if hasattr(status, "missing_information") and status.missing_information:
            self._print_colored(f"❓ 缺失信息: {status.missing_information}", "red", True)
        
        # 打印记忆
        if hasattr(status, "memory") and status.memory:
            self._print_colored(f"🧠 记忆: {status.memory}", "yellow")
        
        # 打印下一步
        if hasattr(status, "next_step") and status.next_step:
            self._print_colored(f"👣 下一步: {status.next_step}", "yellow")
        
        # 打印动作
        if hasattr(status, "action") and status.action:
            # 处理不同类型的action
            if status.action == "answer":
                self._print_colored(f"🛠️ 行动: 生成回答", "yellow", True)
            elif isinstance(status.action, list):
                # 处理工具调用列表
                for i, tool_call in enumerate(status.action):
                    tool_name = tool_call.get("name", "未知工具") if isinstance(tool_call, dict) else str(tool_call)
                    self._print_colored(f"🛠️ 行动 #{i+1}: {tool_name}", "yellow", True)
                    
                    # 如果是字典且有args字段
                    if isinstance(tool_call, dict) and "args" in tool_call:
                        args_str = json.dumps(tool_call["args"], ensure_ascii=False)
                        self._print_colored(f" {args_str}", "yellow")
            else:
                # 处理其他情况
                self._print_colored(f"🛠️ 行动: {str(status.action)}", "yellow", True)
        
        # 打印新证据
        if hasattr(status, "new_evidence") and status.new_evidence:
            self._print_colored(f"📋 新证据:", "green", True)
            for evidence in status.new_evidence:
                self._print_colored(f"  • {evidence.content}", "green")
                self._print_colored(f"  • {evidence.source}", "green")
                self._print_colored(f"  • {evidence.reasoning}", "green")
                self._print_colored(f"  • {evidence.relationship}", "green")
    
    def _print_search_result(self, result):
        """打印搜索结果信息"""
        self._print_colored("\n🏁 核查结论:", "green", True)
        
        # 打印摘要
        if hasattr(result, "summary") and result.summary:
            self._print_colored(f"📊 摘要: {result.summary}", "green")
        
        # 打印结论
        if hasattr(result, "conclusion") and result.conclusion:
            self._print_colored(f"🏁 结论: {result.conclusion}", "green", True)
        
        # 打印来源
        if hasattr(result, "sources") and result.sources:
            self._print_colored(f"📚 来源:", "cyan", True)
            for source in result.sources:
                self._print_colored(f"  • {source}", "cyan")
        
        # 打印置信度
        if hasattr(result, "confidence") and result.confidence:
            self._print_colored(f"⭐ 置信度: {result.confidence}", "cyan", True)
