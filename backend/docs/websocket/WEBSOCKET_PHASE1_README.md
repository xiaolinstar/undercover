# WebSocket Phase 1 实施完成

## ✅ 已完成的任务

### 1. 环境准备和依赖安装
- ✅ 更新 `requirements.txt` 添加 WebSocket 依赖
  - flask-socketio==5.3.6
  - python-socketio==5.11.1
  - eventlet==0.35.2
- ✅ 更新 `.env.example` 添加 WebSocket 配置
- ✅ 更新 `src/config/settings.py` 添加配置类

### 2. 核心组件实现
- ✅ 创建 `src/websocket/` 模块
- ✅ 创建 `src/websocket/events.py` 事件定义
- ✅ 创建 `src/services/notification_service.py` 通知服务
- ✅ 创建 `src/websocket/handlers.py` WebSocket 处理器

### 3. 应用集成
- ✅ 更新 `src/app_factory.py` 集成 SocketIO
- ✅ 更新 `src/main.py` 支持 SocketIO 运行
- ✅ 创建测试脚本 `test_websocket_basic.py`

## 🚀 如何测试

### 方式 A: 使用现有的 docker-compose（推荐）

#### 步骤 1: 安装依赖

```bash
pip install -r requirements.txt
```

#### 步骤 2: 配置环境变量

复制 `.env.example` 到 `.env`（如果还没有）：

```bash
cp .env.example .env
```

确保 `.env` 中包含：
```bash
SECRET_KEY=your-secret-key-here
REDIS_URL=redis://localhost:6379/0
SOCKETIO_ASYNC_MODE=eventlet
SOCKETIO_CORS_ALLOWED_ORIGINS=*
```

#### 步骤 3: 启动 Redis 和 MySQL

```bash
docker-compose up -d redis mysql
```

验证服务是否启动：
```bash
docker-compose ps
```

你应该看到 redis 和 mysql 都在运行。

#### 步骤 4: 启动应用

```bash
python -m src.main
```

你应该看到类似的输出：
```
Application starting in dev mode
SocketIO initialized in eventlet mode
WebSocket handlers registered
 * Running on http://0.0.0.0:5001
```

#### 步骤 5: 运行测试脚本

在另一个终端窗口运行：

```bash
python test_websocket_basic.py
```

---

### 方式 B: 仅启动 Redis（最简单）

如果你只想测试 WebSocket 功能，不需要 MySQL：

#### 步骤 1-2: 同上

#### 步骤 3: 仅启动 Redis

```bash
docker-compose up -d redis
```

或者使用 Docker 直接启动：
```bash
docker run -d -p 6379:6379 --name redis redis:7.0-alpine
```

#### 步骤 4-5: 同上

---

### 方式 C: 本地 Redis（如果已安装）

如果你本地已经安装了 Redis：

```bash
# macOS
brew services start redis

# Linux
sudo systemctl start redis

# 或直接运行
redis-server
```

然后执行步骤 1、2、4、5。

预期输出：
```
============================================================
WebSocket 基础功能测试
============================================================
服务器地址: http://localhost:5001
请确保服务器正在运行: python -m src.main
============================================================

============================================================
测试 1: WebSocket 连接
============================================================
✓ 生成 JWT token: eyJ...
✓ WebSocket 连接成功
✓ 断开连接成功

============================================================
测试 2: 房间订阅
============================================================
✓ 收到连接成功消息: {...}
✓ 收到订阅成功消息: {...}
✓ 测试通过，收到 2 条消息

============================================================
测试 3: 心跳机制
============================================================
✓ 收到 pong 响应: {...}
✓ 心跳测试通过

============================================================
测试 4: 无效 Token 拒绝连接
============================================================
✓ 正确拒绝了无效 token: ...

============================================================
测试结果汇总
============================================================
连接测试: ✓ 通过
订阅测试: ✓ 通过
心跳测试: ✓ 通过
无效Token测试: ✓ 通过
============================================================
总计: 4/4 通过
============================================================
```

