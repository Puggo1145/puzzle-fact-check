import json
from typing import Any, Dict, Optional
from ..base import BaseAgentCallback, NodeEventTiming

class ExampleCallback(BaseAgentCallback):
    """
    示例回调类，演示如何使用节点事件管理器
    """
    def __init__(self):
        super().__init__()
        
        # 在初始化时注册节点事件回调
        
        # 示例1: 在节点开始时执行回调
        self.register_node_event(
            node_name="extract_basic_metadata",
            callback=self._on_metadata_extraction_start,
            timing=NodeEventTiming.ON_START
        )
        
        # 示例2: 在节点结束时执行回调
        self.register_node_event(
            node_name="extract_basic_metadata",
            callback=self._on_metadata_extraction_end,
            timing=NodeEventTiming.ON_END
        )
        
        # 示例3: 使用条件函数，只有在满足条件时才执行回调
        self.register_node_event(
            node_name="extract_knowledge",
            callback=self._on_knowledge_extraction_end,
            timing=NodeEventTiming.ON_END,
            condition=self._is_valid_knowledge
        )
        
        # 示例4: 使用字符串指定触发时机
        self.register_node_event(
            node_name="retrieve_knowledge",
            callback=self._on_knowledge_retrieval_end,
            timing="on_end"  # 等同于 NodeEventTiming.ON_END
        )
    
    def _on_metadata_extraction_start(self, context: Dict[str, Any]) -> None:
        """在元数据提取开始时执行"""
        print("开始提取元数据...")
        # 可以访问 context 中的输入数据
        inputs = context.get("inputs", {})
        print(f"输入文本长度: {len(str(inputs.get('text', '')))}")
    
    def _on_metadata_extraction_end(self, context: Dict[str, Any]) -> None:
        """在元数据提取结束时执行"""
        print("元数据提取完成!")
        # 可以访问 context 中的输出数据
        outputs = context.get("outputs", {})
        if "basic_metadata" in outputs:
            metadata = outputs["basic_metadata"]
            print(f"提取到的元数据: {json.dumps(metadata, ensure_ascii=False, indent=2)}")
    
    def _is_valid_knowledge(self, context: Dict[str, Any]) -> bool:
        """检查是否有有效的知识元"""
        outputs = context.get("outputs", {})
        knowledges = outputs.get("knowledges", {}).get("items", [])
        return bool(knowledges and len(knowledges) > 0)
    
    def _on_knowledge_extraction_end(self, context: Dict[str, Any]) -> None:
        """在知识元提取结束时执行"""
        outputs = context.get("outputs", {})
        knowledges = outputs.get("knowledges", {}).get("items", [])
        print(f"提取到 {len(knowledges)} 个知识元")
        
        # 可以在这里进行进一步处理，例如保存到数据库、发送通知等
    
    def _on_knowledge_retrieval_end(self, context: Dict[str, Any]) -> None:
        """在知识元检索结束时执行"""
        outputs = context.get("outputs", {})
        retrieved_knowledges = outputs.get("retrieved_knowledges", [])
        
        if retrieved_knowledges:
            print("成功检索到知识元定义!")
            for knowledge in retrieved_knowledges:
                print(f"术语: {knowledge.get('term')}")
                print(f"定义: {knowledge.get('description')}")
        else:
            print("未检索到知识元定义")


# 动态注册事件示例
def register_dynamic_events(callback: BaseAgentCallback):
    """
    演示如何在运行时动态注册事件
    """
    # 动态注册事件回调
    callback.register_node_event(
        node_name="custom_node",
        callback=lambda context: print(f"自定义节点执行完成: {context.get('outputs')}"),
        timing=NodeEventTiming.ON_END
    )
    
    # 使用条件函数
    def only_in_production(context: Dict[str, Any]) -> bool:
        """只在生产环境执行"""
        tags = context.get("tags", [])
        return "production" in tags
    
    callback.register_node_event(
        node_name="deploy",
        callback=lambda context: print("部署到生产环境"),
        timing=NodeEventTiming.ON_END,
        condition=only_in_production
    ) 