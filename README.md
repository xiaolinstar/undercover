# 聚会桌游，谁是卧底

一个基于微信小程序的聚会桌游"谁是卧底"项目。

## 📁 项目结构

```
mp-undercover/
├── backend/              # 后端代码（Python Flask）
├── frontend/            # 前端代码（微信小程序）
└── README.md            # 项目说明
```

## 🚀 快速开始

### 本地开发环境（推荐）

**后端服务**：
```bash
# 1. 启动依赖服务（Redis、MySQL）
docker compose -f docker-compose.dev.yml up -d

# 2. 启动后端应用（在 backend 目录）
cd backend
source venv/bin/activate && python main.py
```

**前端开发**：
在微信开发者工具中打开 `frontend/` 目录，开始开发和调试。

### Docker Compose 常用命令

```bash
# 启动开发环境（仅依赖服务）
docker compose -f docker-compose.dev.yml up -d

# 查看服务状态
docker compose -f docker-compose.dev.yml ps

# 查看日志
docker compose -f docker-compose.dev.yml logs -f

# 停止服务
docker compose -f docker-compose.dev.yml down

# 重启服务
docker compose -f docker-compose.dev.yml restart

# 进入容器
docker exec -it undercover-backend-dev bash
```

### 全容器部署（Staging/Production）

**一键启动所有服务**：
```bash
# 默认使用 staging 环境
docker compose up -d

# 或指定环境
docker compose --env-file backend/.env.staging up -d
docker compose --env-file backend/.env.production up -d
```

**停止服务**：
```bash
docker compose down
```

### 测试运行

```bash
# 运行所有测试
cd backend && python -m pytest tests/

# 运行单元测试
python -m pytest tests/unit/ -v

# 运行集成测试
python -m pytest tests/integration/ -v

# 生成覆盖率报告
python -m pytest tests/ --cov=src --cov-report=term-missing

# 生成 HTML 覆盖率报告
python -m pytest tests/ --cov=src --cov-report=html
# 查看报告：open htmlcov/index.html
```

## 📖 文档

详细文档请查看各模块的README：
- [后端文档](backend/README.md)
- [前端文档](frontend/README.md)

## 📞 联系方式

如有问题，请提交Issue。
