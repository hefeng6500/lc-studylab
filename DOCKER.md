# Docker 部署指南

本文档介绍如何使用 Docker 一键部署 LC-StudyLab 项目。

## 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 2GB 可用内存

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/hefeng6500/lc-studylab.git
cd lc-studylab
```

### 2. 配置环境变量

复制环境变量示例文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写必要的配置：

```env
# 必填：OpenAI API Key
OPENAI_API_KEY=sk-your-api-key-here

# 可选：Tavily 搜索 API Key
TAVILY_API_KEY=your-tavily-key

# 可选：高德天气 API Key
AMAP_KEY=your-amap-key

# 前端 API 地址（Docker 内部会自动使用服务名）
NEXT_PUBLIC_API_URL=http://backend:8000
```

### 3. 一键启动

```bash
docker-compose up -d
```

这个命令会：
- 构建后端和前端镜像
- 启动所有服务
- 在后台运行

### 4. 查看服务状态

```bash
docker-compose ps
```

### 5. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 只查看后端日志
docker-compose logs -f backend

# 只查看前端日志
docker-compose logs -f frontend
```

## 访问服务

启动成功后，可以通过以下地址访问：

- **前端应用**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **API 文档 (Swagger)**: http://localhost:8000/docs
- **API 文档 (ReDoc)**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

## 常用命令

### 停止服务

```bash
docker-compose down
```

### 停止并删除数据卷

```bash
docker-compose down -v
```

### 重新构建并启动

```bash
docker-compose up -d --build
```

### 查看服务日志

```bash
# 实时查看所有日志
docker-compose logs -f

# 查看最近 100 行日志
docker-compose logs --tail=100
```

### 进入容器

```bash
# 进入后端容器
docker-compose exec backend bash

# 进入前端容器
docker-compose exec frontend sh
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 只重启后端
docker-compose restart backend

# 只重启前端
docker-compose restart frontend
```

## 数据持久化

项目数据会持久化到以下目录：

- `./backend/data` - 文档、索引、研究数据
- `./backend/logs` - 日志文件

这些目录在容器重启后仍然保留。

## 环境变量说明

### 后端环境变量

| 变量名 | 说明 | 必填 | 默认值 |
|--------|------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | 是 | - |
| `OPENAI_API_BASE` | OpenAI API 基础 URL | 否 | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | 默认模型 | 否 | `gpt-4o` |
| `TAVILY_API_KEY` | Tavily 搜索 API 密钥 | 否 | - |
| `AMAP_KEY` | 高德天气 API 密钥 | 否 | - |
| `LOG_LEVEL` | 日志级别 | 否 | `INFO` |
| `DEBUG` | 调试模式 | 否 | `false` |

### 前端环境变量

| 变量名 | 说明 | 必填 | 默认值 |
|--------|------|------|--------|
| `NEXT_PUBLIC_API_URL` | 后端 API 地址 | 否 | `http://backend:8000` |

**注意**：在 Docker Compose 环境中，前端使用 `http://backend:8000` 访问后端（服务名）。如果单独部署，请修改为实际的后端地址。

## 故障排除

### 端口被占用

如果 8000 或 3000 端口被占用，可以修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "8001:8000"  # 将后端映射到 8001
  - "3001:3000"  # 将前端映射到 3001
```

### 构建失败

如果构建失败，可以尝试：

1. 清理 Docker 缓存：
```bash
docker-compose build --no-cache
```

2. 检查网络连接（需要下载依赖）

3. 查看详细错误日志：
```bash
docker-compose build --progress=plain
```

### 服务无法启动

1. 检查环境变量是否正确配置：
```bash
docker-compose config
```

2. 查看服务日志：
```bash
docker-compose logs backend
docker-compose logs frontend
```

3. 检查服务健康状态：
```bash
docker-compose ps
```

### 前端无法连接后端

1. 确保 `NEXT_PUBLIC_API_URL` 在 Docker 环境中设置为 `http://backend:8000`
2. 检查后端服务是否正常运行：
```bash
curl http://localhost:8000/health
```

3. 检查网络连接：
```bash
docker-compose exec frontend ping backend
```

## 生产环境部署

### 使用环境变量文件

在生产环境中，建议使用 `.env.production` 文件：

```bash
cp .env.example .env.production
# 编辑 .env.production 填写生产环境配置
docker-compose --env-file .env.production up -d
```

### 使用 Docker Secrets

对于敏感信息，可以使用 Docker Secrets：

```yaml
services:
  backend:
    secrets:
      - openai_api_key
secrets:
  openai_api_key:
    file: ./secrets/openai_api_key.txt
```

### 资源限制

在 `docker-compose.yml` 中添加资源限制：

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 使用反向代理

建议在生产环境中使用 Nginx 或 Traefik 作为反向代理：

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
      - frontend
```

## 更新项目

### 更新代码

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build
```

### 更新依赖

如果 `requirements.txt` 或 `package.json` 有更新：

```bash
# 重新构建（不使用缓存）
docker-compose build --no-cache

# 启动服务
docker-compose up -d
```

## 备份和恢复

### 备份数据

```bash
# 备份数据目录
tar -czf backup-$(date +%Y%m%d).tar.gz backend/data backend/logs
```

### 恢复数据

```bash
# 解压备份
tar -xzf backup-YYYYMMDD.tar.gz

# 重启服务
docker-compose restart
```

## 性能优化

### 使用多阶段构建缓存

Dockerfile 已经使用了多阶段构建，可以加快构建速度。

### 使用 BuildKit

启用 BuildKit 可以加快构建：

```bash
DOCKER_BUILDKIT=1 docker-compose build
```

### 使用镜像缓存

在 CI/CD 环境中，可以使用 Docker 镜像缓存服务。

## 安全建议

1. **不要提交 `.env` 文件**：确保 `.env` 在 `.gitignore` 中
2. **使用强密码**：如果添加了认证功能
3. **定期更新镜像**：保持基础镜像和依赖的最新版本
4. **限制网络访问**：使用防火墙规则限制不必要的端口
5. **使用 HTTPS**：在生产环境中使用反向代理配置 HTTPS

## 更多信息

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [Next.js Docker 部署](https://nextjs.org/docs/deployment#docker-image)
- [FastAPI 部署](https://fastapi.tiangolo.com/deployment/)

