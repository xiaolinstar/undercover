# 前后端联调指南

## 🚀 服务器状态

### 当前运行的服务

✅ **后端服务器**: http://localhost:5001  
✅ **MySQL**: localhost:3306  
✅ **Redis**: localhost:6379  

### 健康检查

```bash
curl http://localhost:5001/health
```

响应：
```json
{
  "status": "healthy",
  "timestamp": 1771946280
}
```

## 📡 API 端点

### 1. 认证接口

#### POST /api/v1/auth/login
登录获取 JWT token

**请求**:
```bash
curl -X POST http://localhost:5001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"code": "test_code_123"}'
```

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "token": "mock_jwt_token_for_user_1001",
    "user": {
      "id": 1001,
      "openid": "mock_openid_code_test_",
      "nickname": "小明 (Mock Player)",
      "avatar_url": "https://example.com/avatar.png",
      "total_games": 10,
      "wins": 6
    }
  }
}
```

### 2. 房间接口

#### POST /api/v1/room/create
创建房间

**请求**:
```bash
curl -X POST http://localhost:5001/api/v1/room/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{}'
```

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "room_id": "8888",
    "host_id": 1001,
    "status": "WAITING",
    "config": {
      "player_count": 6,
      "undercover_count": 1,
      "whiteboard_count": 0
    }
  }
}
```

#### POST /api/v1/room/join
加入房间

**请求**:
```bash
curl -X POST http://localhost:5001/api/v1/room/join \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"room_id": "8888"}'
```

#### GET /api/v1/room/{room_id}
获取房间状态

**请求**:
```bash
curl http://localhost:5001/api/v1/room/8888 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "room_id": "8888",
    "host_id": 1001,
    "status": "waiting",
    "player_count": 3,
    "players": [
      {
        "uid": 1001,
        "seat": 1,
        "nickname": "小明",
        "avatar": "url",
        "is_ready": true,
        "is_eliminated": false
      }
    ]
  }
}
```

### 3. 游戏接口

#### POST /api/v1/game/start
开始游戏

**请求**:
```bash
curl -X POST http://localhost:5001/api/v1/game/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"room_id": "8888"}'
```

#### GET /api/v1/game/word
获取玩家词语

**请求**:
```bash
curl http://localhost:5001/api/v1/game/word \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "word": "苹果",
    "role": 1
  }
}
```

#### POST /api/v1/game/vote
投票淘汰玩家

**请求**:
```bash
curl -X POST http://localhost:5001/api/v1/game/vote \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"target_uid": 1002}'
```

#### GET /api/v1/game/sync/{room_id}
状态同步（增强版）

**请求**:
```bash
curl http://localhost:5001/api/v1/game/sync/8888 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "room_id": "8888",
    "status": "playing",
    "player_count": 4,
    "updated_at": 1708675200,
    "players": [
      {
        "openid": "user_123",
        "nickname": "玩家1",
        "seat": 1,
        "is_eliminated": false,
        "is_creator": true
      }
    ],
    "my_info": {
      "openid": "user_123",
      "seat": 1,
      "is_eliminated": false,
      "is_creator": true
    }
  }
}
```

## 🔌 WebSocket 连接

### 两种 WebSocket 协议

服务端同时支持两种 WebSocket 协议：

1. **Socket.IO**（用于 Web 端）
   - 地址：`ws://localhost:5001/socket.io/`
   - 协议：Socket.IO
   - 客户端：socket.io-client

2. **原生 WebSocket**（用于微信小程序）✅
   - 地址：`ws://localhost:5001/ws`
   - 协议：标准 WebSocket
   - 客户端：wx.connectSocket

### 微信小程序连接

**重要**: 微信小程序必须使用原生 WebSocket 端点！

详细的微信小程序连接指南请查看：
- **[MINIPROGRAM_WEBSOCKET_GUIDE.md](MINIPROGRAM_WEBSOCKET_GUIDE.md)** - 完整的小程序 WebSocket 使用说明

### Web 端连接（Socket.IO）

#### 连接地址
```
ws://localhost:5001/socket.io/?EIO=4&transport=websocket
```

### 连接流程

#### 1. 生成 JWT Token

首先需要通过 `/api/v1/auth/login` 获取 token，或者使用测试 token：

