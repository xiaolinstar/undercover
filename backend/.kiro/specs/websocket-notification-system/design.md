# WebSocket 实时通知系统 - 设计文档

## 1. 架构概览

### 1.1 整体架构（单实例简化版）

```
┌─────────────────┐         ┌──────────────────┐
│  小程序客户端    │◄───WS───►│  Flask-SocketIO  │
│                 │         │   WebSocket      │
│  - 订阅房间      │         │   Server         │
│  - 接收通知      │         │  (单实例部署)     │
│  - HTTP拉取数据  │         └────────┬─────────┘
└────────┬────────┘                  │
         │                           │
         │ HTTP API                  │ 读写
         │                           │
         ▼                           ▼
┌─────────────────┐         ┌──────────────────┐
│  Flask HTTP     │◄────────►│  Redis + MySQL   │
│  API Endpoints  │         │  - Room State    │
│                 │         │  - User Data     │
│  - /api/game/*  │         │  - Game Records  │
│  - /api/room/*  │         └──────────────────┘
└─────────────────┘
```

**说明**：
- 单实例部署，无需 Redis Pub/Sub
- WebSocket 连接在进程内管理
- 专注于游戏事件通知，不包含聊天等复杂功能

### 1.2 核心设计原则

1. **职责分离**: WebSocket 仅推送事件通知，HTTP API 负责数据传输
2. **简化优先**: 单实例部署，避免过度设计
3. **可扩展性**: 架构支持未来扩展到多实例（但当前不实现）
4. **专注核心**: 只实现游戏事件通知，不实现聊天、社交等功能

## 2. 技术选型

### 2.1 WebSocket 框架
- **选择**: flask-socketio + python-socketio
- **理由**:
  - 与现有 Flask 架构无缝集成
  - 支持 WebSocket 和 Long Polling 降级
  - 单实例部署简单，无需额外配置
  - 成熟稳定，文档完善

### 2.2 消息分发
- **选择**: flask-socketio 内置的 room 机制
- **理由**:
  - 进程内管理，简单高效
  - 无需 Redis Pub/Sub
  - 延迟更低（< 10ms）
  - 未来可轻松升级到 Redis 消息队列


## 3. 核心组件设计

### 3.1 NotificationService (通知服务)

**职责**: 统一的通知发送接口，屏蔽底层实现细节

**接口设计**:
```python
class NotificationService:
    def __init__(self, socketio):
        self.socketio = socketio
    
    def notify_room(
        self, 
        room_id: str, 
        event: str, 
        data: dict,
        exclude_user: str | None = None
    ) -> None:
        """
        向房间内所有订阅者发送通知
        
        Args:
            room_id: 房间ID
            event: 事件类型（如 'room.player_joined'）
            data: 事件数据（轻量级提示信息）
            exclude_user: 排除的用户ID（可选，如操作发起者）
        """
        message = {
            "event": event,
            "room_id": room_id,
            "timestamp": int(time.time()),
            "data": data
        }
        
        # 使用 flask-socketio 的 room 机制直接发送
        self.socketio.emit(
            event,
            message,
            room=room_id,
            skip_sid=exclude_user  # 排除特定用户
        )
```

**实现要点**:
- 单实例部署，直接通过 socketio.emit() 发送
- 使用 flask-socketio 内置的 room 机制
- 无需 Redis Pub/Sub

### 3.2 连接管理（简化版）

**职责**: 管理 WebSocket 连接、房间订阅关系

**实现方式**:
- 使用 flask-socketio 内置的 session 和 room 机制
- 连接信息存储在进程内存中
- 无需 Redis 存储连接映射

**核心方法**:
```python
# 连接时存储用户信息
@socketio.on('connect')
def handle_connect(auth):
    session['user_id'] = user_id  # 存储在 flask session
    
# 订阅房间
@socketio.on('subscribe')
def handle_subscribe(data):
    room_id = data['room_id']
    join_room(room_id)  # flask-socketio 内置方法
    
# 取消订阅
@socketio.on('unsubscribe')
def handle_unsubscribe(data):
    room_id = data['room_id']
    leave_room(room_id)  # flask-socketio 内置方法
```


### 3.3 WebSocket 事件处理器

**文件**: `src/websocket/handlers.py`

