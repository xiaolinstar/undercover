# WebSocket 开发规范

## 1. 开发流程规范

### 1.1 代码提交前检查清单

在提交任何代码前，必须完成以下检查：

- [ ] **运行所有单元测试**
  ```bash
  python -m pytest tests/ -v
  ```
  
- [ ] **确保测试通过率 100%**（排除已知的遗留问题）
  - 当前已知问题：`tests/api_test.py::ApiIntegrationTest::test_full_game_flow`
  - 所有其他测试必须通过

- [ ] **清理 Docker 进程**
  ```bash
  docker-compose down
  ```

- [ ] **验证代码格式**
  ```bash
  ruff check src/
  ```

### 1.2 测试环境准备

#### 启动测试环境

```bash
# 1. 启动 Redis（如果需要）
docker-compose up -d redis

# 2. 运行测试
python -m pytest tests/ -v

# 3. 清理环境
docker-compose down
```

#### 测试覆盖率

```bash
# 生成覆盖率报告
python -m pytest tests/ --cov=src --cov-report=term-missing

# 生成 HTML 报告
python -m pytest tests/ --cov=src --cov-report=html
```

## 2. WebSocket 开发规范

### 2.1 事件命名规范

事件名称格式：`{domain}.{action}`

**示例**：
- ✅ `room.player_joined` - 正确
- ✅ `game.started` - 正确
- ❌ `playerJoined` - 错误（驼峰命名）
- ❌ `ROOM_PLAYER_JOINED` - 错误（全大写）

**事件定义位置**：`src/websocket/events.py`

### 2.2 消息格式规范

所有 WebSocket 消息必须遵循统一格式：

```json
{
  "event": "room.player_joined",
  "room_id": "8888",
  "timestamp": 1708675200,
  "data": {
    "player_count": 4,
    "hint": "新玩家加入"
  }
}
```

**字段说明**：
- `event` (必需): 事件类型
- `room_id` (必需): 房间ID
- `timestamp` (必需): Unix 时间戳
- `data` (可选): 轻量级提示数据

### 2.3 通知发送规范

**使用 NotificationService**：

```python
# ✅ 正确：使用 NotificationService
if self.notification:
    self.notification.notify_room(
        room_id=room_id,
        event="room.player_joined",
        data={"player_count": 4, "hint": "新玩家加入"}
    )

# ❌ 错误：直接使用 socketio
socketio.emit('room.player_joined', data, room=room_id)
```

**检查 notification_service 是否存在**：

```python
# 始终检查 notification_service 是否已初始化
if self.notification:
    self.notification.notify_room(...)
```

### 2.4 数据传输规范

**WebSocket 传输**：
- ✅ 轻量级提示信息（如 "新玩家加入"）
- ✅ 事件类型和房间ID
- ❌ 完整的房间状态数据
- ❌ 玩家详细信息列表

**HTTP API 传输**：
- ✅ 完整的房间状态
- ✅ 玩家列表和详细信息
- ✅ 游戏配置和规则

## 3. 测试规范

### 3.1 单元测试规范

**测试文件位置**：
- 服务层测试：`tests/unit/src/services/`
- 模型层测试：`tests/unit/src/models/`
- WebSocket 测试：`tests/unit/src/websocket/`（未来添加）

**测试命名规范**：
```python
def test_notify_room_success():
    """测试成功发送房间通知"""
    pass

def test_notify_room_with_invalid_room_id():
    """测试无效房间ID的处理"""
    pass
```

### 3.2 集成测试规范

**WebSocket 集成测试**：

```python
def test_websocket_connection():
    """测试 WebSocket 连接"""
    client = Client()
    token = generate_test_token("test_user")
    client.connect(SERVER_URL, auth={'token': token})
    # 验证连接成功
    assert client.connected
```

### 3.3 测试数据规范

**使用 fakeredis**：
```python
# 测试环境自动使用 fakeredis
# 无需手动配置
```

**JWT Token 生成**：
```python
import jwt
import time

def generate_test_token(user_id: str) -> str:
    payload = {
        'user_id': user_id,
        'exp': int(time.time()) + 3600
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
```

## 4. 代码审查规范

### 4.1 审查检查点

- [ ] 是否添加了必要的类型提示
- [ ] 是否添加了文档字符串
- [ ] 是否处理了异常情况
- [ ] 是否添加了日志记录
- [ ] 是否更新了相关测试
- [ ] 是否遵循了命名规范

### 4.2 日志规范

