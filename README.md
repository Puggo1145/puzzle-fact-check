# Puzzle: A graph-based self-reflective AI news fact-checking agent
A research project from Nova news AI. Puzzle 使用一个主推理模型作为全局事实陈述提取、任务规划和推理的核心，使用多个子模型根据主模型规划的任务进行自主网络检索，并使用图谱存储和更新证据，最终生成可解释的推理过程和结论。主模型将根据当前推理状态和证据图谱，动态调整检索策略和推理路径，实现自我修正和持续优化，最终生成高质量的核查结论

采用 LangGraph 进行工作流编排，实现了模块化、低耦合、高内聚的架构设计。系统由主推理引擎、专家子模型集群、知识图谱管理器和工具集成层组成，通过状态管理和事件驱动机制实现各组件间的协调与通信。

# Built with
- LangGraph
- LangChain
- Browser-use
- Neo4j

# 参考项目结构

```
puzzle/
├── core/                      # 核心系统组件
│   ├── engine.py              # 主推理引擎
│   ├── state_manager.py       # 状态管理器
│   ├── event_bus.py           # 事件总线
│   └── config.py              # 系统配置
├── models/                    # 模型定义
│   ├── base_model.py          # 模型基类
│   ├── main_reasoner.py       # 主推理模型
│   └── experts/               # 专家模型
│       ├── source_tracer.py   # 媒体信源追踪
│       └── web_searcher.py    # 网络搜索
├── knowledge/                 # 知识图谱管理
│   ├── graph_manager.py       # 图谱管理器
│   ├── schema.py              # 图谱模式定义
│   ├── node_types.py          # 节点类型定义
│   └── relation_types.py      # 关系类型定义
├── tools/                     # 工具集成
│   ├── tool_registry.py       # 工具注册中心
│   ├── base_tool.py           # 工具基类
│   ├── search/                # 搜索工具
│   │   ├── google_search.py   # Google搜索
│   │   └── bing_search.py     # Bing搜索
│   ├── browser/               # 浏览器工具
│   │   ├── browser_tool.py    # 浏览器操作
│   │   └── content_parser.py  # 内容解析
│   └── data/                  # 数据工具
│       ├── statistics_tool.py # 统计分析
│       └── chart_parser.py    # 图表解析
├── workflows/                 # LangGraph工作流
│   ├── main_workflow.py       # 主工作流定义
│   ├── verification_flow.py   # 验证工作流
│   └── reflection_flow.py     # 反思工作流
├── states/                    # 状态定义
│   ├── base_state.py          # 状态基类
│   ├── verification_state.py  # 验证状态
│   └── reasoning_state.py     # 推理状态
├── utils/                     # 工具函数
│   ├── token_counter.py       # Token计数器
│   ├── logger.py              # 日志工具
│   └── prompt_templates.py    # 提示模板
├── api/                       # API接口
│   ├── routes.py              # 路由定义
│   └── controllers.py         # 控制器
├── tests/                     # 测试代码
│   ├── unit/                  # 单元测试
│   └── integration/           # 集成测试
├── config/                    # 配置文件
│   ├── default.yaml           # 默认配置
│   └── production.yaml        # 生产配置
├── main.py                    # 应用入口
└── README.md                  # 项目说明
```

# 参考核心组件设计
### 1. 状态管理

```python
# states/base_state.py
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class BaseState(BaseModel):
    """所有状态的基类，定义共享属性"""
    session_id: str
    timestamp: float = Field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """将状态转换为字典"""
        return self.dict()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseState":
        """从字典创建状态"""
        return cls(**data)

# states/verification_state.py
class VerificationState(BaseState):
    """事实验证状态"""
    statements: List[Dict[str, Any]] = Field(default_factory=list)
    evidence: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    verification_status: Dict[str, str] = Field(default_factory=dict)
    current_focus: Optional[str] = None
    
    def add_statement(self, statement_id: str, content: str, metadata: Dict[str, Any]) -> None:
        """添加待验证陈述"""
        self.statements.append({
            "id": statement_id,
            "content": content,
            "metadata": metadata
        })
        self.verification_status[statement_id] = "pending"
    
    def add_evidence(self, statement_id: str, evidence: Dict[str, Any]) -> None:
        """为陈述添加证据"""
        if statement_id not in self.evidence:
            self.evidence[statement_id] = []
        self.evidence[statement_id].append(evidence)
```

