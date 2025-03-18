import json
from ..base import (
    BaseAgentCallback, 
    NodeEventTiming, 
    OnChainStartContext,
    OnChainEndContext,
    OnToolStartContext,
    OnToolEndContext,
    OnToolErrorContext,
    OnLLMStartContext,
    OnLLMEndContext,
)
from .prompts import evaluate_current_status_output_parser, generate_answer_output_parser
from .states import SearchAgentState
from db import db_integration
from typing import cast, Optional


class DBIntegrationCallback(BaseAgentCallback):
    def __init__(self):
        super().__init__()
        
        self.current_retrieval_step_purpose: Optional[str] = None
        
        # 保存当前 retrieval step purpose，方便匹配对应的 node
        @self.node_event(node_name="__start__", timing=NodeEventTiming.ON_CHAIN_START)
        def store_news_text_to_db(context: OnChainStartContext):
            inputs = cast(SearchAgentState, context["inputs"])
            self.current_retrieval_step_purpose = inputs.purpose
        
        @self.node_event(node_name="evaluate_current_status", timing=NodeEventTiming.ON_CHAIN_END)
        def store_search_evidences_to_db(context: OnChainEndContext):
            if not self.current_retrieval_step_purpose:
                raise ValueError("Current retrieval step purpose is not set.")
            
            outputs = context["outputs"]
            if not outputs.get("evidences"): # 检索过程中可能没有检索到新证据
                return
            db_integration.store_search_evidences(self.current_retrieval_step_purpose, outputs["evidences"])
            
        @self.node_event(node_name="generate_answer", timing=NodeEventTiming.ON_CHAIN_END)
        def store_search_result_to_db(context: OnChainEndContext) -> None:
            if not self.current_retrieval_step_purpose:
                raise ValueError("Current retrieval step purpose is not set.")
            
            outputs = context["outputs"]
            db_integration.store_search_results(self.current_retrieval_step_purpose, outputs["result"])
    

class CLIModeCallback(BaseAgentCallback):
    """
    Search Agent CLI Mode 回调，主要用于在 terminal 显示 LLM 的推理过程
    """

    def __init__(self):
        super().__init__()
        
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
        
        self.handle_chain_end()
        self.handle_tools()
        self.print_llm_start_info()
        self.print_llm_results()

    def _print_colored(self, text, color="blue", bold=False):
        prefix = ""
        if bold:
            prefix += self.colors["bold"]

        if color in self.colors:
            prefix += self.colors[color]

        print(f"{prefix}{text}{self.colors['reset']}")

    def _format_json(self, data):
        if isinstance(data, str):
            try:
                parsed_data = json.loads(data)
                return json.dumps(parsed_data, indent=2, ensure_ascii=False)
            except:
                return data
        elif isinstance(data, (dict, list)):
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            return str(data)
    
    def handle_chain_end(self):
        @self.node_event(timing=NodeEventTiming.ON_CHAIN_END)
        def track_token_usage(context: OnChainEndContext):
            outputs = context["outputs"]
            if "token_usage" in outputs:
                current_tokens = int(outputs["token_usage"])
                tokens_used = current_tokens - self.last_tokens

                # 只有当token消耗有变化时才显示统计信息
                if tokens_used > 0:
                    self.last_tokens = current_tokens

                    self._print_colored(f"\n📊 Token消耗统计: ", "blue", True)
                    self._print_colored(f"   本次消耗: {tokens_used} tokens", "blue")
                    self._print_colored(f"   累计消耗: {current_tokens} tokens", "blue")
                    self._print_colored(f"{'-'*50}", "blue")
        
    def handle_tools(self):
        @self.node_event(timing=NodeEventTiming.ON_TOOL_START)
        def print_tool_start(context: OnToolStartContext):

            tool_name = context["serialized"].get("name", "Unknown Tool")
            self._print_colored(f"\n🔨 开始执行工具: {tool_name}", "purple")
            self._print_colored(f"📥 输入: {context['input_str']}", "purple")

        @self.node_event(timing=NodeEventTiming.ON_TOOL_END)
        def print_tool_result(context: OnToolEndContext):
            output = context["output"]
            
            self._print_colored(f"\n📤 工具执行结果:", "green")
            
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

        @self.node_event(timing=NodeEventTiming.ON_TOOL_ERROR)
        def print_tool_error(context: OnToolErrorContext):
            error = context["error"]
            
            self._print_colored(f"\n❌ 工具执行错误:", "red", True)
            self._print_colored(f"{str(error)}", "red")
            self._print_colored(f"{'-'*50}", "red")

    def print_llm_start_info(self):
        @self.node_event(node_name="evaluate_current_status", timing=NodeEventTiming.ON_LLM_START)
        def print_evaluate_status_start(context: OnLLMStartContext):
            self.llm_call_count += 1
            model_name = context["serialized"]["name"]
            self._print_colored(
                f"\n🧠 LLM 开始评估当前状态 (调用 #{self.llm_call_count}, {model_name})",
                "purple",
                True,
            )
        
        @self.node_event(node_name="generate_answer", timing=NodeEventTiming.ON_LLM_START)
        def print_generate_answer_start(context: OnLLMStartContext):
            model_name = context["serialized"]["name"]
            self.llm_call_count += 1
            self._print_colored(
                f"\n🧠 LLM 开始生成检索结论 (调用 #{self.llm_call_count}, {model_name})",
                "green",
                True,
            )
        
    def print_llm_results(self):
        @self.node_event(node_name="evaluate_current_status", timing=NodeEventTiming.ON_LLM_END)
        def print_status_evaluation_end(context: OnLLMEndContext):
            generated_text = context["response"].generations[0][0].text
            try:
                parsed_result = evaluate_current_status_output_parser.parse(generated_text)
                self._print_status_evaluation(parsed_result)
            except Exception as e:
                self._print_colored(f"解析状态评估失败: {str(e)}", "red")
                self._print_colored(generated_text, "cyan")
        
        @self.node_event(node_name="generate_answer", timing=NodeEventTiming.ON_LLM_END)
        def print_generate_answer_end(context: OnLLMEndContext):
            generated_text = context["response"].generations[0][0].text
            try:
                parsed_result = generate_answer_output_parser.parse(generated_text)
                self._print_search_result(parsed_result)
            except Exception as e:
                self._print_colored(f"解析核查结论失败: {str(e)}", "red")
                self._print_colored(generated_text, "cyan")
        
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
