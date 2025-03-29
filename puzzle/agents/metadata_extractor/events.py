import json
from enum import Enum
from pubsub import pub
from db import db_integration
from .states import BasicMetadata, Knowledge, Knowledges

class MetadataExtractAgentEvents(Enum):
    STORE_BASIC_METADATA = "store_basic_metadata"
    STORE_RETRIEVED_KNOWLEDGE = "store_retrieved_knowledge"
    EXTRACT_BASIC_METADATA_START = (
        "extract_basic_metadata_start"
    )
    EXTRACT_BASIC_METADATA_END = (
        "extract_basic_metadata_end"
    )
    EXTRACT_KNOWLEDGE_START = "extract_knowledge_start"
    EXTRACT_KNOWLEDGE_END = "extract_knowledge_end"
    RETRIEVE_KNOWLEDGE_START = "retrieve_knowledge_start"
    RETRIEVE_KNOWLEDGE_END = "retrieve_knowledge_end"


class DBEvents:
    """
    DB Integration 回调，将 metadata 存储到 neo4j
    """

    def __init__(self):
        self.setup_subscribers()

    def setup_subscribers(self):
        # Subscribe to events
        pub.subscribe(
            self.store_basic_metadata,
            MetadataExtractAgentEvents.STORE_BASIC_METADATA.value,
        )
        pub.subscribe(
            self.store_retrieved_knowledge,
            MetadataExtractAgentEvents.STORE_RETRIEVED_KNOWLEDGE.value,
        )

    def store_basic_metadata(self, basic_metadata: BasicMetadata) -> None:
        db_integration.store_basic_metadata(basic_metadata)

    def store_retrieved_knowledge(self, retrieved_knowledge: Knowledge) -> None:
        db_integration.store_retrieved_knowledge(retrieved_knowledge)

class CLIModeEvents:
    """
    Metadata Extractor CLI Mode 回调，主要用于在 terminal 显示 LLM 的推理过程
    """

    def __init__(self):
        self.step_count = 0  # 总步骤计数
        self.start_time = None
        self.last_tokens = 0
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
        # LLM start events
        pub.subscribe(
            self.print_basic_metadata_start,
            MetadataExtractAgentEvents.EXTRACT_BASIC_METADATA_START.value,
        )
        pub.subscribe(
            self.print_knowledge_start,
            MetadataExtractAgentEvents.EXTRACT_KNOWLEDGE_START.value,
        )
        pub.subscribe(
            self.print_retrieve_knowledge_start,
            MetadataExtractAgentEvents.RETRIEVE_KNOWLEDGE_START.value,
        )

        # LLM end events
        pub.subscribe(
            self.print_basic_metadata_end,
            MetadataExtractAgentEvents.EXTRACT_BASIC_METADATA_END.value,
        )
        pub.subscribe(
            self.print_knowledge_end,
            MetadataExtractAgentEvents.EXTRACT_KNOWLEDGE_END.value,
        )
        pub.subscribe(
            self.print_retrieve_knowledge_end,
            MetadataExtractAgentEvents.RETRIEVE_KNOWLEDGE_END.value,
        )

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

    # LLM start event handlers
    def print_basic_metadata_start(self):
        self._print_colored(
            f"\n🧠 LLM 开始提取基本元数据",
            "purple",
            True,
        )

    def print_knowledge_start(self):
        self._print_colored(
            f"\n🧠 LLM 开始提取知识元",
            "cyan",
            True,
        )

    def print_retrieve_knowledge_start(self):
        self._print_colored(
            f"\n🧠 LLM 开始检索知识元定义",
            "green",
            True,
        )

    # LLM end event handlers
    def print_basic_metadata_end(self, basic_metadata: BasicMetadata):
        self._print_basic_metadata(basic_metadata)

    def print_knowledge_end(self, knowledges: Knowledges):
        self._print_knowledges(knowledges)

    def print_retrieve_knowledge_end(self, retrieved_knowledge: Knowledge):
        self._print_retrieved_knowledge(retrieved_knowledge)

    def _print_basic_metadata(self, metadata):
        """打印基本元数据信息"""
        self._print_colored("\n📋 基本元数据:", "blue", True)
        # 新闻类型
        self._print_colored(f"📰 新闻类型: {metadata.news_type}", "blue")
        # 新闻六要素
        self._print_colored("\n🔍 新闻六要素 (5W1H):", "blue", True)
        # Who
        if metadata.who:
            self._print_colored("👤 Who (谁):", "blue")
            for item in metadata.who:
                self._print_colored(f"  • {item}", "blue")
        # What
        if metadata.what:
            self._print_colored("📌 What (什么):", "blue")
            for item in metadata.what:
                self._print_colored(f"  • {item}", "blue")
        # When
        if metadata.when:
            self._print_colored("🕒 When (何时):", "blue")
            for item in metadata.when:
                self._print_colored(f"  • {item}", "blue")
        # Where
        if metadata.where:
            self._print_colored("📍 Where (何地):", "blue")
            for item in metadata.where:
                self._print_colored(f"  • {item}", "blue")
        # Why
        if metadata.why:
            self._print_colored("❓ Why (为何):", "blue")
            for item in metadata.why:
                self._print_colored(f"  • {item}", "blue")
        # How
        if metadata.how:
            self._print_colored("🛠️ How (如何):", "blue")
            for item in metadata.how:
                self._print_colored(f"  • {item}", "blue")

    def _print_knowledges(self, knowledges: Knowledges):
        """打印知识元信息"""
        self._print_colored("\n🧩 知识元列表:", "cyan", True)

        if not knowledges.items:
            self._print_colored("  未提取到知识元", "cyan")
            return

        for i, item in enumerate(knowledges.items):
            self._print_colored(f"\n📝 知识元 #{i+1}:", "cyan", True)
            self._print_colored(f"  术语: {item.term}", "cyan")
            self._print_colored(f"  类别: {item.category}", "cyan")

            if hasattr(item, "description") and item.description:
                self._print_colored(f"  定义: {item.description}", "cyan")

            if hasattr(item, "source") and item.source:
                self._print_colored(f"  来源: {item.source}", "cyan")

    def _print_retrieved_knowledge(self, knowledge: Knowledge):
        """打印检索到的知识元定义"""
        self._print_colored("\n📚 知识元检索结果:", "green", True)

        # 打印术语
        if hasattr(knowledge, "term"):
            self._print_colored(f"📝 术语: {knowledge.term}", "green", True)

        # 打印类别
        if hasattr(knowledge, "category"):
            self._print_colored(f"🏷️ 类别: {knowledge.category}", "green")

        # 打印定义
        if hasattr(knowledge, "description") and knowledge.description:
            # 如果定义很长，分段显示
            description = knowledge.description
            if len(description) > 300:
                # 尝试按句子分割
                sentences = description.split(". ")
                self._print_colored(f"📚 定义:", "green", True)
                current_line = ""
                for sentence in sentences:
                    if len(current_line) + len(sentence) > 80:
                        self._print_colored(f"  {current_line}", "green")
                        current_line = sentence + ". "
                    else:
                        current_line += sentence + ". "
                if current_line:
                    self._print_colored(f"  {current_line}", "green")
            else:
                self._print_colored(f"📚 定义: {description}", "green")
        else:
            self._print_colored(f"📚 定义: 未找到定义", "yellow")

        # 打印来源
        if hasattr(knowledge, "source") and knowledge.source:
            self._print_colored(f"🔗 来源: {knowledge.source}", "green")