**核心事件**:
```python
@socketio.on('connect')
def handle_connect(auth):
    """处理连接建立"""
    # 1. 验证 JWT token
    # 2. 存储用户信息到 session
    # 3. 返回连接成功消息

@socketio.on('subscribe')
def handle_subscribe(data):
    """处理房间订阅"""
    # 1. 验证用户是否在房间内
    # 2. 加入 SocketIO room
    # 3. 返回订阅成功消息

@socketio.on('unsubscribe')
def handle_unsubscribe(data):
    """处理取消订阅"""
    # 1. 离开 SocketIO room

@socketio.on('disconnect')
def handle_disconnect():
    """处理连接断开"""
    # 1. 清理 session 信息
    # 2. 自动离开所有 room

@socketio.on('ping')
def handle_ping():
    """处理心跳"""
    emit('pong')
```

**说明**: 单实例部署下，无需复杂的连接管理，flask-socketio 自动处理


## 4. 事件定义

### 4.1 事件命名规范

格式: `{domain}.{action}`

示例:
- `room.player_joined` - 房间域，玩家加入动作
- `game.started` - 游戏域，开始动作
- `vote.submitted` - 投票域，提交动作

### 4.2 事件消息格式

**统一格式**:
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

**字段说明**:
- `event`: 事件类型（必需）
- `room_id`: 房间ID（必需）
- `timestamp`: Unix 时间戳（必需）
- `data`: 事件数据（可选，轻量级提示信息）

### 4.3 完整事件列表

#### 房间事件 (room.*)
1. `room.player_joined` - 玩家加入
2. `room.player_left` - 玩家离开
3. `room.player_ready` - 玩家准备
4. `room.disbanded` - 房间解散

#### 游戏事件 (game.*)
1. `game.started` - 游戏开始
2. `game.phase_changed` - 阶段变更
3. `game.player_eliminated` - 玩家淘汰
4. `game.ended` - 游戏结束

#### 投票事件 (vote.*)
1. `vote.submitted` - 投票提交
2. `vote.completed` - 投票完成


## 5. 业务集成点

### 5.1 GameService 集成

在现有的 `GameService` 中添加通知发送：

```python
class GameService:
    def __init__(
        self, 
        room_repo: RoomRepository, 
        user_repo: UserRepository,
        push_service: PushService | None = None,
        notification_service: NotificationService | None = None  # 新增
    ):
        self.notification = notification_service
    
    def join_room(self, user_id: str, room_id: str):
        # ... 现有逻辑 ...
        
        # 发送通知
        if self.notification:
            self.notification.notify_room(
                room_id=room_id,
                event="room.player_joined",
                data={
                    "player_count": room.get_player_count(),
                    "hint": "新玩家加入"
                },
                exclude_user=user_id  # 排除操作者自己
            )
    
    def start_game(self, user_id: str):
        # ... 现有逻辑 ...
        
        # 发送通知
        if self.notification:
            self.notification.notify_room(
                room_id=room.room_id,
                event="game.started",
                data={"hint": "游戏已开始，请查看你的词语"}
            )
    
    def vote_player(self, user_id: str, target_index: int):
        # ... 现有逻辑 ...
        
        # 发送投票通知
        if self.notification:
            self.notification.notify_room(
                room_id=room.room_id,
                event="vote.submitted",
                data={
                    "voted_count": len(room.eliminated),
                    "total_count": room.get_player_count(),
                    "hint": f"{len(room.eliminated)}/{room.get_player_count()} 玩家已被淘汰"
                }
            )
        
        # 如果游戏结束，发送结束通知
        if game_ended:
            if self.notification:
                self.notification.notify_room(
                    room_id=room.room_id,
                    event="game.ended",
                    data={
                        "winner": winner_team,
                        "hint": result_message
                    }
                )
```

### 5.2 集成位置总结

| 业务方法 | 触发事件 | 集成位置 |
|---------|---------|---------|
| `create_room()` | - | 无需通知（创建者自己知道） |
| `join_room()` | `room.player_joined` | 加入成功后 |
| `start_game()` | `game.started` | 发牌完成后 |
| `vote_player()` | `vote.submitted` | 投票记录后 |
| `vote_player()` | `game.ended` | 游戏结束判定后 |


## 6. HTTP API 增强

### 6.1 房间状态同步接口

**现有接口**: `GET /api/game/sync/{room_id}`