```python
import jwt
import time

token = jwt.encode(
    {
        'user_id': 'test_user_123',
        'exp': int(time.time()) + 3600
    },
    'your-secret-key-here',  # 与 .env 中的 SECRET_KEY 一致
    algorithm='HS256'
)
print(token)
```

#### 2. 建立 WebSocket 连接

使用 Socket.IO 客户端连接：

**JavaScript 示例**:
```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:5001', {
  auth: {
    token: 'YOUR_JWT_TOKEN'
  },
  transports: ['websocket']
});

// 监听连接成功
socket.on('connected', (data) => {
  console.log('Connected:', data);
  // data: { connection_id: '...', user_id: '...' }
});

// 监听连接错误
socket.on('connect_error', (error) => {
  console.error('Connection error:', error);
});
```

**Python 示例**:
```python
import socketio
import jwt
import time

# 生成 token
token = jwt.encode(
    {'user_id': 'test_user_123', 'exp': int(time.time()) + 3600},
    'your-secret-key-here',
    algorithm='HS256'
)

# 创建客户端
sio = socketio.Client()

# 连接
sio.connect('http://localhost:5001', auth={'token': token})

# 监听事件
@sio.on('connected')
def on_connected(data):
    print('Connected:', data)

sio.wait()
```

#### 3. 订阅房间

连接成功后，订阅房间以接收通知：

```javascript
// 订阅房间
socket.emit('subscribe', { room_id: '8888' });

// 监听订阅成功
socket.on('subscribed', (data) => {
  console.log('Subscribed to room:', data);
  // data: { room_id: '8888', success: true }
});

// 监听订阅错误
socket.on('subscribe_error', (data) => {
  console.error('Subscribe error:', data);
  // data: { error: 'ROOM_NOT_FOUND', message: '房间不存在' }
});
```

#### 4. 接收游戏事件

订阅成功后，会自动接收房间内的所有事件：

```javascript
// 玩家加入
socket.on('room.player_joined', (data) => {
  console.log('Player joined:', data);
  // data: {
  //   event: 'room.player_joined',
  //   room_id: '8888',
  //   timestamp: 1708675200,
  //   data: { player_count: 4, hint: '玩家2 加入了房间' }
  // }
});

// 游戏开始
socket.on('game.started', (data) => {
  console.log('Game started:', data);
  // data: {
  //   event: 'game.started',
  //   room_id: '8888',
  //   timestamp: 1708675200,
  //   data: { 
  //     player_count: 4, 
  //     undercover_count: 1,
  //     hint: '游戏已开始，请查看您的词语' 
  //   }
  // }
});

// 投票提交
socket.on('vote.submitted', (data) => {
  console.log('Vote submitted:', data);
  // data: {
  //   event: 'vote.submitted',
  //   room_id: '8888',
  //   timestamp: 1708675200,
  //   data: { 
  //     target_index: 2,
  //     eliminated_count: 1,
  //     hint: '玩家2 被投票淘汰' 
  //   }
  // }
});

// 游戏结束
socket.on('game.ended', (data) => {
  console.log('Game ended:', data);
  // data: {
  //   event: 'game.ended',
  //   room_id: '8888',
  //   timestamp: 1708675200,
  //   data: { 
  //     winner_team: 'civilian',
  //     hint: '游戏结束！平民获胜，成功找出了所有卧底！' 
  //   }
  // }
});
```

#### 5. 心跳保活

定期发送 ping 保持连接：

```javascript
// 每 30 秒发送一次 ping
setInterval(() => {
  socket.emit('ping');
}, 30000);

// 监听 pong 响应
socket.on('pong', () => {
  console.log('Pong received');
});
```

#### 6. 取消订阅

离开房间时取消订阅：

```javascript
socket.emit('unsubscribe', { room_id: '8888' });
```

## 🎮 完整游戏流程示例

### 1. 用户 A 创建房间

```bash
# 1. 登录获取 token
TOKEN_A=$(curl -s -X POST http://localhost:5001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"code": "user_a"}' | jq -r '.data.token')

# 2. 创建房间
ROOM_ID=$(curl -s -X POST http://localhost:5001/api/v1/room/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_A" \
  -d '{}' | jq -r '.data.room_id')

echo "Room created: $ROOM_ID"

# 3. WebSocket 连接并订阅房间
# (使用前端代码连接)
```

