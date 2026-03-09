#!/bin/bash

# 前端项目迁移脚本
# 将微信小程序项目移动到后端项目下

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

echo -e "${BLUE}🔄 开始迁移前端项目...${NC}"
echo ""

# 检查源目录是否存在
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}❌ 前端项目目录不存在: $FRONTEND_DIR${NC}"
    exit 1
fi

# 检查目标目录是否已存在
if [ -d "$TARGET_DIR" ]; then
    echo -e "${YELLOW}⚠️  目标目录已存在: $TARGET_DIR${NC}"
    read -p "是否删除现有目录并重新迁移？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}🗑️  删除现有目录...${NC}"
        rm -rf "$TARGET_DIR"
    else
        echo -e "${RED}❌ 迁移已取消${NC}"
        exit 1
    fi
fi

# 重命名后端src目录为backend
if [ -d "$BACKEND_DIR/src" ] && [ ! -d "$BACKEND_DIR/backend" ]; then
    echo -e "${YELLOW}📁 重命名 src -> backend...${NC}"
    mv "$BACKEND_DIR/src" "$BACKEND_DIR/backend"
fi

# 复制前端项目
echo -e "${YELLOW}📋 复制前端项目...${NC}"
cp -r "$FRONTEND_DIR" "$TARGET_DIR"

# 更新前端配置文件中的路径引用
echo -e "${YELLOW}🔧 更新前端配置...${NC}"

# 更新微信小程序配置（如果需要）
# 这里可以添加配置文件的更新逻辑

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

# 创建开发环境配置
echo -e "${YELLOW}⚙️  创建开发环境配置...${NC}"

# 创建docker-compose.dev.yml（如果不存在）
if [ ! -f "$BACKEND_DIR/docker-compose.dev.yml" ]; then
    cat > "$BACKEND_DIR/docker-compose.dev.yml" << 'EOF'
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: undercover-backend-dev
    ports:
      - "5001:5001"
    env_file:
      - .env
    environment:
      - TZ=Asia/Shanghai
      - FLASK_ENV=development
      - FLASK_DEBUG=1
      - REDIS_URL=redis://redis:6379/0
      - SQLALCHEMY_DATABASE_URI=mysql+pymysql://undercover:undercover@mysql:3306/undercover
    volumes:
      - ./backend:/app/backend
      - ./tests:/app/tests
    command: python -m backend.main
    depends_on:
      redis:
        condition: service_started
      mysql:
        condition: service_started

  redis:
    image: redis:7.0-alpine
    container_name: undercover-redis-dev
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - undercover_redis_dev_data:/data
    environment:
      - TZ=Asia/Shanghai

  mysql:
    image: mysql:8.4
    container_name: undercover-mysql-dev
    restart: always
    ports:
      - "3306:3306"
    volumes:
      - undercover_mysql_dev_data:/var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD=root
      - MYSQL_DATABASE=undercover
      - MYSQL_USER=undercover
      - MYSQL_PASSWORD=undercover
      - TZ=Asia/Shanghai
    command: --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci

volumes:
  undercover_redis_dev_data:
  undercover_mysql_dev_data:
EOF
    echo -e "${GREEN}✅ 创建 docker-compose.dev.yml${NC}"
fi

# 更新启动脚本
cat > "$BACKEND_DIR/scripts/dev-start.sh" << 'EOF'
#!/bin/bash

# 前后端联调启动脚本

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 启动前后端联调环境...${NC}"

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker未运行，请先启动Docker${NC}"
    exit 1
fi

# 检查.env文件
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env文件不存在，从.env.example创建...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ 已创建.env文件，请根据需要修改配置${NC}"
fi

# 停止旧容器
echo -e "${YELLOW}🛑 停止旧容器...${NC}"
docker-compose -f docker-compose.dev.yml down

# 启动开发环境
echo -e "${YELLOW}🔧 启动开发环境...${NC}"
docker-compose -f docker-compose.dev.yml up -d

# 等待服务启动
echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
sleep 8

# 检查服务状态
echo -e "${GREEN}📊 检查服务状态...${NC}"
docker-compose -f docker-compose.dev.yml ps

# 健康检查
echo -e "${YELLOW}🔍 健康检查...${NC}"
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:5001/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 后端服务健康检查通过${NC}"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo -e "${YELLOW}⏳ 等待后端服务启动... ($RETRY_COUNT/$MAX_RETRIES)${NC}"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}❌ 后端服务启动失败${NC}"
    echo -e "${YELLOW}查看日志：docker-compose -f docker-compose.dev.yml logs backend${NC}"
    exit 1
fi

