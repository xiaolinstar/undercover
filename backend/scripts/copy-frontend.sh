#!/bin/bash

# 前端项目复制脚本
# 将微信小程序项目复制到后端项目下，保持原项目不变

set -e

# 项目路径
BACKEND_DIR="/Users/xlxing/PycharmProjects/mp-undercover"
FRONTEND_DIR="/Users/xlxing/WechatProjects/undercover"
TARGET_DIR="$BACKEND_DIR/frontend"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 开始复制前端项目...${NC}"
echo ""

# 检查源目录是否存在
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}❌ 前端项目目录不存在: $FRONTEND_DIR${NC}"
    exit 1
fi

# 检查目标目录是否已存在
if [ -d "$TARGET_DIR" ]; then
    echo -e "${YELLOW}⚠️  目标目录已存在: $TARGET_DIR${NC}"
    read -p "是否删除现有目录并重新复制？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}🗑️  删除现有目录...${NC}"
        rm -rf "$TARGET_DIR"
    else
        echo -e "${RED}❌ 复制已取消${NC}"
        exit 1
    fi
fi

# 复制前端项目
echo -e "${YELLOW}📋 复制前端项目到后端项目...${NC}"
cp -r "$FRONTEND_DIR" "$TARGET_DIR"

# 创建.gitignore条目（如果不存在）
if [ -f "$BACKEND_DIR/.gitignore" ]; then
    if ! grep -q "frontend/node_modules" "$BACKEND_DIR/.gitignore"; then
        echo -e "${YELLOW}📝 更新.gitignore...${NC}"
        echo "" >> "$BACKEND_DIR/.gitignore"
        echo "# Frontend" >> "$BACKEND_DIR/.gitignore"
        echo "frontend/node_modules/" >> "$BACKEND_DIR/.gitignore"
        echo "frontend/.cloudbase/" >> "$BACKEND_DIR/.gitignore"
        echo "frontend/miniprogram/.DS_Store" >> "$BACKEND_DIR/.gitignore"
    fi
fi

# 创建项目说明文档
cat > "$BACKEND_DIR/PROJECT_STRUCTURE.md" << 'EOF'
# 项目结构说明

## 📁 目录结构

```
mp-undercover/
├── src/                  # 后端代码（Python Flask）
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
│   ├── app_factory.py   # 应用工厂
│   ├── extensions.py    # 扩展配置
│   └── main.py          # 入口文件
│
├── frontend/            # 前端代码（微信小程序，从WechatProjects/undercover复制）
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
├── tests/              # 后端测试
│   ├── integration/    # 集成测试
│   └── unit/          # 单元测试
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
├── migrations/       # 数据库迁移
│
├── docker-compose.yml        # 生产环境配置
├── docker-compose.dev.yml    # 开发环境配置
├── requirements.txt          # Python依赖
├── pyproject.toml            # Python项目配置
├── pytest.ini               # 测试配置
├── .env.example             # 环境变量示例
├── .gitignore               # Git忽略文件
└── README.md                # 项目说明
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
   - 修改 `src/` 目录下的代码
   - 运行测试：`python3 -m pytest`
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
- 运行测试：`python3 -m pytest`
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
   - API类型定义：`src/models/responses/` 和 `frontend/miniprogram/types/`
   - 配置文件：`src/config/` 和 `frontend/miniprogram/config/`
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
2. **AI工具支持**：AI可以理解整个项目结构，提供更好的建议
3. **类型安全**：前后端类型定义可以共享
4. **文档同步**：API文档和代码同步更新
5. **版本控制**：前后端版本同步，避免兼容性问题
6. **安全复制**：原项目不受影响，可以随时重新复制
EOF

echo -e "${GREEN}✅ 创建项目结构说明文档${NC}"

# 完成提示
echo ""
echo -e "${GREEN}✅ 复制完成！${NC}"
echo ""
echo -e "${GREEN}📁 项目结构：${NC}"
echo -e "   - 后端: ${GREEN}./src${NC}"
echo -e "   - 前端: ${GREEN}./frontend${NC} (从 $FRONTEND_DIR 复制)"
echo -e "   - 测试: ${GREEN}./tests${NC}"
echo -e "   - 文档: ${GREEN}./docs${NC}"
echo ""
echo -e "${GREEN}📝 下一步操作：${NC}"
echo -e "   1. 检查复制结果: ${GREEN}ls -la frontend${NC}"
echo -e "   2. 启动开发环境: ${GREEN}./scripts/dev-start.sh${NC}"
echo -e "   3. 在微信开发者工具中打开: ${GREEN}$(pwd)/frontend${NC}"
echo -e "   4. 查看项目结构: ${GREEN}cat PROJECT_STRUCTURE.md${NC}"
echo ""
echo -e "${BLUE}💡 提示：${NC}"
echo -e "   - 原前端项目保持不变: ${BLUE}$FRONTEND_DIR${NC}"
echo -e "   - 可以继续在原项目中独立开发"
echo -e "   - 需要同步时重新运行: ${BLUE}./scripts/copy-frontend.sh${NC}"
echo -e "   - 在IDEA中可以同时看到前后端代码，便于AI工具理解"
echo ""
