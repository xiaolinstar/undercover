---
name: docker-deploy
description: 使用 Docker Compose 部署项目技能，包括开发环境、预发布环境和生产环境的部署方式。适用于各种后端和前端项目，暂不适用于 Android、IOS、微信小程序等应用。
---

# Docker 部署技能

项目部署使用 Docker Compose，通过环境变量区分不同环境。

## 环境配置

### 环境列表

- **开发环境**（development）：本地开发
- **预发布环境**（staging）：测试验证
- **生产环境**（production）：正式运行

### 环境变量

**配置文件结构**：
- 服务目录下的 `.env.example`: 环境变量模板（提交到 git）
- 服务目录下的 `.env.development`: 开发环境变量（不提交）
- 服务目录下的 `.env.staging`: 预发布环境变量（不提交）
- 服务目录下的 `.env.production`: 生产环境变量（不提交）

**创建配置文件**：

```bash
# 进入服务目录（如 backend/）
cd backend

# 根据环境创建特定环境变量文件
cp .env.example .env.development
cp .env.example .env.staging
cp .env.example .env.production
```

**环境变量检查**：在特定环境下启动项目时，如果未发现对应的环境变量文件，服务将终止并报错。

**环境自动推导**：
- 应用启动时会根据配置文件名自动推导环境
- 如果存在 `.env.production` 文件，则使用生产环境
- 如果存在 `.env.staging` 文件，则使用预发布环境
- 如果存在 `.env.development` 文件，则使用开发环境
- 优先级：production > staging > development
- 无需手动设置 `APP_ENV` 等环境标识

**重要**：
- 服务目录下的 `.env.example` 提交到 git 仓库
- 服务目录下的 `.env.development`、`.env.staging`、`.env.production` 不提交到 git 仓库
- 在服务目录的 `.gitignore` 中添加：`.env.*`
- 在项目根目录的 `.gitignore` 中添加：`backend/.env.*`

注意：不要修改 `.env.development`、`.env.staging`、`.env.production` 中的内容，仅修改参数值。

## 部署命令

### 开发环境

仅部署依赖组件（数据库、缓存等），应用服务在本地运行。

**特点**：
- 依赖服务使用 Docker 容器
- 应用服务在本地运行
- 便于调试和开发
- 支持热重载

**部署步骤**：

开发环境需要创建 `docker-compose.dev.yml` 文件，仅包含依赖服务。

```bash
# 1. 进入服务目录（如 backend/）
cd backend

# 2. 创建开发环境变量文件（如果不存在）
cp .env.example .env.development

# 3. 返回项目根目录
cd ..

# 4. 启动依赖服务
docker compose -f docker-compose.dev.yml up -d

# 5. 启动应用服务（根据项目类型选择）
# Python 项目
cd backend && source venv/bin/activate && python main.py

# Node.js 项目
cd frontend && npm run dev

# Java 项目
cd backend && ./mvnw spring-boot:run
```

### 预发布环境

完整部署所有服务，使用 Docker 容器运行。

**特点**：
- 所有服务使用 Docker 容器
- 模拟生产环境配置
- 用于测试验证
- 应用根据配置文件名自动推导环境

**部署步骤**：

```bash
# 1. 进入服务目录（如 backend/）
cd backend

# 2. 创建预发布环境变量文件（如果不存在）
cp .env.example .env.staging

# 3. 返回项目根目录
cd ..

# 4. 启动所有服务
docker compose --env-file backend/.env.staging up -d
```

### 生产环境

完整部署所有服务，使用 Docker 容器运行。

**特点**：
- 所有服务使用 Docker 容器
- 使用强密码和严格的安全配置
- 启用 HTTPS 和访问限制
- 应用根据配置文件名自动推导环境

**部署步骤**：

```bash
# 1. 进入服务目录（如 backend/）
cd backend

# 2. 创建生产环境变量文件（如果不存在）
cp .env.example .env.production

# 3. 返回项目根目录
cd ..

# 4. 启动所有服务
docker compose --env-file backend/.env.production up -d
```

### 停止服务

停止服务时使用与启动时相同的参数：

```bash
# 开发环境
docker compose -f docker-compose.dev.yml down

# 预发布环境
docker compose --env-file backend/.env.staging down

# 生产环境
docker compose --env-file backend/.env.production down
```

### 常用命令

```bash
# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f

# 重启服务
docker compose restart

# 进入容器
docker compose exec app bash
```

## Docker Compose 文件

### docker-compose.yml