# 显示服务地址
echo ""
echo -e "${GREEN}✅ 前后端联调环境启动完成！${NC}"
echo ""
echo -e "${GREEN}📡 服务地址：${NC}"
echo -e "   - 后端API: ${GREEN}http://localhost:5001${NC}"
echo -e "   - WebSocket: ${GREEN}ws://localhost:5001/ws${NC}"
echo -e "   - MySQL: ${GREEN}localhost:3306${NC}"
echo -e "   - Redis: ${GREEN}localhost:6379${NC}"
echo ""
echo -e "${GREEN}📱 前端项目：${NC}"
echo -e "   - 路径: ${GREEN}./frontend${NC}"
echo -e "   - 在微信开发者工具中打开: ${GREEN}$(pwd)/frontend${NC}"
echo ""
echo -e "${GREEN}🔧 开发工具：${NC}"
echo -e "   - 查看后端日志: ${GREEN}docker-compose -f docker-compose.dev.yml logs -f backend${NC}"
echo -e "   - 重启后端服务: ${GREEN}docker-compose -f docker-compose.dev.yml restart backend${NC}"
echo -e "   - 进入后端容器: ${GREEN}docker exec -it undercover-backend-dev bash${NC}"
echo ""
echo -e "${GREEN}🧪 测试工具：${NC}"
echo -e "   - 运行后端测试: ${GREEN}python3 -m pytest${NC}"
echo -e "   - 运行前端测试: ${GREEN}cd frontend && npm test${NC}"
echo -e "   - API健康检查: ${GREEN}curl http://localhost:5001/health${NC}"
echo ""
echo -e "${GREEN}🛑 停止服务：${NC}"
echo -e "   ${GREEN}./scripts/dev-stop.sh${NC}"
echo ""
EOF

chmod +x "$BACKEND_DIR/scripts/dev-start.sh"
echo -e "${GREEN}✅ 更新启动脚本${NC}"

# 创建项目说明文档
cat > "$BACKEND_DIR/PROJECT_STRUCTURE.md" << 'EOF'
# 项目结构说明

## 📁 目录结构

```
mp-undercover/
├── backend/              # 后端代码（Python Flask）
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
├── frontend/            # 前端代码（微信小程序）
│   ├── miniprogram/    # 小程序源码
│   │   ├── pages/      # 页面
│   │   ├── components/ # 组件
│   │   ├── services/   # 服务层
│   │   ├── models/     # 数据模型
│   │   ├── types/      # TypeScript类型
│   │   ├── utils/      # 工具函数
│   │   ├── config/     # 配置文件
│   │   └── mock/       # Mock数据
│   ├── tests/          # 前端测试
│   ├── typings/        # TypeScript类型定义
│   ├── package.json    # 依赖配置
│   └── tsconfig.json   # TypeScript配置
│
├── tests/              # 后端测试
│   ├── integration/    # 集成测试
│   └── unit/          # 单元测试
│
├── docs/              # 共享文档
│   ├── api/           # API文档
│   ├── guides/        # 开发指南
│   └── architecture.md
│
├── scripts/           # 开发脚本
│   ├── dev-start.sh  # 启动开发环境
│   └── dev-stop.sh   # 停止开发环境
│
├── migrations/       # 数据库迁移
│
├── docker-compose.yml         # 生产环境配置
├── docker-compose.dev.yml     # 开发环境配置
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
   - 修改 `backend/` 目录下的代码
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
   - API类型定义：`backend/models/responses/` 和 `frontend/miniprogram/types/`
   - 配置文件：`backend/config/` 和 `frontend/miniprogram/config/`
   - 文档：`docs/` 目录

3. **版本控制**
   - 使用Git管理整个项目
   - 前后端代码在同一仓库，便于版本同步
   - 使用.gitignore排除不必要的文件

## 🎯 优势

1. **统一开发环境**：前后端在同一项目下，便于管理
2. **AI工具支持**：AI可以理解整个项目结构，提供更好的建议
3. **类型安全**：前后端类型定义可以共享
4. **文档同步**：API文档和代码同步更新
5. **版本控制**：前后端版本同步，避免兼容性问题
EOF

echo -e "${GREEN}✅ 创建项目结构说明文档${NC}"

# 完成提示
echo ""
echo -e "${GREEN}✅ 迁移完成！${NC}"
echo ""
echo -e "${GREEN}📁 新的项目结构：${NC}"
echo -e "   - 后端: ${GREEN}./backend${NC}"
echo -e "   - 前端: ${GREEN}./frontend${NC}"
echo -e "   - 测试: ${GREEN}./tests${NC}"
echo -e "   - 文档: ${GREEN}./docs${NC}"
echo ""
echo -e "${GREEN}📝 下一步操作：${NC}"
echo -e "   1. 检查迁移结果: ${GREEN}ls -la${NC}"
echo -e "   2. 启动开发环境: ${GREEN}./scripts/dev-start.sh${NC}"
echo -e "   3. 在微信开发者工具中打开: ${GREEN}$(pwd)/frontend${NC}"
echo -e "   4. 查看项目结构: ${GREEN}cat PROJECT_STRUCTURE.md${NC}"
echo ""
echo -e "${YELLOW}⚠️  注意事项：${NC}"
echo -e "   - 原前端项目仍在: ${YELLOW}$FRONTEND_DIR${NC}"
echo -e "   - 确认迁移无误后，可以删除原项目"
echo -e "   - 更新IDEA项目配置，识别新的目录结构"
echo ""