**增强内容**:
```python
@api_bp.route("/game/sync/<room_id>", methods=["GET"])
@login_required
def sync_room(room_id):
    """
    获取房间完整状态
    客户端收到 WS 通知后调用此接口获取详细数据
    """
    user_id = get_current_user_id()
    
    # 验证用户是否在房间内
    user = user_repo.get(user_id)
    if not user or user.current_room != room_id:
        return jsonify({
            "code": 403,
            "message": "无权访问该房间"
        }), 403
    
    # 获取房间信息
    room = room_repo.get(room_id)
    if not room:
        return jsonify({
            "code": 404,
            "message": "房间不存在"
        }), 404
    
    # 构建响应数据
    response_data = {
        "room_id": room.room_id,
        "status": room.status.value,
        "current_round": room.current_round,
        "updated_at": room.last_active.isoformat(),  # 版本控制
        "players": [],
        "my_info": None
    }
    
    # 玩家列表
    for i, player_id in enumerate(room.players):
        player = user_repo.get(player_id)
        player_info = {
            "uid": player_id,
            "seat": i + 1,
            "nickname": player.nickname if player else f"玩家{i+1}",
            "is_host": player_id == room.creator,
            "is_alive": player_id not in room.eliminated,
            "is_ready": False  # 未来扩展
        }
        response_data["players"].append(player_info)
        
        # 当前用户信息
        if player_id == user_id:
            response_data["my_info"] = {
                "seat": i + 1,
                "word": room.words.get("undercover" if player_id in room.undercovers else "civilian"),
                "role": 2 if player_id in room.undercovers else 1,
                "is_alive": player_id not in room.eliminated
            }
    
    return jsonify({
        "code": 200,
        "message": "success",
        "data": response_data
    })
```

### 6.2 批量状态查询接口（可选）

```python
@api_bp.route("/game/sync/batch", methods=["POST"])
@login_required
def sync_rooms_batch():
    """
    批量查询多个房间状态
    用于用户同时在多个房间的场景
    """
    data = request.get_json()
    room_ids = data.get("room_ids", [])
    
    # 限制批量查询数量
    if len(room_ids) > 10:
        return jsonify({
            "code": 400,
            "message": "最多同时查询10个房间"
        }), 400
    
    # ... 实现逻辑 ...
```


## 7. 安全设计

### 7.1 WebSocket 认证

**方案**: JWT Token 认证

**流程**:
```
1. 客户端通过 HTTP API 登录获取 JWT token
2. 建立 WebSocket 连接时在 auth 参数中传递 token
3. 服务器验证 token 有效性
4. 验证通过后建立连接，否则拒绝
```

**实现**:
```python
@socketio.on('connect')
def handle_connect(auth):
    if not auth or 'token' not in auth:
        return False  # 拒绝连接
    
    try:
        # 验证 JWT token
        payload = jwt.decode(
            auth['token'], 
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        user_id = payload.get('user_id')
        
        # 存储用户信息到 session
        session['user_id'] = user_id
        
        # 注册连接
        connection_manager.register_connection(user_id, request.sid)
        
        emit('connected', {
            'event': 'connected',
            'data': {
                'connection_id': request.sid,
                'user_id': user_id
            }
        })
        
    except jwt.InvalidTokenError:
        return False  # 拒绝连接
```

### 7.2 房间订阅权限验证

**规则**: 用户只能订阅自己加入的房间

```python
@socketio.on('subscribe')
def handle_subscribe(data):
    user_id = session.get('user_id')
    room_id = data.get('room_id')
    
    # 验证用户是否在房间内
    user = user_repo.get(user_id)
    if not user or user.current_room != room_id:
        emit('subscribe_error', {
            'event': 'subscribe_error',
            'room_id': room_id,
            'data': {
                'error': 'PERMISSION_DENIED',
                'message': '您不在该房间内'
            }
        })
        return
    
    # 加入 SocketIO room
    join_room(room_id)
    
    # 注册订阅关系
    connection_manager.subscribe_room(user_id, room_id)
    
    emit('subscribed', {
        'event': 'subscribed',
        'room_id': room_id,
        'data': {'success': True}
    })
```

### 7.3 消息防重放

**方案**: 时间戳验证

