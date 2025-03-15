import json
from uuid import UUID
from typing import Any, Dict, Optional
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.agents import AgentAction
from .prompts import basic_metadata_extractor_output_parser, knowledge_extraction_output_parser, knowledge_retrieve_output_parser


class MetadataExtractorCallback(BaseCallbackHandler):
    """
    Callback function，用于跟踪和显示 Metadata Extractor Agent 执行过程中的状态变化
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
        # 跟踪当前正在执行的节点
        self.current_node = None
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
        
    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """当链开始运行时调用，检查当前节点"""
        try:            
            # 从 kwargs 中读取 node 名称
            node_name = None
            if kwargs and "metadata" in kwargs and isinstance(kwargs["metadata"], dict):
                node_name = kwargs["metadata"].get("langgraph_node", None)
                self.current_node = node_name
        except Exception as e:
            print(f"Error in on_chain_start: {str(e)}")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """当链结束运行时调用"""
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
        tool_name = serialized.get("name", "Unknown Tool")
        self._print_colored(f"\n🔨 开始执行工具: {tool_name}", "purple")
        self._print_colored(f"📥 输入: {input_str}", "purple")

    def on_tool_end(self, output, **kwargs):
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
        self._print_colored(f"\n❌ 工具执行错误:", "red", True)
        self._print_colored(f"{str(error)}", "red")
        self._print_colored(f"{'-'*50}", "red")

    def on_llm_start(self, serialized, prompts, **kwargs):
        """当LLM开始生成时调用"""
        self.llm_call_count += 1  # 增加LLM调用计数

        model_name = serialized.get("name", "Unknown Model")
        
        # 根据当前节点显示不同的开始信息
        if self.current_node == "extract_basic_metadata":
            self._print_colored(
                f"\n🧠 LLM 开始提取基本元数据 (调用 #{self.llm_call_count}, {model_name})",
                "purple",
                True,
            )
        elif self.current_node == "extract_knowledge":
            self._print_colored(
                f"\n🧠 LLM 开始提取知识元 (调用 #{self.llm_call_count}, {model_name})",
                "cyan",
                True,
            )
        elif self.current_node == "retrieve_knowledge":
            self._print_colored(
                f"\n🧠 LLM 开始检索知识元定义 (调用 #{self.llm_call_count}, {model_name})",
                "green",
                True,
            )
        else:
            self._print_colored(
                f"\n🧠 LLM 开始生成 (调用 #{self.llm_call_count}, {model_name})",
                "purple",
                True,
            )
        # 如果需要查看提示词，可以取消下面的注释
        # self._print_colored(f"提示词: {prompts}", "purple")

    def on_llm_end(self, response, **kwargs):
        """当LLM生成结束时调用"""
        if self.current_node == "agent" or self.current_node == "tools":
            return
        
        self._print_colored("📋 输出:", "cyan", True)
        
        # 根据当前节点处理不同的输出
        if not hasattr(response, "generations") or not response.generations:
            return
            
        generated_text = response.generations[0][0].text
        
        if self.current_node == "extract_basic_metadata":
            try:
                parsed_result = basic_metadata_extractor_output_parser.parse(generated_text)
                self._print_basic_metadata(parsed_result)
            except Exception as e:
                self._print_colored(f"解析基本元数据失败: {str(e)}", "red")
                print(generated_text)
        elif self.current_node == "extract_knowledge":
            try:
                parsed_result = knowledge_extraction_output_parser.parse(generated_text)
                self._print_knowledges(parsed_result)
            except Exception as e:
                self._print_colored(f"解析知识元失败: {str(e)}", "red")
                print(generated_text)
        elif self.current_node == "generate_structured_response":
            try:
                # 尝试解析为知识元对象
                parsed_result = knowledge_retrieve_output_parser.parse(generated_text)
                self._print_retrieved_knowledge(parsed_result)
            except Exception as e:
                self._print_colored(f"解析知识元检索结果失败: {str(e)}\n")
                print(generated_text)
    
    def _print_basic_metadata(self, metadata):
        """打印基本元数据信息"""
        self._print_colored("\n📋 基本元数据:", "blue", True)
        
        # 打印新闻类型
        self._print_colored(f"📰 新闻类型: {metadata.news_type}", "blue")
        
        # 打印新闻六要素
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
    
    def _print_knowledges(self, knowledges):
        """打印知识元信息"""
        self._print_colored("\n🧩 知识元列表:", "cyan", True)
        
        if not knowledges.items:
            self._print_colored("  未提取到知识元", "cyan")
            return
            
        for i, item in enumerate(knowledges.items):
            self._print_colored(f"\n📝 知识元 #{i+1}:", "cyan", True)
            self._print_colored(f"  术语: {item.term}", "cyan")
            self._print_colored(f"  类别: {item.category}", "cyan")
            
            if hasattr(item, 'definition') and item.definition:
                self._print_colored(f"  定义: {item.definition}", "cyan")
                
            if hasattr(item, 'importance') and item.importance:
                self._print_colored(f"  重要性: {item.importance}", "cyan")
                
            if hasattr(item, 'source') and item.source:
                self._print_colored(f"  来源: {item.source}", "cyan")
                
    def _print_retrieved_knowledge(self, knowledge):
        """打印检索到的知识元定义"""
        self._print_colored("\n📚 知识元检索结果:", "green", True)
        
        # 打印术语
        if hasattr(knowledge, 'term'):
            self._print_colored(f"📝 术语: {knowledge.term}", "green", True)
            
        # 打印类别
        if hasattr(knowledge, 'category'):
            self._print_colored(f"🏷️ 类别: {knowledge.category}", "green")
            
        # 打印定义
        if hasattr(knowledge, 'description') and knowledge.description:
            # 如果定义很长，分段显示
            description = knowledge.description
            if len(description) > 300:
                # 尝试按句子分割
                sentences = description.split('. ')
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
        if hasattr(knowledge, 'source') and knowledge.source:
            self._print_colored(f"🔗 来源: {knowledge.source}", "green")
