## 部署方案

本项目提供三种部署方式：本地运行、Docker 单容器、Docker Compose（前后端）。

### 1. 本地运行（开发）

```bash
conda create -n astockquant -c conda-forge -y python=3.10
conda activate astockquant
pip install -r backend/requirements.txt

python backend/main.py
```

### 2. Docker 单容器（仅后端）

```bash
docker build -t astockquant-backend -f backend/Dockerfile backend
docker run --rm -it -p 8000:8000 astockquant-backend
```

### 3. Docker Compose（前后端）

```bash
docker compose -f deploy/docker-compose.yml up --build
```

### 环境变量

- `HTTP_PROXY`, `HTTPS_PROXY`: 如需外网代理
- `TZ`: 时区（默认 Asia/Shanghai）
- `NEXT_PUBLIC_API_BASE`: 前端访问后端的地址（Compose 默认 http://backend:8000）

### 挂载与持久化

- 日志目录：建议在容器内使用 `/var/log/astockquant`，通过 `volumes` 挂载到宿主机
- 数据目录：如有本地缓存/模型，可挂载 `/app/data` 到宿主机

Compose 示例片段：

```yaml
services:
  backend:
    volumes:
      - ./data:/app/data
      - ./logs:/var/log/astockquant
    healthcheck:
      test: ["CMD", "python", "-c", "import socket; s=socket.socket(); s.connect(('localhost',8000)); print('ok')"]
      interval: 30s
      timeout: 5s
      retries: 3
  frontend:
    environment:
      - NEXT_PUBLIC_API_BASE=http://backend:8000
```


