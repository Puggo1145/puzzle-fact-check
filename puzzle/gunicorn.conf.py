import os
import multiprocessing

# 单工作进程配置
workers = 1
worker_class = "sync"  # 使用同步工作模式，避免与 trio 冲突
threads = 4  # 每个工作进程的线程数

# 超时配置
timeout = 120  # 请求超时时间，根据实际情况调整
graceful_timeout = 10  # 优雅停机的超时时间
keepalive = 5  # 长连接超时

# 日志配置
accesslog = "-"  # 标准输出访问日志
errorlog = "-"  # 标准输出错误日志
loglevel = "info"

# 进程命名
proc_name = "puzzle_api"

# 绑定地址
bind = "0.0.0.0:" + os.getenv("PORT", "8000")

# 开发环境配置
if os.getenv("FLASK_ENV") == "development":
    reload = True  # 代码更改时自动重载
    workers = 1 