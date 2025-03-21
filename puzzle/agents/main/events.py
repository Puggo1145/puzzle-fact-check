import json
import time
from datetime import datetime
from enum import Enum
from pubsub import pub
from db import db_integration
from .states import RetrievalResultVerification, CheckPoints

class MainAgentEvents(Enum):
    # DB 相关事件
    STORE_NEWS_TEXT = "main.store_news_text"
    
    # Node 开始事件
    EXTRACT_CHECK_POINT_START = "main.extract_check_point_start"
    EVALUATE_SEARCH_RESULT_START = "main.evaluate_search_result_start"
    WRITE_FACT_CHECKING_REPORT_START = "main.write_fact_checking_report_start"
    
    # Node 结束事件
    EXTRACT_CHECK_POINT_END = "main.extract_check_point_end"
    EVALUATE_SEARCH_RESULT_END = "main.evaluate_search_result_end"
    WRITE_FACT_CHECKING_REPORT_END = "main.write_fact_checking_report_end"
    
    # LLM 决策
    LLM_DECISION = "main.llm_decision"
    

class DBEvents:
    """
    DB Integration 回调，将新闻文本存储到数据库
    """

    def __init__(self):
        self.setup_subscribers()

    def setup_subscribers(self):
        # Subscribe to events
        pub.subscribe(
            self.store_news_text_to_db,
            MainAgentEvents.STORE_NEWS_TEXT.value,
        )

    def store_news_text_to_db(self, news_text: str) -> None:
        db_integration.initialize_with_news_text(news_text)


class CLIModeEvents:
    """
    Main Agent CLI Mode 回调，主要用于在 terminal 显示 LLM 的推理过程
    """

    def __init__(self):
        self.start_time = None
        self.token_usage = 0
        self.has_thinking_started = False
        self.has_content_started = False
        self.current_node = None

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
        
    def _print_colored(self, text, color="blue", bold=False):
        """Print colored text"""
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
                parsed_data = json.loads(data)
                return json.dumps(parsed_data, indent=2, ensure_ascii=False)
            except:
                return data
        elif isinstance(data, (dict, list)):
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            return str(data)
    
    # LLM 开始事件处理
    def on_extract_check_point_start(self):
        self.current_node = "extract_check_point"
        self.start_time = time.time()
        self.has_thinking_started = False
        self.has_content_started = False
        
        self._print_colored(
            f"\n🧠 LLM 开始提取核查点",
            "cyan",
            True,
        )
    
    def on_evaluate_search_result_start(self):
        self.current_node = "evaluate_search_result"
        self.start_time = time.time()
        self.has_thinking_started = False
        self.has_content_started = False
        
        self._print_colored(
            f"\n🧠 LLM 开始评估检索结果",
            "yellow",
            True,
        )
    
    def on_write_report_start(self):
        self.current_node = "write_fact_checking_report"
        self.start_time = time.time()
        self.has_thinking_started = False
        self.has_content_started = False
        
        self._print_colored(
            f"\n🧠 LLM 开始撰写核查报告",
            "green",
            True,
        )
    
    # LLM 结束事件处理
    def on_extract_check_point_end(self, check_points_result: CheckPoints):
        # 生成耗时
        if self.start_time:
            generation_time = time.time() - self.start_time
            self._print_colored(f"\n⏱️ 推理耗时: {generation_time:.2f}秒", "blue")

        # 控制台格式化输出
        self._print_colored("\n📋 LLM 的核查计划：", "cyan", True)
        
        # 处理核查计划
        try:
            check_points = check_points_result.items
            for idx, check_point in enumerate(check_points):
                print(f"\n第 {idx+1} 条陈述")
                print(f"陈述内容：{check_point.content}")
                print(f"是否需要核查：{'是' if check_point.is_verification_point else '否'}")
                print(f"核查理由：{check_point.importance}")
                if check_point.retrieval_step:
                    for idx, plan in enumerate(check_point.retrieval_step):
                        print(f"核查计划 {idx+1}：")
                        print(f"- 核查目标：{plan.purpose}")
                        print(f"- 目标信源类型：{plan.expected_sources}")
        except Exception as e:
            self._print_colored(f"解析核查计划失败: {str(e)}", "red")
            print(check_points_result)
    
    def on_evaluate_search_result_end(self, verification_result: RetrievalResultVerification):
        # 生成耗时
        if self.start_time:
            generation_time = time.time() - self.start_time
            self._print_colored(f"\n⏱️ 推理耗时: {generation_time:.2f}秒", "blue")

        try:
            # 打印评估结果
            status_emoji = "✅" if verification_result.verified else "❌"
            status_color = "green" if verification_result.verified else "red"
            
            self._print_colored(f"\n{status_emoji} 评估结论:", status_color, True)
            self._print_colored(f"📝 推理过程: {verification_result.reasoning}", "yellow")
            self._print_colored(f"🔍 是否认可: {'是' if verification_result.verified else '否'}", status_color)
            if verification_result.updated_purpose:
                self._print_colored(f"新的检索目的: {verification_result.updated_purpose}", "purple")
            if verification_result.updated_expected_sources:
                self._print_colored(f"新的预期来源: {', '.join(verification_result.updated_expected_sources)}", "purple")
            
        except Exception as e:
            self._print_colored(f"解析评估结果失败: {str(e)}", "red")
            print(verification_result)
    
    def on_write_report_end(self, response_text: str):
        # 生成耗时
        if self.start_time:
            generation_time = time.time() - self.start_time
            self._print_colored(f"\n⏱️ 推理耗时: {generation_time:.2f}秒", "blue")

        # 控制台格式化输出
        self._print_colored("\n📋 正在保存核查报告:", "cyan", True)
        
        # 保存为 markdown 到 logs/llm_outputs 目录下
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logs/llm_outputs/{timestamp}_report.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(response_text)
        
        # 直接打印报告内容，不尝试解析为JSON
        self._print_colored("\n📊 事实核查报告:", "green", True)
        print(response_text)
    
    def on_llm_decision(
        self, 
        decision: str,
        reason: str | None = None
    ):
        self._print_colored(f"\n🧠 LLM 做出决策: {decision}", "blue", True)
        if reason:
            self._print_colored(f"🔍 决策理由: {reason}", "yellow")