```python
def validate_message_timestamp(timestamp: int) -> bool:
    """验证消息时间戳，防止重放攻击"""
    current_time = int(time.time())
    # 允许 5 分钟的时间差
    return abs(current_time - timestamp) <= 300
```


## 8. 性能优化

### 8.1 连接池管理

**问题**: 大量连接可能导致内存占用过高

**方案**:
- 限制单个服务实例最大连接数（如 5000）
- 超过限制时拒绝新连接，返回 503
- 定期清理僵尸连接（超过 5 分钟无心跳）

```python
class ConnectionLimiter:
    MAX_CONNECTIONS = 5000
    
    def can_accept_connection(self) -> bool:
        current_count = self.get_connection_count()
        return current_count < self.MAX_CONNECTIONS
```

### 8.2 消息批量发送

**问题**: 频繁的小消息发送影响性能

**方案**: 对于非紧急消息，使用批量发送

```python
class MessageBatcher:
    def __init__(self, interval=0.1):
        self.interval = interval
        self.buffer = []
    
    def add_message(self, room_id, event, data):
        self.buffer.append((room_id, event, data))
    
    def flush(self):
        """批量发送缓冲区中的消息"""
        for room_id, event, data in self.buffer:
            socketio.emit(event, data, room=room_id)
        self.buffer.clear()
```

### 8.3 Redis 连接复用

**方案**: 使用连接池，避免频繁创建连接

```python
redis_pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    max_connections=50,
    decode_responses=False
)
redis_client = redis.Redis(connection_pool=redis_pool)
```

### 8.4 消息压缩（可选）

**场景**: 大量客户端同时在线时

**方案**: 对消息进行 gzip 压缩

```python
import gzip
import json

def compress_message(data: dict) -> bytes:
    json_str = json.dumps(data)
    return gzip.compress(json_str.encode('utf-8'))
```


## 9. 监控和可观测性

### 9.1 关键指标

**连接指标**:
- `ws_connections_total`: 当前连接数
- `ws_connections_created`: 累计建立连接数
- `ws_connections_closed`: 累计断开连接数
- `ws_connection_duration_seconds`: 连接持续时间

**消息指标**:
- `ws_messages_sent_total`: 发送消息总数（按事件类型分组）
- `ws_messages_received_total`: 接收消息总数
- `ws_message_send_duration_seconds`: 消息发送延迟

**订阅指标**:
- `ws_room_subscribers_total`: 房间订阅者数量（按房间分组）
- `ws_subscribe_errors_total`: 订阅失败次数

### 9.2 Prometheus 集成

```python
from prometheus_client import Counter, Gauge, Histogram

# 定义指标
ws_connections = Gauge(
    'ws_connections_total',
    'Current number of WebSocket connections'
)

ws_messages_sent = Counter(
    'ws_messages_sent_total',
    'Total number of messages sent',
    ['event_type']
)

ws_message_latency = Histogram(
    'ws_message_send_duration_seconds',
    'Message send latency'
)

# 在代码中使用
@socketio.on('connect')
def handle_connect(auth):
    ws_connections.inc()
    # ...

@socketio.on('disconnect')
def handle_disconnect():
    ws_connections.dec()
    # ...

def send_notification(room_id, event, data):
    with ws_message_latency.time():
        socketio.emit(event, data, room=room_id)
        ws_messages_sent.labels(event_type=event).inc()
```

### 9.3 日志规范

**连接日志**:
```python
logger.info("WebSocket connected", extra={
    'user_id': user_id,
    'connection_id': request.sid,
    'remote_addr': request.remote_addr
})
```

**订阅日志**:
```python
logger.info("Room subscribed", extra={
    'user_id': user_id,
    'room_id': room_id,
    'subscriber_count': len(subscribers)
})
```

**错误日志**:
```python
logger.error("Subscription failed", extra={
    'user_id': user_id,
    'room_id': room_id,
    'error': str(e)
})
```


## 10. 部署配置

### 10.1 依赖安装

**requirements.txt 新增**:
```
flask-socketio==5.3.6
python-socketio==5.11.1
eventlet==0.35.2  # 推荐使用 eventlet
```

### 10.2 应用启动配置

**开发环境**:
```python
# src/main.py
from src.app_factory import AppFactory

app, socketio = AppFactory.create_app()

if __name__ == "__main__":
    # 单实例模式，无需 message_queue
    socketio.run(
        app,
        host="0.0.0.0",
        port=5001,
        debug=True
    )
```