### 2. 主推理引擎

```python
# core/engine.py
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import Dict, Any, List

class MainReasoningEngine:
    """主推理引擎，负责任务规划和综合推理"""
    
    def __init__(self, model_config: Dict[str, Any], prompt_templates: Dict[str, str]):
        pass
        
    def extract_statements(self, text: str) -> List[Dict[str, Any]]:
        """从文本中提取需要验证的陈述"""
        pass
    
    def plan_verification(self, statements: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """为每个陈述规划验证步骤"""
        pass
        
    def synthesize_conclusion(self, state: "VerificationState") -> Dict[str, Any]:
        """根据收集的证据综合结论"""
        pass
    
    def _parse_statements(self, content: str) -> List[Dict[str, Any]]:
        """解析模型输出的陈述"""
        # 实现解析逻辑
        pass
    
    def _parse_verification_plan(self, content: str) -> List[str]:
        """解析验证计划"""
        # 实现解析逻辑
        pass
    
    def _parse_conclusion(self, content: str) -> Dict[str, Any]:
        """解析结论"""
        # 实现解析逻辑
        pass
```

### 3. 专家模型接口

```python
# models/base_model.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class ExpertModel(ABC):
    """专家模型基类，定义所有专家模型必须实现的接口"""
    
    @abstractmethod
    def verify_statement(self, statement: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """验证特定陈述"""
        pass
    
    @abstractmethod
    def extract_evidence(self, content: str, statement: Dict[str, Any]) -> Dict[str, Any]:
        """从内容中提取与陈述相关的证据"""
        pass
    
    @abstractmethod
    def evaluate_source(self, source: Dict[str, Any]) -> float:
        """评估来源的可靠性"""
        pass
    
    @abstractmethod
    def summarize_evidence(self, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """总结多条证据"""
        pass

# models/experts/data_expert.py
class DataExpert(ExpertModel):
    """数据验证专家，专注于数字、统计等数据类型核查"""
    
    def __init__(self, model_config: Dict[str, Any], prompt_templates: Dict[str, str]):
        pass
        
    def verify_statement(self, statement: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """验证包含数据的陈述"""
        pass
    
    # 实现其他抽象方法...
```

### 4. 知识图谱管理器

```python
# knowledge/graph_manager.py
from neo4j import GraphDatabase
from typing import Dict, Any, List, Optional

class GraphManager:
    """知识图谱管理器，负责与Neo4j交互"""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def create_statement_node(self, statement: Dict[str, Any]) -> str:
        """创建陈述节点"""
        with self.driver.session() as session:
            pass
    
    def create_evidence_node(self, evidence: Dict[str, Any]) -> str:
        """创建证据节点"""
        pass
    
    def create_relationship(self, from_id: str, to_id: str, rel_type: str, properties: Dict[str, Any]) -> None:
        """创建关系"""
        pass
    
    def get_evidence_for_statement(self, statement_id: str) -> List[Dict[str, Any]]:
        """获取与陈述相关的所有证据"""
        pass
    
    def _record_to_evidence(self, record) -> Dict[str, Any]:
        """将Neo4j记录转换为证据字典"""
        pass
```

### 5. 工具注册与管理

```python
# tools/tool_registry.py
from typing import Dict, Any, Callable, List, Type
from .base_tool import BaseTool

class ToolRegistry:
    """工具注册中心，管理所有可用工具"""
    
    def __init__(self):
        self.tools: Dict[str, Type[BaseTool]] = {}
        self.instances: Dict[str, BaseTool] = {}
    
    def register_tool(self, tool_id: str, tool_class: Type[BaseTool]) -> None:
        """注册工具类"""
        self.tools[tool_id] = tool_class
    
    def get_tool(self, tool_id: str, **kwargs) -> BaseTool:
        """获取工具实例，如果不存在则创建"""
        if tool_id not in self.instances:
            if tool_id not in self.tools:
                raise ValueError(f"Tool {tool_id} not registered")
            self.instances[tool_id] = self.tools[tool_id](**kwargs)
        return self.instances[tool_id]
    
    def list_available_tools(self) -> List[str]:
        """列出所有可用工具"""
        return list(self.tools.keys())
    
    def get_tool_description(self, tool_id: str) -> Dict[str, Any]:
        """获取工具描述"""
        if tool_id not in self.tools:
            raise ValueError(f"Tool {tool_id} not registered")
        return self.tools[tool_id].get_description()

# tools/base_tool.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseTool(ABC):
    """所有工具的基类"""
    
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具操作"""
        pass
    
    @classmethod
    def get_description(cls) -> Dict[str, Any]:
        """获取工具描述"""
        return {
            "name": cls.__name__,
            "description": cls.__doc__,
            "parameters": cls.get_parameters(),
            "returns": cls.get_returns()
        }
    
    @classmethod
    @abstractmethod
    def get_parameters(cls) -> List[Dict[str, Any]]:
        """获取参数描述"""
        pass
    
    @classmethod
    @abstractmethod
    def get_returns(cls) -> Dict[str, Any]:
        """获取返回值描述"""
        pass
```

