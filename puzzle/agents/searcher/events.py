import json
from enum import Enum
from pubsub import pub
from db import db_integration
from .states import SearchResult

class SearchAgentEvents(Enum):
    # DB 相关事件
    STORE_CHECK_POINT = "searcher.store_check_point"
    STORE_SEARCH_EVIDENCES = "searcher.store_search_evidences"
    STORE_SEARCH_RESULT = "searcher.store_search_result"
    
    # CLI 显示相关事件
    PRINT_SEARCH_AGENT_START = "searcher.print_search_agent_start"
    PRINT_TOKEN_USAGE = "searcher.print_token_usage"
    PRINT_TOOL_START = "searcher.print_tool_start"
    PRINT_TOOL_RESULT = "searcher.print_tool_result"
    PRINT_TOOL_ERROR = "searcher.print_tool_error"
    PRINT_EVALUATE_STATUS_START = "searcher.print_evaluate_status_start"
    PRINT_GENERATE_ANSWER_START = "searcher.print_generate_answer_start"
    PRINT_STATUS_EVALUATION_END = "searcher.print_status_evaluation_end"
    PRINT_GENERATE_ANSWER_END = "searcher.print_generate_answer_end"


class DBEvents:
    """
    DB Integration 回调，将搜索结果存储到数据库
    """

    def __init__(self):
        self.setup_subscribers()
        self.current_retrieval_step_purpose = None

    def setup_subscribers(self):
        # Subscribe to events
        pub.subscribe(
            self.store_check_point,
            SearchAgentEvents.STORE_CHECK_POINT.value,
        )
        pub.subscribe(
            self.store_search_evidences,
            SearchAgentEvents.STORE_SEARCH_EVIDENCES.value,
        )
        pub.subscribe(
            self.store_search_result,
            SearchAgentEvents.STORE_SEARCH_RESULT.value,
        )

    def store_check_point(self, content: str, purpose: str, expected_sources: list[str]) -> None:
        db_integration.store_check_point(content, purpose, expected_sources)
        self.current_retrieval_step_purpose = purpose

    def store_search_evidences(self, evidences: list) -> None:
        if not self.current_retrieval_step_purpose:
            raise ValueError("Current retrieval step purpose is not set.")
        
        if not evidences or len(evidences) == 0:
            return
        
        db_integration.store_search_evidences(self.current_retrieval_step_purpose, evidences)

    def store_search_result(self, result: SearchResult) -> None:
        if not self.current_retrieval_step_purpose:
            raise ValueError("Current retrieval step purpose is not set.")
        
        db_integration.store_search_results(self.current_retrieval_step_purpose, result)


class CLIModeEvents:
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
        
        self.setup_subscribers()

    def setup_subscribers(self):
        # Chain events
        pub.subscribe(
            self.print_search_agent_start,
            SearchAgentEvents.PRINT_SEARCH_AGENT_START.value,
        )
        pub.subscribe(
            self.track_token_usage,
            SearchAgentEvents.PRINT_TOKEN_USAGE.value,
        )
        
        # Tool events
        pub.subscribe(
            self.print_tool_start,
            SearchAgentEvents.PRINT_TOOL_START.value,
        )
        pub.subscribe(
            self.print_tool_result,
            SearchAgentEvents.PRINT_TOOL_RESULT.value,
        )
        pub.subscribe(
            self.print_tool_error,
            SearchAgentEvents.PRINT_TOOL_ERROR.value,
        )
        
        # LLM events
        pub.subscribe(
            self.print_evaluate_status_start,
            SearchAgentEvents.PRINT_EVALUATE_STATUS_START.value,
        )
        pub.subscribe(
            self.print_status_evaluation_end,
            SearchAgentEvents.PRINT_STATUS_EVALUATION_END.value,
        )
        pub.subscribe(
            self.print_generate_answer_start,
            SearchAgentEvents.PRINT_GENERATE_ANSWER_START.value,
        )
        pub.subscribe(
            self.print_generate_answer_end,
            SearchAgentEvents.PRINT_GENERATE_ANSWER_END.value,
        )

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
    
    # Chain event handlers
    def print_search_agent_start(
        self, 
        content: str, 
        purpose: str, 
        expected_sources: list[str]
    ):
        self._print_colored(f"\n🔍 开始执行检索任务", "yellow", True)
        self._print_colored(f" - 核查点 -> {content}", "yellow", True)
        self._print_colored(f" - 检索目标 -> {purpose}", "yellow", True)
        self._print_colored(f" - 预期信息来源 -> {expected_sources}", "yellow", True)
    
    def track_token_usage(self, current_tokens: int):
        tokens_used = current_tokens - self.last_tokens

        # 只有当token消耗有变化时才显示统计信息
        if tokens_used > 0:
            self.last_tokens = current_tokens

            self._print_colored(f"\n📊 Token消耗统计: ", "blue", True)
            self._print_colored(f"   本次消耗: {tokens_used} tokens", "blue")
            self._print_colored(f"   累计消耗: {current_tokens} tokens", "blue")
            self._print_colored(f"{'-'*50}", "blue")
    
    # Tool event handlers
    def print_tool_start(self, tool_name: str, input_str: str):
        self._print_colored(f"\n🔨 开始执行工具: {tool_name}", "purple")
        self._print_colored(f"📥 输入: {input_str}", "purple")

    def print_tool_result(self, output):
        self._print_colored(f"\n📤 工具执行结果:", "green")
        
        # 处理不同类型的输出
        try:
            # 如果是字符串类型，检查长度并按需截断
            if isinstance(output, str):
                if len(output) > 500:
                    self._print_colored(f"{output[:497]}...", "green")
                else:
                    self._print_colored(output, "green")
            elif isinstance(output, dict):
                self._print_colored(json.dumps(output, indent=2, ensure_ascii=False), "green")
            elif isinstance(output, list):
                if len(output) > 5:
                    self._print_colored(json.dumps(output[:5], indent=2, ensure_ascii=False), "green")
                    self._print_colored(f"...", "green")
                else:
                    self._print_colored(json.dumps(output, indent=2, ensure_ascii=False), "green")
            else:
                # 处理非字符串类型
                self._print_colored(str(output), "green")
        except Exception as e:
            self._print_colored(f"输出处理错误: {str(e)}", "red")

    def print_tool_error(self, error):
        self._print_colored(f"\n❌ 工具执行错误:", "red", True)
        self._print_colored(f"{str(error)}", "red")
        self._print_colored(f"{'-'*50}", "red")

    # LLM event handlers
    def print_evaluate_status_start(self, model_name: str):
        self.llm_call_count += 1
        self._print_colored(
            f"\n🧠 LLM 开始评估当前状态 (调用 #{self.llm_call_count}, {model_name})",
            "purple",
            True,
        )
    
    def print_generate_answer_start(self, model_name: str):
        self.llm_call_count += 1
        self._print_colored(
            f"\n🧠 LLM 开始生成检索结论 (调用 #{self.llm_call_count}, {model_name})",
            "green",
            True,
        )
    
    def print_status_evaluation_end(self, status):
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
                self._print_colored(f" 原文片段：{evidence.content}", "green")
                self._print_colored(f" 来源：{evidence.source}", "green")
                self._print_colored(f" 推理：{evidence.reasoning}", "green")
                self._print_colored(f" 关系：{evidence.relationship}", "green")
    
    def print_generate_answer_end(self, result):
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