**生产环境** (Gunicorn + eventlet):
```bash
gunicorn --worker-class eventlet \
         --workers 1 \
         --bind 0.0.0.0:5001 \
         --timeout 120 \
         "src.main:app"
```

**注意**: 单实例部署时，workers 设置为 1

### 10.3 Nginx 配置

```nginx
server {
    listen 80;
    server_name api.example.com;
    
    # WebSocket 路径
    location /socket.io/ {
        proxy_pass http://127.0.0.1:5001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # 超时设置
        proxy_connect_timeout 7d;
        proxy_send_timeout 7d;
        proxy_read_timeout 7d;
    }
    
    # HTTP API 路径
    location /api/ {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 10.4 环境变量

**.env 新增**:
```bash
# WebSocket 配置
SOCKETIO_ASYNC_MODE=eventlet  # 或 threading
SOCKETIO_CORS_ALLOWED_ORIGINS=*  # 生产环境应限制具体域名

# 未来多实例扩展时使用（当前不需要）
# SOCKETIO_MESSAGE_QUEUE=redis://localhost:6379/1
```


## 11. 测试策略

### 11.1 单元测试

**测试 NotificationService**:
```python
def test_notify_room(mock_redis, mock_socketio):
    service = NotificationService(mock_socketio, mock_redis)
    
    service.notify_room(
        room_id="8888",
        event="room.player_joined",
        data={"player_count": 4}
    )
    
    # 验证消息发布到 Redis
    mock_redis.publish.assert_called_once()
    
    # 验证消息格式
    call_args = mock_redis.publish.call_args
    assert call_args[0][0] == "room:8888:events"
```

**测试 ConnectionManager**:
```python
def test_subscribe_room(connection_manager):
    result = connection_manager.subscribe_room("user123", "8888")
    assert result is True
    
    subscribers = connection_manager.get_room_subscribers("8888")
    assert "user123" in subscribers
```

### 11.2 集成测试

**测试 WebSocket 连接流程**:
```python
def test_websocket_connection_flow(socketio_client):
    # 1. 建立连接
    client = socketio_client.connect(
        'http://localhost:5001',
        auth={'token': 'valid_jwt_token'}
    )
    
    # 2. 验证连接成功
    received = client.get_received()
    assert received[0]['event'] == 'connected'
    
    # 3. 订阅房间
    client.emit('subscribe', {'room_id': '8888'})
    
    # 4. 验证订阅成功
    received = client.get_received()
    assert received[0]['event'] == 'subscribed'
```

**测试事件通知**:
```python
def test_room_notification(socketio_client, game_service):
    # 客户端 A 和 B 都订阅房间 8888
    client_a = socketio_client.connect(auth={'token': token_a})
    client_b = socketio_client.connect(auth={'token': token_b})
    
    client_a.emit('subscribe', {'room_id': '8888'})
    client_b.emit('subscribe', {'room_id': '8888'})
    
    # 客户端 C 加入房间
    game_service.join_room('user_c', '8888')
    
    # 验证 A 和 B 都收到通知
    received_a = client_a.get_received()
    received_b = client_b.get_received()
    
    assert any(msg['event'] == 'room.player_joined' for msg in received_a)
    assert any(msg['event'] == 'room.player_joined' for msg in received_b)
```

### 11.3 压力测试

**测试并发连接**:
```python
import asyncio
from socketio import AsyncClient

async def connect_client(index):
    client = AsyncClient()
    await client.connect('http://localhost:5001')
    await asyncio.sleep(60)  # 保持连接 1 分钟
    await client.disconnect()

async def test_concurrent_connections():
    # 模拟 1000 个并发连接
    tasks = [connect_client(i) for i in range(1000)]
    await asyncio.gather(*tasks)
```


## 12. 客户端实现指南

### 12.1 小程序 WebSocket 连接

```javascript
// utils/websocket.js
class WebSocketManager {
  constructor() {
    this.socket = null;
    this.connected = false;
    this.subscribedRooms = new Set();
  }
  