### 6. LangGraph工作流定义

```python
# workflows/main_workflow.py
from langgraph.graph import StateGraph, END
from typing import Dict, Any, List, Tuple

def create_main_workflow(
    engine: "MainReasoningEngine",
    expert_models: Dict[str, "ExpertModel"],
    graph_manager: "GraphManager",
    tool_registry: "ToolRegistry"
) -> StateGraph:
    """创建主工作流"""
    
    # 定义工作流状态类型
    workflow = StateGraph(VerificationState)
    
    # 定义节点函数
    def extract_statements(state: VerificationState) -> VerificationState:
        """提取需要验证的陈述"""
        # 实现逻辑
        return state
    
    def plan_verification(state: VerificationState) -> VerificationState:
        """规划验证步骤"""
        # 实现逻辑
        return state
    
    def assign_experts(state: VerificationState) -> Dict[str, VerificationState]:
        """将陈述分配给专家模型"""
        # 根据陈述类型分配专家
        # 返回包含专家ID的字典，用于条件路由
        return {"data_expert": state} # 示例
    
    def verify_with_expert(state: VerificationState, expert_id: str) -> VerificationState:
        """使用特定专家验证陈述"""
        expert = expert_models[expert_id]
        # 实现验证逻辑
        return state
    
    def collect_evidence(state: VerificationState) -> VerificationState:
        """收集所有证据"""
        # 实现逻辑
        return state
    
    def synthesize_conclusion(state: VerificationState) -> VerificationState:
        """综合结论"""
        # 实现逻辑
        return state
    
    def reflect_and_improve(state: VerificationState) -> Tuple[VerificationState, bool]:
        """反思并决定是否需要进一步验证"""
        # 实现逻辑
        needs_more_verification = False  # 示例
        return state, needs_more_verification
    
    # 添加节点
    workflow.add_node("extract_statements", extract_statements)
    workflow.add_node("plan_verification", plan_verification)
    workflow.add_node("assign_experts", assign_experts)
    workflow.add_node("verify_with_data_expert", lambda state: verify_with_expert(state, "data_expert"))
    workflow.add_node("verify_with_history_expert", lambda state: verify_with_expert(state, "history_expert"))
    # 添加更多专家节点...
    workflow.add_node("collect_evidence", collect_evidence)
    workflow.add_node("synthesize_conclusion", synthesize_conclusion)
    workflow.add_node("reflect_and_improve", reflect_and_improve)
    
    # 定义边
    workflow.add_edge("extract_statements", "plan_verification")
    workflow.add_edge("plan_verification", "assign_experts")
    
    # 条件路由
    workflow.add_conditional_edges(
        "assign_experts",
        lambda outputs: list(outputs.keys())[0],  # 选择专家
        {
            "data_expert": "verify_with_data_expert",
            "history_expert": "verify_with_history_expert",
            # 更多专家路由...
        }
    )
    
    # 合并专家验证结果
    workflow.add_edge("verify_with_data_expert", "collect_evidence")
    workflow.add_edge("verify_with_history_expert", "collect_evidence")
    # 更多专家边...
    
    workflow.add_edge("collect_evidence", "synthesize_conclusion")
    workflow.add_edge("synthesize_conclusion", "reflect_and_improve")
    
    # 条件循环或结束
    workflow.add_conditional_edges(
        "reflect_and_improve",
        lambda state_and_flag: "continue" if state_and_flag[1] else "end",
        {
            "continue": "plan_verification",  # 循环回去进行更多验证
            "end": END  # 结束工作流
        }
    )
    
    return workflow
```

