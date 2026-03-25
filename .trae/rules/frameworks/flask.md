---
description: Flask 轻量级 Python Web 应用程序的约定和最佳实践。
globs: **/*.py
alwaysApply: false
---

# Flask 规则

## 核心原则

- 使用应用工厂（Application Factory）模式实现灵活的应用初始化
- 使用 Blueprints 按功能或资源组织路由
- 使用 Flask-SQLAlchemy 处理数据库模型和 ORM
- 使用应用工厂（application factories）实现灵活的应用初始化
- 使用 Flask 扩展实现常见功能（Flask-Login、Flask-WTF 等）
- 在环境变量中存储配置
- 使用 Flask-Migrate 进行数据库迁移
- 使用错误处理器实现适当的错误处理
- 使用 Flask-RESTful 或类似工具构建 API

## 项目结构

```
project/
├── app_factory.py          # 应用工厂
├── main.py                 # 应用启动入口
├── extensions.py           # Flask 扩展初始化
├── api/                    # API 蓝图和接口层
├── config/                 # 配置管理
├── models/                 # 数据模型层
├── repositories/           # 数据访问层（可选）
├── services/               # 业务逻辑层（可选）
├── exceptions/             # 异常处理（可选）
├── utils/                  # 工具函数
├── migrations/             # 数据库迁移
└── tests/                  # 测试代码
```