  connect(token) {
    return new Promise((resolve, reject) => {
      this.socket = wx.connectSocket({
        url: 'wss://api.example.com/socket.io/',
        header: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      this.socket.onOpen(() => {
        console.log('WebSocket connected');
        this.connected = true;
        this.startHeartbeat();
        resolve();
      });
      
      this.socket.onMessage((res) => {
        this.handleMessage(JSON.parse(res.data));
      });
      
      this.socket.onError((err) => {
        console.error('WebSocket error:', err);
        reject(err);
      });
      
      this.socket.onClose(() => {
        console.log('WebSocket closed');
        this.connected = false;
        this.reconnect();
      });
    });
  }
  
  subscribe(roomId) {
    if (!this.connected) {
      console.warn('WebSocket not connected');
      return;
    }
    
    this.socket.send({
      data: JSON.stringify({
        action: 'subscribe',
        room_id: roomId
      })
    });
    
    this.subscribedRooms.add(roomId);
  }
  
  handleMessage(message) {
    const { event, room_id, data } = message;
    
    switch(event) {
      case 'room.player_joined':
        this.onPlayerJoined(room_id, data);
        break;
      case 'game.started':
        this.onGameStarted(room_id, data);
        break;
      // ... 其他事件处理
    }
  }
  
  onPlayerJoined(roomId, data) {
    // 收到通知后，调用 HTTP API 获取最新数据
    wx.request({
      url: `https://api.example.com/api/game/sync/${roomId}`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${this.token}`
      },
      success: (res) => {
        // 更新页面数据
        this.updateRoomData(res.data.data);
      }
    });
  }
  
  startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      if (this.connected) {
        this.socket.send({
          data: JSON.stringify({ action: 'ping' })
        });
      }
    }, 30000);  // 每 30 秒发送一次心跳
  }
  
  reconnect() {
    // 指数退避重连
    setTimeout(() => {
      this.connect(this.token).then(() => {
        // 重新订阅之前的房间
        this.subscribedRooms.forEach(roomId => {
          this.subscribe(roomId);
        });
      });
    }, 1000);
  }
}

export default new WebSocketManager();
```

### 12.2 降级方案

```javascript
// 当 WebSocket 不可用时，降级为轮询
class PollingFallback {
  constructor(roomId, interval = 3000) {
    this.roomId = roomId;
    this.interval = interval;
    this.timer = null;
  }
  
  start() {
    this.timer = setInterval(() => {
      this.fetchRoomState();
    }, this.interval);
  }
  
  stop() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }
  
  fetchRoomState() {
    wx.request({
      url: `https://api.example.com/api/game/sync/${this.roomId}`,
      method: 'GET',
      success: (res) => {
        // 更新页面数据
        this.updateRoomData(res.data.data);
      }
    });
  }
}
```


## 13. 故障处理和容错

### 13.1 常见故障场景

#### 场景 1: Redis Pub/Sub 延迟
**症状**: 消息延迟超过 1 秒
**原因**: Redis 负载过高或网络问题
**处理**:
- 监控 Redis 延迟指标
- 考虑使用 Redis Cluster 分散负载
- 客户端定期轮询兜底

#### 场景 2: WebSocket 连接频繁断开
**症状**: 客户端频繁重连
**原因**: 
- Nginx 超时配置过短
- 服务器资源不足
- 网络不稳定

**处理**:
- 调整 Nginx 超时配置（proxy_read_timeout）
- 增加服务器资源
- 客户端实现指数退避重连

#### 场景 3: 消息丢失
**症状**: 客户端未收到某些通知
**原因**:
- 客户端断线期间的消息
- Redis Pub/Sub 不保证消息持久化

**处理**:
- 客户端重连后主动调用 HTTP API 同步状态
- 在 HTTP 响应中包含 `updated_at` 字段
- 客户端比对本地和服务器的时间戳

### 13.2 优雅关闭

```python
import signal
import sys

def graceful_shutdown(signum, frame):
    """优雅关闭服务"""
    logger.info("Received shutdown signal, closing connections...")
    
    # 1. 停止接受新连接
    socketio.stop()
    
    # 2. 通知所有客户端即将关闭
    socketio.emit('server_shutdown', {
        'event': 'server_shutdown',
        'data': {
            'message': '服务器即将重启，请稍后重连',
            'reconnect_after': 10
        }
    }, broadcast=True)
    
    # 3. 等待消息发送完成
    time.sleep(2)
    
    # 4. 关闭 Redis 连接
    redis_client.close()
    
    logger.info("Shutdown complete")
    sys.exit(0)

# 注册信号处理
signal.signal(signal.SIGTERM, graceful_shutdown)
signal.signal(signal.SIGINT, graceful_shutdown)
```

### 13.3 熔断机制

```python
class CircuitBreaker:
    """熔断器：防止故障扩散"""
    
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e
    
    def on_success(self):
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.warning("Circuit breaker opened")

# 使用示例
redis_breaker = CircuitBreaker()

def publish_with_breaker(channel, message):
    return redis_breaker.call(redis_client.publish, channel, message)
```


## 14. 实现检查清单

### 14.1 Phase 1: 基础设施（必需）
- [ ] 安装 flask-socketio 和相关依赖
- [ ] 创建 NotificationService 类
- [ ] 创建 ConnectionManager 类
- [ ] 实现 WebSocket 连接认证（JWT）
- [ ] 实现房间订阅/取消订阅
- [ ] 实现 Redis Pub/Sub 监听器
- [ ] 配置 SocketIO 使用 Redis 消息队列

### 14.2 Phase 2: 核心事件（必需）
- [ ] 定义所有事件类型常量
- [ ] 在 GameService.join_room() 中集成通知
- [ ] 在 GameService.start_game() 中集成通知
- [ ] 在 GameService.vote_player() 中集成通知
- [ ] 增强 HTTP API /api/game/sync 接口
- [ ] 添加 updated_at 字段用于版本控制

### 14.3 Phase 3: 高级功能（推荐）
- [ ] 实现心跳保活机制
- [ ] 实现断线重连逻辑（客户端）
- [ ] 实现订阅恢复机制
- [ ] 添加投票进度通知
- [ ] 实现批量状态查询接口

### 14.4 Phase 4: 监控和优化（推荐）
- [ ] 集成 Prometheus 指标
- [ ] 添加连接数监控
- [ ] 添加消息延迟监控
- [ ] 实现连接数限制
- [ ] 实现消息批量发送（可选）
- [ ] 添加熔断机制

### 14.5 Phase 5: 测试和文档（必需）
- [ ] 编写 NotificationService 单元测试
- [ ] 编写 ConnectionManager 单元测试
- [ ] 编写 WebSocket 集成测试
- [ ] 编写压力测试
- [ ] 更新 API 文档
- [ ] 编写客户端接入文档

### 14.6 Phase 6: 部署准备（必需）
- [ ] 配置 Nginx WebSocket 代理
- [ ] 配置 Gunicorn + eventlet
- [ ] 添加环境变量配置
- [ ] 实现优雅关闭
- [ ] 配置日志输出
- [ ] 准备监控告警规则

## 15. 风险评估

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| WebSocket 连接不稳定 | 高 | 中 | 实现自动重连 + HTTP 降级 |
| Redis Pub/Sub 延迟 | 中 | 低 | 监控 + 客户端轮询兜底 |
| 消息风暴 | 高 | 中 | 客户端随机延迟 + Redis 缓存 |
| 内存泄漏 | 高 | 低 | 定期清理 + 连接数限制 |
| 跨实例消息丢失 | 中 | 低 | Redis Pub/Sub 可靠性高 |

## 16. 后续优化方向

1. **消息优先级**: 重要消息（游戏结束）优先投递
2. **离线消息**: 存储用户离线期间的消息，上线后推送
3. **消息去重**: 防止客户端收到重复通知
4. **智能降级**: 根据网络质量自动切换 WS/轮询
5. **消息压缩**: 对大量消息进行 gzip 压缩
6. **房间分组**: 支持房间分组广播（如大厅广播）
7. **私聊消息**: 支持玩家之间的私聊
8. **消息历史**: 保存最近 N 条消息供客户端查询

## 17. 参考资料

- [Flask-SocketIO 官方文档](https://flask-socketio.readthedocs.io/)
- [Socket.IO 协议规范](https://socket.io/docs/v4/)
- [Redis Pub/Sub 文档](https://redis.io/docs/manual/pubsub/)
- [WebSocket RFC 6455](https://datatracker.ietf.org/doc/html/rfc6455)
- [JWT 认证最佳实践](https://jwt.io/introduction)

---

**文档版本**: 1.0  
**最后更新**: 2024-02-23  
**维护者**: 开发团队
