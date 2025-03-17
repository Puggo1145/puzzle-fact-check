# Agent 节点事件管理器

本文档介绍如何使用节点事件管理器来注册和处理 LangGraph 节点事件。

## 概述

节点事件管理器允许您在 LangGraph 节点执行的不同阶段（开始或结束时）注册回调函数，以便执行自定义操作，如日志记录、数据存储、监控等。

## 基本用法

### 1. 创建自定义回调类

首先，创建一个继承自 `BaseAgentCallback` 的自定义回调类：

```python
from agents.base import BaseAgentCallback, NodeEventTiming

class MyCustomCallback(BaseAgentCallback):
    def __init__(self):
        super().__init__()
        
        # 在初始化时注册节点事件回调
        self.register_node_event(
            node_name="my_node",
            callback=self._on_node_end,
            timing=NodeEventTiming.ON_END
        )
    
    def _on_node_end(self, context):
        print("节点执行完成!")
        print(f"输出: {context.get('outputs')}")
```

### 2. 注册事件回调

您可以在回调类的初始化方法中注册事件回调，也可以在运行时动态注册：

```python
# 在初始化时注册
def __init__(self):
    super().__init__()
    
    self.register_node_event(
        node_name="extract_data",
        callback=self._process_data,
        timing=NodeEventTiming.ON_END
    )

# 动态注册
def setup_additional_callbacks(self):
    self.register_node_event(
        node_name="analyze_data",
        callback=self._log_analysis_result,
        timing=NodeEventTiming.ON_END
    )
```

### 3. 使用条件函数

您可以添加条件函数，只有在满足条件时才执行回调：

```python
def __init__(self):
    super().__init__()
    
    self.register_node_event(
        node_name="deploy_model",
        callback=self._notify_deployment,
        timing=NodeEventTiming.ON_END,
        condition=self._is_production_deployment
    )

def _is_production_deployment(self, context):
    tags = context.get("tags", [])
    return "production" in tags
```

## 回调上下文

回调函数会接收一个上下文字典，其中包含与事件相关的信息：

### 节点开始时的上下文 (ON_START)

```python
{
    "serialized": {...},  # 序列化的节点信息
    "inputs": {...},      # 节点输入
    "kwargs": {...}       # 其他参数
}
```

### 节点结束时的上下文 (ON_END)

```python
{
    "outputs": {...},     # 节点输出
    "run_id": UUID,       # 运行ID
    "parent_run_id": UUID,# 父运行ID
    "tags": [...],        # 标签列表
    "kwargs": {...}       # 其他参数
}
```

## 完整示例

请参考 `agents/metadata_extractor/example_callback.py` 文件，其中包含了使用节点事件管理器的完整示例。

## 兼容性

为了保持向后兼容性，`BaseAgentCallback` 类仍然保留了 `handle_node_event` 方法，但建议使用新的节点事件管理器 API。 