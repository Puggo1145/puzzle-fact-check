# Puzzle Fact Check 部署指南
该文档暂时由 AI 生成，稍后会根据实际情况进行修改

本文档提供将 Puzzle Fact Check 后端部署到生产环境的简要步骤。

## 准备工作

1. 服务器需求:
   - 安装好 1panel 面板
   - 至少 2GB 内存
   - 至少 10GB 存储空间

## 配置步骤

### 1. 克隆代码库

```bash
git clone <你的代码库URL>
cd puzzle
```

### 2. 配置环境变量

编辑 `.env.production` 文件，填入:
- API Keys (OpenAI, Qwen, DeepSeek 等)
- 其他必要的配置

### 3. 构建Docker镜像

在项目根目录下构建Docker镜像:

```bash
docker build -t puzzle-factcheck:latest .
```

### 4. 使用1panel部署

1. 登录1panel控制面板
2. 导航到"应用管理" > "Docker应用"
3. 创建新的容器，使用以下配置:
   - 镜像: `puzzle-factcheck:latest` (或者将镜像推送到Registry后使用)
   - 端口映射: 主机端口(任选) -> 容器端口 8000
   - 环境变量: 可从`.env.production`导入
   - 挂载卷: 可选择挂载 `logs` 目录用于持久化日志

4. 启动容器并检查日志确保服务正常运行

### 5. 配置HTTPS和访问限制

通过1panel面板:

1. 导航到"网站管理"部分
2. 创建新站点或编辑现有站点
3. 配置反向代理，将流量转发到Docker容器的端口
4. 在1panel中申请并配置SSL证书
5. 配置访问控制和请求限制策略

## 安全注意事项

1. API Key 保护
   - 确保 `.env.production` 文件不包含敏感信息或在1panel的环境变量中安全配置
   - 不要将 API Key 提交到版本控制系统

2. 更新策略
   - 定期更新容器镜像
   - 保持依赖库最新

## 监控与维护

通过1panel面板:

1. 监控容器资源使用情况
2. 查看容器日志
3. 配置自动重启策略

## 问题排查

如遇服务启动问题:

1. 通过1panel检查容器日志
2. 验证环境变量是否正确设置
3. 确保所有所需的 API Key 都已提供
4. 检查网络配置和防火墙规则

如需更多帮助，请参考项目文档或联系支持团队。 