### 2. 用户 B 加入房间

```bash
# 1. 登录获取 token
TOKEN_B=$(curl -s -X POST http://localhost:5001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"code": "user_b"}' | jq -r '.data.token')

# 2. 加入房间
curl -X POST http://localhost:5001/api/v1/room/join \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_B" \
  -d "{\"room_id\": \"$ROOM_ID\"}"

# 3. WebSocket 连接并订阅房间
# 用户 A 会收到 room.player_joined 通知
```

### 3. 开始游戏

```bash
# 房主（用户 A）开始游戏
curl -X POST http://localhost:5001/api/v1/game/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_A" \
  -d "{\"room_id\": \"$ROOM_ID\"}"

# 所有玩家会收到 game.started 通知
```

### 4. 查看词语

```bash
# 用户 A 查看词语
curl http://localhost:5001/api/v1/game/word \
  -H "Authorization: Bearer $TOKEN_A"

# 用户 B 查看词语
curl http://localhost:5001/api/v1/game/word \
  -H "Authorization: Bearer $TOKEN_B"
```

### 5. 投票淘汰

```bash
# 房主投票淘汰玩家
curl -X POST http://localhost:5001/api/v1/game/vote \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_A" \
  -d '{"target_uid": 1002}'

# 所有玩家会收到 vote.submitted 通知
# 如果游戏结束，还会收到 game.ended 通知
```

## 🔍 调试工具

### 1. API 文档

访问 Swagger UI 查看完整 API 文档：
```
http://localhost:5001/apidocs/
```

### 2. WebSocket 测试脚本

使用项目提供的测试脚本：
```bash
python test_websocket_basic.py
```

### 3. 查看服务器日志

实时查看服务器输出，了解请求处理情况。

### 4. Redis 数据查看

```bash
# 连接 Redis
docker exec -it undercover-redis redis-cli

# 查看所有房间
KEYS room:*

# 查看房间详情
GET room:8888

# 查看所有用户
KEYS user:*
```

### 5. MySQL 数据查看

```bash
# 连接 MySQL
docker exec -it undercover-mysql mysql -u root -proot_password undercover_db

# 查看游戏记录
SELECT * FROM game_records ORDER BY ended_at DESC LIMIT 10;

# 查看用户统计
SELECT openid, nickname, total_games, wins FROM users;
```

## ⚠️ 常见问题

### 1. WebSocket 连接失败

**问题**: Connection rejected: invalid token

**解决**:
- 确保 token 使用正确的 SECRET_KEY 生成
- 检查 token 是否过期
- 确认 token 格式正确（JWT）

### 2. 订阅房间失败

**问题**: Subscribe error: ROOM_NOT_FOUND

**解决**:
- 确认房间 ID 正确
- 检查房间是否已创建
- 使用 Redis CLI 查看房间数据

**问题**: Subscribe error: PERMISSION_DENIED

**解决**:
- 确认用户已加入房间
- 检查用户 ID 是否正确

### 3. 收不到通知

**问题**: 订阅成功但收不到事件通知

**解决**:
- 确认已正确订阅房间
- 检查事件监听器是否正确注册
- 查看服务器日志确认通知是否发送

### 4. CORS 错误

**问题**: 跨域请求被阻止

**解决**:
- 检查 `.env` 中的 `SOCKETIO_CORS_ALLOWED_ORIGINS` 配置
- 开发环境可以设置为 `*`
- 生产环境应设置为具体的前端域名

## 📞 技术支持

如果遇到问题，请：

1. 查看服务器日志
2. 检查 Redis 和 MySQL 连接状态
3. 使用测试脚本验证功能
4. 查看相关文档：
   - [QUICK_START.md](QUICK_START.md)
   - [PHASE1_COMPLETION_REPORT.md](PHASE1_COMPLETION_REPORT.md)
   - [PHASE2_COMPLETION_REPORT.md](PHASE2_COMPLETION_REPORT.md)

---

**服务器地址**: http://localhost:5001  
**WebSocket 地址**: ws://localhost:5001/socket.io/  
**API 文档**: http://localhost:5001/apidocs/  
**健康检查**: http://localhost:5001/health

祝联调顺利！🎉
