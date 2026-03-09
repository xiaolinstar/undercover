# 项目结构说明

## 📁 目录结构

```
mp-undercover/
├── backend/              # 后端代码（Python Flask）- 完全独立模块
│   ├── api/             # API路由
│   ├── models/          # 数据模型
│   ├── services/        # 业务逻辑
│   ├── websocket/       # WebSocket处理
│   ├── config/          # 配置文件
│   ├── exceptions/      # 异常处理
│   ├── repositories/    # 数据访问层
│   ├── utils/           # 工具函数
│   ├── wechat/          # 微信相关
│   ├── fsm/             # 状态机
│   ├── strategies/      # 策略模式
│   ├── tests/           # 后端测试
│   ├── app_factory.py   # 应用工厂
│   ├── extensions.py    # 扩展配置
│   ├── main.py          # 入口文件
│   ├── requirements.txt # Python依赖
│   ├── pyproject.toml   # Python项目配置
│   ├── pytest.ini      # 测试配置
│   ├── .coveragerc     # 代码覆盖率配置
│   ├── Dockerfile      # Docker配置
│   ├── .env.example    # 环境变量示例
│   ├── .gitignore      # Git忽略文件
│   └── .dockerignore   # Docker忽略文件
│
├── frontend/            # 前端代码（微信小程序）
│   ├── miniprogram/    # 小程序源码
│   │   ├── pages/      # 页面
│   │   ├── components/ # 组件
│   │   ├── services/   # 服务层
│   │   ├── models/     # 数据模型
│   │   ├── types/      # TypeScript类型
│   │   ├── utils/      # 工具函数
│   │   ├── config/     # 配置文件
│   │   ├── mock/       # Mock数据
│   │   ├── assets/     # 静态资源
│   │   ├── app.json
│   │   ├── app.ts
│   │   └── sitemap.json
│   ├── tests/          # 前端测试
│   ├── typings/        # TypeScript类型定义
│   ├── package.json    # 依赖配置
│   ├── tsconfig.json   # TypeScript配置
│   └── jest.config.js  # 测试配置
│
├── docs/              # 共享文档
│   ├── api/           # API文档
│   ├── guides/        # 开发指南
│   ├── architecture.md
│   └── developer_guide.md
│
├── scripts/           # 开发脚本
│   ├── copy-frontend.sh  # 复制前端项目
│   ├── dev-start.sh     # 启动开发环境
│   └── dev-stop.sh      # 停止开发环境
│
├── docker-compose.yml        # 生产环境配置
├── docker-compose.dev.yml    # 开发环境配置
├── README.md                # 项目说明
├── PROJECT_STRUCTURE.md      # 项目结构说明
└── TODO.md                 # 待办事项
```

## 🚀 快速开始

### 1. 启动开发环境

```bash
# 启动后端服务
./scripts/dev-start.sh
```

### 2. 打开前端项目

在微信开发者工具中打开项目：
- 项目路径：`./frontend`
- 不校验合法域名（开发模式）

### 3. 开发流程

1. **后端开发**
   - 修改 `backend/` 目录下的代码
   - 运行测试：`cd backend && python3 -m pytest`
   - 查看日志：`docker-compose -f docker-compose.dev.yml logs -f backend`

2. **前端开发**
   - 修改 `frontend/miniprogram/` 目录下的代码
   - 运行测试：`cd frontend && npm test`
   - 在微信开发者工具中预览

3. **联调测试**
   - 后端API：http://localhost:5001
   - WebSocket：ws://localhost:5001/ws
   - 前端配置：`frontend/miniprogram/config/api.config.ts`

## 📡 服务地址

- **后端API**: http://localhost:5001
- **WebSocket**: ws://localhost:5001/ws
- **MySQL**: localhost:3306
- **Redis**: localhost:6379

## 🔧 开发工具

### 后端
- 运行测试：`cd backend && python3 -m pytest`
- 查看日志：`docker-compose -f docker-compose.dev.yml logs -f backend`
- 重启服务：`docker-compose -f docker-compose.dev.yml restart backend`
- 进入容器：`docker exec -it undercover-backend-dev bash`

### 前端
- 运行测试：`cd frontend && npm test`
- 构建项目：在微信开发者工具中点击"编译"
- 预览项目：在微信开发者工具中点击"预览"

## 📝 注意事项

1. **AI工具使用**
   - 整个项目在同一个IDEA项目下，AI工具可以更好地理解前后端关联
   - 修改API时，AI可以同时更新前后端相关代码
   - 类型定义共享，减少重复工作

2. **代码共享**
   - API类型定义：`backend/models/responses/` 和 `frontend/miniprogram/types/`
   - 配置文件：`backend/config/` 和 `frontend/miniprogram/config/`
   - 文档：`docs/` 目录

3. **版本控制**
   - 使用Git管理整个项目
   - 前后端代码在同一仓库，便于版本同步
   - 使用.gitignore排除不必要的文件

4. **前端项目同步**
   - 前端项目从 `/Users/xlxing/WechatProjects/undercover` 复制
   - 原项目保持不变，可以继续独立开发
   - 如需同步最新代码，重新运行 `./scripts/copy-frontend.sh`

## 🔄 同步前端代码

当原始前端项目有更新时，可以重新复制：

```bash
./scripts/copy-frontend.sh
```

这会删除当前的 `frontend/` 目录并重新复制最新的代码。

## 🎯 优势

1. **统一开发环境**：前后端在同一项目下，便于管理
2. **完全独立模块**：backend是完全独立的模块，包含所有配置和测试
3. **AI工具支持**：AI可以理解整个项目结构，提供更好的建议
4. **类型安全**：前后端类型定义可以共享
5. **文档同步**：API文档和代码同步更新
6. **版本控制**：前后端版本同步，避免兼容性问题
7. **安全复制**：原项目不受影响，可以随时重新复制
8. **模块化设计**：backend和frontend都是完全独立的模块