### 7. 事件总线

```python
# core/event_bus.py
from typing import Dict, Any, Callable, List
import uuid

class EventBus:
    """事件总线，用于组件间通信"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, callback: Callable) -> str:
        """订阅事件"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        subscription_id = str(uuid.uuid4())
        self.subscribers[event_type].append((subscription_id, callback))
        return subscription_id
    
    def unsubscribe(self, event_type: str, subscription_id: str) -> bool:
        """取消订阅"""
        if event_type not in self.subscribers:
            return False
        
        for i, (sid, _) in enumerate(self.subscribers[event_type]):
            if sid == subscription_id:
                self.subscribers[event_type].pop(i)
                return True
        
        return False
    
    def publish(self, event_type: str, data: Dict[str, Any] = None) -> None:
        """发布事件"""
        if event_type not in self.subscribers:
            return
        
        for _, callback in self.subscribers[event_type]:
            callback(data or {})
```

## 依赖注入与应用配置

```python
# core/config.py
import yaml
from typing import Dict, Any

class Config:
    """应用配置管理"""
    
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value

# main.py
from core.config import Config
from core.engine import MainReasoningEngine
from core.event_bus import EventBus
from knowledge.graph_manager import GraphManager
from tools.tool_registry import ToolRegistry
from models.experts.data_expert import DataExpert
from models.experts.history_expert import HistoryExpert
from workflows.main_workflow import create_main_workflow

def create_app(config_path: str = "config/default.yaml"):
    """创建应用实例"""
    # 加载配置
    config = Config(config_path)
    
    # 创建事件总线
    event_bus = EventBus()
    
    # 创建知识图谱管理器
    graph_manager = GraphManager(
        uri=config.get("neo4j.uri"),
        user=config.get("neo4j.user"),
        password=config.get("neo4j.password")
    )
    
    # 创建工具注册中心
    tool_registry = ToolRegistry()
    
    # 注册工具
    from tools.search.google_search import GoogleSearch
    from tools.browser.browser_tool import BrowserTool
    
    tool_registry.register_tool("google_search", GoogleSearch)
    tool_registry.register_tool("browser", BrowserTool)
    
    # 创建主推理引擎
    engine = MainReasoningEngine(
        model_config=config.get("models.main"),
        prompt_templates=config.get("prompts")
    )
    
    # 创建专家模型
    expert_models = {
        "data_expert": DataExpert(
            model_config=config.get("models.experts.data"),
            prompt_templates=config.get("prompts")
        ),
        "history_expert": HistoryExpert(
            model_config=config.get("models.experts.history"),
            prompt_templates=config.get("prompts")
        ),
        # 更多专家...
    }
    
    # 创建工作流
    workflow = create_main_workflow(
        engine=engine,
        expert_models=expert_models,
        graph_manager=graph_manager,
        tool_registry=tool_registry
    )
    
    return {
        "config": config,
        "event_bus": event_bus,
        "graph_manager": graph_manager,
        "tool_registry": tool_registry,
        "engine": engine,
        "expert_models": expert_models,
        "workflow": workflow
    }

if __name__ == "__main__":
    app = create_app()
    # 启动应用...
```

# 检索时精简
### 证据分层架构

**Core Logic**
- 仅包含直接支持/反驳陈述的1-2个关键句子
- 必须包含明确的逻辑关系标记

**Contextual Evidence**
- 包含核心证据的必要上下文(2-3句)
- 仅在主推理模型请求时加载

**Full Evidence Source**
- 存储为外部URL引用
- 仅在特殊情况下访问 

### 证据优先级机制

为每条证据分配一个综合评分(0-10)，基于：
- 相关性：证据与陈述的直接相关程度(0-3)
- 可靠性：来源的权威性和可信度(0-3)
- 时效性：信息的时间贴近度(0-2)
- 独特性：提供的独特信息价值(0-2)

主推理将优先考虑评分≥7的证据，其他证据仅在必要时考虑。 

### 语义压缩表示

采用高效的证据表示方法：

1. **实体规范化**：使用唯一ID代替重复出现的实体名称
   - 示例：将"美国总统拜登"替换为Entity[P001]