## 📁 新增文件

```
src/
├── websocket/
│   ├── __init__.py          # WebSocket 模块初始化
│   ├── events.py            # 事件类型定义
│   └── handlers.py          # WebSocket 事件处理器
├── services/
│   └── notification_service.py  # 通知服务
└── config/
    └── settings.py          # 更新：添加 WebSocket 配置

test_websocket_basic.py      # 测试脚本
WEBSOCKET_PHASE1_README.md   # 本文档
```

## 🔧 核心 API

### NotificationService

```python
from src.services.notification_service import NotificationService

# 在 GameService 中使用
notification_service.notify_room(
    room_id="8888",
    event="room.player_joined",
    data={"player_count": 4, "hint": "新玩家加入"}
)
```

### WebSocket 事件

客户端可以发送的事件：
- `connect` - 建立连接（需要 JWT token）
- `subscribe` - 订阅房间
- `unsubscribe` - 取消订阅
- `ping` - 心跳

客户端可以接收的事件：
- `connected` - 连接成功
- `subscribed` - 订阅成功
- `subscribe_error` - 订阅失败
- `pong` - 心跳响应
- `room.player_joined` - 玩家加入（未来集成）
- `game.started` - 游戏开始（未来集成）
- 等等...

## ⚠️ 已知限制

1. **房间权限验证未完成**：
   - 当前 `subscribe` 事件不验证用户是否真的在房间内
   - 需要在 Phase 2 集成 `room_repo` 和 `user_repo` 完成验证

2. **GameService 未集成通知**：
   - NotificationService 已创建但未在 GameService 中调用
   - 将在 Phase 2 完成集成

## 🎯 下一步：Phase 2

Phase 2 将完成业务集成：

1. 在 `GameService` 中集成 `NotificationService`
2. 在 `join_room()` 中发送 `room.player_joined` 通知
3. 在 `start_game()` 中发送 `game.started` 通知
4. 在 `vote_player()` 中发送 `vote.submitted` 通知
5. 在游戏结束时发送 `game.ended` 通知
6. 增强 HTTP API `/api/game/sync/{room_id}`

## 🐛 故障排查

### 问题 1: 连接被拒绝

**症状**: `Connection refused` 或 `Connection error`

**解决**:
- 确保服务器正在运行：`python -m src.main`
- 检查端口是否正确（默认 5001）
- 检查防火墙设置

### 问题 2: Token 验证失败

**症状**: `Connection rejected: invalid token`

**解决**:
- 确保 `.env` 中的 `SECRET_KEY` 与测试脚本中的一致
- 检查 token 是否过期

### 问题 3: Redis 连接失败

**症状**: `Redis connection error`

**解决**:
```bash
# 检查 Redis 是否运行
docker-compose ps

# 如果没有运行，启动 Redis
docker-compose up -d redis

# 或者使用独立的 Redis 容器
docker run -d -p 6379:6379 --name redis redis:7.0-alpine

# 测试 Redis 连接
redis-cli ping
# 应该返回 PONG
```

检查 `REDIS_URL` 配置是否正确：
- Docker Compose: `redis://localhost:6379/0`
- 容器内: `redis://redis:6379/0`

### 问题 4: eventlet 相关错误

**症状**: `ImportError: cannot import name 'eventlet'`

**解决**:
```bash
pip install eventlet==0.35.2
```

## 📚 参考文档

- [Flask-SocketIO 官方文档](https://flask-socketio.readthedocs.io/)
- [Socket.IO 客户端文档](https://socket.io/docs/v4/client-api/)
- [项目设计文档](.kiro/specs/websocket-notification-system/design.md)
- [任务列表](.kiro/specs/websocket-notification-system/tasks.md)

---

**Phase 1 完成时间**: 2024-02-23  
**下一阶段**: Phase 2 - 业务集成
