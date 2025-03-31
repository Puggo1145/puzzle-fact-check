# Puzzle Fact Check SSE API

这是 Puzzle Fact Check 项目的 SSE API 模块，它允许前端通过 Server-Sent Events (SSE) 调用 LangGraph Agent 并跟踪其执行过程。

## 运行方式

### 开发模式

```bash
# 使用 Flask 开发服务器
poetry run python -m api.app
```

### 生产模式

```bash
# 使用 Gunicorn (单工作进程)
./run_server.sh
```

### 更新依赖并运行

如果遇到依赖问题或需要更新依赖，可以使用以下脚本：

```bash
./update_and_run.sh
```

## 注意事项

- 为保证 SSE 事件流和会话状态管理的稳定性，Gunicorn 配置使用了单工作进程模式
- 使用 `interrupt` API 终止任务时，请确保使用与创建会话相同的实例处理请求

