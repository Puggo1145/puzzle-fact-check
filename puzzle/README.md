# Puzzle Fact Check SSE API

这是 Puzzle Fact Check 项目的 SSE API 模块，它允许前端通过 Server-Sent Events (SSE) 调用 LangGraph Agent 并跟踪其执行过程。

## 功能特点

- 使用 Server-Sent Events (SSE) 实时流式输出 Agent 执行状态
- 支持前端追踪 Agent 在各个执行阶段的输出和流程
- 事件设计参考了 CLI 模式的事件，确保前端看到的内容与 CLI 模式一致
- 支持人工反馈与干预机制
- 简单的 Web 界面演示

## 目录结构

```
puzzle/
├── agents/ - Agent 实现模块
│   ├── base.py - 基本 Agent 类
│   ├── main/ - 主 Agent 模块
│   ├── metadata_extractor/ - 元数据提取 Agent
│   ├── searcher/ - 搜索 Agent
├── api/ - API 模块
│   ├── app.py - Flask 应用
│   ├── service.py - Agent 服务层
│   ├── __init__.py
├── frontend/ - 前端演示
│   ├── index.html - 简单 Web 界面
├── run_api.py - API 启动脚本
```

## 安装依赖

确保已安装以下依赖：

```bash
pip install flask flask-cors pubsub pypubsub langchain-openai langchain-core langgraph
```

## 运行 API 服务

```bash
python run_api.py
```

API 服务将在 http://localhost:8000 上运行。

## API 接口说明

### 1. 创建 Agent

```
POST /api/agents
```

请求体:
```json
{
  "model_name": "gpt-4o",
  "model_provider": "openai"
}
```

响应:
```json
{
  "session_id": "uuid-string"
}
```

### 2. 启动 Agent 执行

```
POST /api/agents/{session_id}/run
```

请求体:
```json
{
  "news_text": "要核查的新闻文本"
}
```

### 3. 发送人类反馈

```
POST /api/agents/{session_id}/feedback
```

请求体:
```json
{
  "feedback": "approve" | "revise"
}
```

### 4. 订阅事件流

```
GET /api/agents/{session_id}/events
```

这是一个 SSE 端点，返回事件流。前端可以使用 `EventSource` API 订阅。

## 事件类型

API 会发出以下类型的事件：

- `extract_check_point_start` - 开始提取核查点
- `extract_check_point_end` - 完成提取核查点
- `evaluate_search_result_start` - 开始评估检索结果
- `evaluate_search_result_end` - 完成评估检索结果
- `write_fact_check_report_start` - 开始撰写核查报告
- `write_fact_check_report_end` - 完成撰写核查报告
- `llm_decision` - LLM 做出决策
- `wait_human_feedback` - 等待人类反馈
- `human_feedback_received` - 收到人类反馈
- `task_complete` - 任务完成
- `error` - 发生错误

## 前端演示

打开 `frontend/index.html` 文件，它是一个简单的 Web 界面，演示如何使用 SSE API 与 Agent 交互。

确保 API 服务已经启动，然后在浏览器中打开 HTML 文件。

## 使用方法

1. 点击"创建 Agent"按钮创建一个新的 Agent 实例
2. 在文本框中输入要核查的新闻文本
3. 点击"开始核查"按钮启动核查流程
4. 在事件日志区域实时查看 Agent 执行过程
5. 当 Agent 需要人类反馈时，点击"接受核查计划"或"要求修改核查计划"按钮
6. 核查完成后，最终报告将显示在页面底部

## 开发说明

- `api/service.py` 包含 Agent 服务层，负责创建和管理 Agent 实例
- `api/app.py` 包含 Flask 应用，提供 HTTP API
- `SSEModeEvents` 类类似于 `CLIModeEvents`，但输出为事件流而非控制台
- 通过 `pubsub` 库实现事件发布/订阅机制

## 实现技术

- Flask - Web 框架
- Server-Sent Events (SSE) - 服务器推送事件
- LangGraph - Agent 编排框架
- pubsub - 事件发布/订阅