2. **关系编码**：使用简洁代码表示证据与陈述的关系
   - S+: 强力支持
   - S-: 弱支持
   - N: 中性/无关
   - C-: 弱反驳
   - C+: 强力反驳

3. **证据模板化**：使用结构化模板存储常见证据类型
   - 数值型证据：[Entity] [数值关系] [数值±误差] [单位] [时间点]
   - 事件型证据：[行为主体] [行为] [客体] [时间] [地点] 

### 证据合并与去重

1. **相似度聚类**：使用语义相似度(≥85%)识别相似证据
2. **多源合并**：合并来自不同来源的相似证据，保留所有来源引用
3. **强度累积**：记录支持同一论点的来源数量，提升可信度
4. **冲突标记**：显式标记来自不同来源但内容矛盾的证据 

### 增量检索与按需扩展

1. **基础-扩展模式**：
   - 基础阶段：对每个陈述仅检索1-2条核心证据
   - 扩展阶段：仅针对有争议或证据不足的陈述进行深度检索

2. **检索停止条件**：
   - 达到证据饱和(多个可靠来源一致确认)
   - 发现明确反例
   - 达到预设检索深度上限 

# 整体框架优化方案
### 任务规划与资源分配

1. **动态资源分配**
   - 根据陈述的重要性、复杂性和不确定性动态调整分配的检索资源
   - 对社会影响大、涉及重要人物或敏感话题的陈述分配更多检索资源

2. **子任务优先级队列**
   - 使用多因素评分模型为检索任务排序
   - 允许随时调整优先级，响应新发现的关键信息 

### 子模型专业化

1. **专业化检索模型**
   - 数据验证专家：专注于数字、统计、趋势等数据类型核查
   - 历史事件专家：专注于历史事件、时间线和因果关系核查
   - 人物关系专家：专注于人物背景、关系网络和行为模式核查
   - 科学事实专家：专注于科学原理、研究发现和技术知识核查

2. **协作与知识共享机制**
   - 子模型间建立发现共享通道，允许一个子模型利用另一个子模型的发现
   - 实现"知识广播"机制，重要发现自动通知所有相关子模型 

### 知识图谱结构增强

1. **时间敏感图谱**
   - 每个节点和关系添加时间属性：事件发生时间、报道时间、验证时间
   - 支持时间线视图，追踪事件和信息演变

2. **不确定性表示**
   - 使用概率权重表示关系的确定性(0.0-1.0)
   - 明确区分"未验证"和"已证伪"节点
   
3. **多维度关系**
   - 支持复合关系类型，包含：逻辑关系、时间关系、空间关系等
   - 实现关系的元属性，描述关系本身的特性

### 反思与自我修正机制

1. **决策点记录**
   - 记录每个重要推理步骤和证据选择
   - 构建决策树，支持回溯和替代路径探索

2. **假设测试**
   - 主动生成与当前结论相反的假设
   - 专门分配资源验证这些假设，增强结论可靠性

3. **失败模式库**
   - 维护常见检索和推理失败模式
   - 对照检查当前任务是否符合已知失败模式

### 系统效率优化

1. **证据缓存与复用**
   - 建立证据缓存机制，相似陈述可复用已验证的证据
   - 设置时效性标志，定期更新时效性敏感的缓存

2. **批量处理**
   - 识别相关陈述集合，一次性检索相关证据
   - 优化检索查询，一次检索满足多个相关陈述的需求

3. **并行检索管道**
   - 无依赖关系的检索任务并行执行
   - 实现检索结果流式处理，边检索边更新图谱

### 工具使用智能化

1. **工具选择与调用优化**
   - 为每个工具维护效能指标(准确率、延迟、token消耗)
   - 基于历史效能数据，智能选择最适合当前任务的工具
   - 支持工具组合调用模式，解决复杂检索需求

2. **查询优化**
   - 自动生成多样化检索查询，覆盖不同表达和角度
   - 实现查询结果分析与查询重构反馈循环

### 最终输出优化

1. **多层次结论呈现**
   - 简明摘要：1-2句核心结论
   - 详细解释：支持/反驳的主要证据及推理路径
   - 完整分析：全部证据、不确定因素和置信度分析

2. **可解释性增强**
   - 生成决策依据图，明确展示哪些证据影响了最终结论
   - 提供替代解释，说明若某些证据不可靠时可能的不同结论

