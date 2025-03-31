FROM python:3.11-slim

WORKDIR /app

# 设置环境变量
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=0

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/etc/poetry python3 -

# 添加Poetry到PATH
ENV PATH="/etc/poetry/bin:$PATH"

# 安装playwright依赖（如果实际需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxcb1 \
    libxkbcommon0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY pyproject.toml poetry.lock ./

# 安装依赖
RUN poetry install

# 安装playwright浏览器 (如果需要)
RUN poetry run playwright install chromium

# 复制环境变量文件
COPY .env .env.production ./

# 复制应用代码
COPY . .

# 创建启动脚本
RUN echo '#!/bin/bash\n\
if [ "$MODE" = "production" ]; then\n\
  export $(grep -v "^#" .env.production | xargs)\n\
else\n\
  export $(grep -v "^#" .env | xargs)\n\
fi\n\
exec poetry run gunicorn -c gunicorn.conf.py api.app:app\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# 暴露端口
EXPOSE 8000

# 启动应用
ENTRYPOINT ["/app/entrypoint.sh"]