**日志级别**：
- `DEBUG`: 详细的调试信息
- `INFO`: 业务流程关键节点
- `WARNING`: 可恢复的异常
- `ERROR`: 严重错误

**日志示例**：
```python
logger.info("WebSocket connected", extra={
    'user_id': user_id,
    'sid': request.sid,
    'remote_addr': request.remote_addr
})

logger.error("Failed to send notification", extra={
    'room_id': room_id,
    'event': event,
    'error': str(e)
})
```

## 5. 环境配置规范

### 5.1 必需的环境变量

```bash
# 核心配置
SECRET_KEY=your-secret-key-here
REDIS_URL=redis://localhost:6379/0

# WebSocket 配置
SOCKETIO_ASYNC_MODE=threading  # 或 eventlet
SOCKETIO_CORS_ALLOWED_ORIGINS=*
```

### 5.2 开发环境 vs 生产环境

**开发环境** (`.env`):
```bash
APP_ENV=dev
DEBUG=True
SOCKETIO_ASYNC_MODE=threading
SOCKETIO_CORS_ALLOWED_ORIGINS=*
```

**生产环境**:
```bash
APP_ENV=prod
DEBUG=False
SOCKETIO_ASYNC_MODE=eventlet
SOCKETIO_CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

## 6. 故障排查规范

### 6.1 常见问题检查清单

**WebSocket 连接失败**：
1. [ ] 检查服务器是否运行
2. [ ] 检查 JWT token 是否有效
3. [ ] 检查 SECRET_KEY 是否一致
4. [ ] 检查 CORS 配置

**测试失败**：
1. [ ] 检查 Redis 是否运行
2. [ ] 检查环境变量配置
3. [ ] 检查依赖是否安装完整
4. [ ] 查看详细错误日志

**性能问题**：
1. [ ] 检查 Redis 连接数
2. [ ] 检查 WebSocket 连接数
3. [ ] 检查消息发送频率
4. [ ] 查看服务器资源使用

### 6.2 日志查看

**应用日志**：
```bash
# 查看实时日志
tail -f logs/app.log

# 搜索错误
grep ERROR logs/app.log
```

**Docker 日志**：
```bash
# 查看 Redis 日志
docker-compose logs redis

# 实时查看
docker-compose logs -f redis
```

## 7. 版本控制规范

### 7.1 提交信息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型 (type)**：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `test`: 测试相关
- `refactor`: 重构
- `style`: 代码格式
- `chore`: 构建/工具相关

**示例**：
```
feat(websocket): 添加房间订阅功能

- 实现 subscribe/unsubscribe 事件处理
- 添加房间权限验证
- 添加单元测试

Closes #123
```

### 7.2 分支管理

- `main`: 主分支，稳定版本
- `develop`: 开发分支
- `feature/websocket-phase1`: 功能分支
- `hotfix/websocket-auth`: 热修复分支

## 8. 文档更新规范

### 8.1 必须更新的文档

当添加新功能时，必须更新：

1. **API 文档** - 如果添加了新的 HTTP 端点
2. **事件文档** - 如果添加了新的 WebSocket 事件
3. **README** - 如果改变了使用方式
4. **测试文档** - 如果添加了新的测试

### 8.2 文档位置

- 需求文档：`.kiro/specs/websocket-notification-system/requirements.md`
- 设计文档：`.kiro/specs/websocket-notification-system/design.md`
- 任务列表：`.kiro/specs/websocket-notification-system/tasks.md`
- 开发规范：`.kiro/specs/websocket-notification-system/DEVELOPMENT_GUIDELINES.md`（本文档）

## 9. 性能优化规范

### 9.1 WebSocket 性能

- 单实例支持 500-1000 并发连接
- 消息延迟 < 500ms
- 心跳间隔 30 秒

### 9.2 监控指标

**必须监控的指标**：
- WebSocket 连接数
- 消息发送量
- 消息延迟
- 错误率
- Redis 连接数

## 10. 安全规范

### 10.1 认证

- 所有 WebSocket 连接必须通过 JWT 认证
- Token 过期时间：1 小时
- 使用 HS256 算法

### 10.2 授权

- 用户只能订阅自己加入的房间
- 验证房间权限
- 防止消息重放攻击

### 10.3 敏感信息

- 不在日志中记录 Token
- 不在 WebSocket 消息中传输敏感数据
- SECRET_KEY 必须使用环境变量

---

**文档版本**: 1.0  
**最后更新**: 2024-02-24  
**维护者**: 开发团队