完整部署配置，包含所有服务（app、数据库、缓存等）。

适用于预发布环境和生产环境。

### docker-compose.dev.yml

开发环境配置，仅包含依赖服务（数据库、缓存等）。

适用于开发环境，应用服务在本地运行。

## 环境自动推导实现

### 实现原理

应用启动时会自动检测配置文件，并根据文件名推导运行环境：

```python
def get_env_from_config_file():
    """根据配置文件名推导环境"""
    backend_dir = Path(__file__).parent
    
    # 检查环境变量文件是否存在
    env_files = [
        (".env.production", "prod"),
        (".env.staging", "staging"),
        (".env.development", "dev"),
    ]
    
    for env_file, env in env_files:
        env_file_path = backend_dir / env_file
        if env_file_path.exists():
            return env
    
    return "dev"
```

### 优先级

1. 如果存在 `.env.production` 文件，则使用生产环境
2. 如果存在 `.env.staging` 文件，则使用预发布环境
3. 如果存在 `.env.development` 文件，则使用开发环境
4. 如果都不存在，默认使用开发环境
 
### 部署示例

**预发布环境**：
```bash
# 只需要指定配置文件，应用会从 ENV_FILE 环境变量推导环境
docker compose --env-file backend/.env.staging up -d
```

**生产环境**：
```bash
# 只需要指定配置文件，应用会从 ENV_FILE 环境变量推导环境
docker compose --env-file backend/.env.production up -d
```

### 优势

- **简洁**：只需指定配置文件，无需额外的环境变量
- **可靠**：不会因为忘记设置环境变量而导致配置错误
- **直观**：配置文件名直接对应环境
- **灵活**：仍然支持通过命令行参数手动指定环境
- **安全**：.env.* 文件不会被打包到镜像中
- **无冗余**：从 ENV_FILE 推导环境，避免重复配置

## 环境变量配置

### 关键环境变量

根据项目类型，配置以下关键环境变量：

**后端项目**：
- 数据库连接 URL（开发环境使用 localhost，其他环境使用服务名）
- 缓存连接 URL（开发环境使用 localhost，其他环境使用服务名）
- 应用密钥（SECRET_KEY、API_KEY 等）
- 日志级别（DEBUG、INFO、WARNING）

**前端项目**：
- API 地址（开发环境、预发布环境、生产环境使用不同地址）
- WebSocket 地址
- 环境标识

### 环境差异

| 配置项 | 开发环境 | 预发布环境 | 生产环境 |
|--------|---------|-----------|---------|
| 数据库/缓存地址 | localhost | 服务名 | 服务名 |
| 日志级别 | DEBUG | INFO | WARNING |
| CORS/访问限制 | * | 特定域名 | 特定域名 |
| 文件日志 | 关闭 | 开启 | 开启 |

## 健康检查

在 Docker Compose 中为容器服务添加健康检查（health check），确保服务正常运行。

### 配置方法

在 `docker-compose.yml` 中为每个服务添加 `healthcheck` 配置：

```yaml
services:
  app:
    image: your-app:latest
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  mysql:
    image: mysql:8.4
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p$$MYSQL_ROOT_PASSWORD"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:7.0-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### 参数说明

- `test`: 健康检查命令
- `interval`: 检查间隔时间
- `timeout`: 超时时间
- `retries`: 失败重试次数
- `start_period`: 容器启动后等待时间

### 查看健康状态

```bash
# 查看所有服务的健康状态
docker compose ps

# 查看特定服务的健康状态
docker inspect --format='{{json .State.Health}}' <container_id>

# 查看健康检查日志
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' <container_id>
```

### 后端健康检查

```bash
curl http://localhost:{port}/health
```

### 数据库健康检查

```bash
docker compose exec mysql mysql -u user -ppassword -e "SELECT 1"
```

### 缓存健康检查

```bash
docker compose exec redis redis-cli ping
```

## 安全配置

### 生产环境要求

- 使用强密码
- 限制 CORS 允许的源
- 启用 HTTPS
- 定期更新依赖
- 使用防火墙限制访问

### 环境变量安全

- 不在代码中硬编码敏感信息
- 使用环境变量管理密钥
- 不将 `.env.*` 文件提交到版本控制
- 使用 `.env.example` 作为模板

## 备份恢复

### 备份数据库

```bash
docker compose exec mysql mysqldump -u user -ppassword database > backup.sql
```

### 恢复数据库

```bash
docker compose exec -T mysql mysql -u user -ppassword database < backup.sql
```