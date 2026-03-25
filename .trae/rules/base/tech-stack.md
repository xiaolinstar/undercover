---
description: 项目所使用的技术栈以及官方文档
globs:
alwaysApply: true
---

# 技术栈规范

- 前端：微信小程序，使用 TypeScript（严格模式）
- 服务端：Flask 3.1+，Python 3.11+
- 数据库：MySQL 8.4，Redis 7.0
- 部署方式：
  - 开发环境 dev：Docker Compose 启动中间件依赖，Flask 应用在本地运行，微信小程序通过 localhost 访问后端服务
  - 预发布环境 staging：使用 Docker Compose 部署，与生产环境配置相同
  - 生产环境 prod：使用 Kubernetes 部署，Kustomize 管理配置

## Frontend 规范

- **包管理**：npm
- **框架**：微信小程序
- **语言**：TypeScript（严格模式）
- **测试**：Jest，@types/jest
- **类型定义**：miniprogram-api-typings


## Backend 规范

- **环境和包管理**：venv、pip
- **ORM**：Flask-SQLAlchemy，Flask-Migrate
- **WebSocket**：Flask-SocketIO，Python-SocketIO，优先编写原生 WebSocket，以适配微信小程序客户端
- **配置管理**：Pydantic，Pydantic-Settings
- **认证**：PyJWT
- **微信集成**：WeChatPy
- **测试**：pytest，pytest-cov，fakeredis
- **代码质量**：ruff