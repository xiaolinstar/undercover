# WebSocket 连接问题解决方案总结

## 🎯 问题

微信小程序的 `wx.connectSocket` 只支持原生 WebSocket 协议，不支持 Socket.IO 协议。

原有服务端使用 Flask-SocketIO（Socket.IO 协议），导致小程序无法连接。

## ✅ 解决方案

添加原生 WebSocket 支持，同时保留 Socket.IO，实现双协议支持。

### 架构设计

```
┌─────────────────┐         ┌─────────────────┐
│   Web 客户端    │         │  微信小程序     │
│  (Socket.IO)    │         │ (原生 WebSocket)│
└────────┬────────┘         └────────┬────────┘
         │                           │
         │ Socket.IO                 │ WebSocket
         │ ws://.../socket.io/       │ ws://.../ws
         │                           │
         └───────────┬───────────────┘
                     │
         ┌───────────▼───────────┐
         │   Flask 服务器        │
         │                       │
         │  ┌─────────────────┐  │
         │  │ Flask-SocketIO  │  │
         │  │  (Socket.IO)    │  │
         │  └─────────────────┘  │
         │                       │
         │  ┌─────────────────┐  │
         │  │   Flask-Sock    │  │
         │  │ (原生 WebSocket)│  │
         │  └─────────────────┘  │
         │                       │
         │  ┌─────────────────┐  │
         │  │NotificationService│
         │  │  (统一通知)     │  │
         │  └─────────────────┘  │
         └───────────────────────┘
```

## 📦 实现内容

### 1. 新增文件

#### `src/websocket/native_handlers.py`
- 原生 WebSocket 处理器
- 支持认证、订阅、心跳等功能
- 兼容微信小程序的消息格式

#### `test_native_websocket.py`
- 原生 WebSocket 测试脚本
- 验证连接、认证、订阅、心跳功能

#### `MINIPROGRAM_WEBSOCKET_GUIDE.md`
- 微信小程序完整连接指南
- 包含示例代码和 WebSocketManager 类

### 2. 修改文件

#### `src/services/notification_service.py`
- 添加原生 WebSocket 广播支持
- 同时向 Socket.IO 和原生 WebSocket 客户端发送通知

#### `src/app_factory.py`
- 初始化 Flask-Sock
- 集成原生 WebSocket 广播函数

#### `requirements.txt`
- 添加 `flask-sock==0.7.0`

#### `FRONTEND_INTEGRATION_GUIDE.md`
- 更新 WebSocket 连接说明
- 添加双协议支持说明

## 🔌 连接方式

### Web 端（Socket.IO）

```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:5001', {
  auth: { token: 'YOUR_JWT_TOKEN' },
  transports: ['websocket']
});
```

**地址**: `ws://localhost:5001/socket.io/`

### 微信小程序（原生 WebSocket）

```javascript
const socketTask = wx.connectSocket({
  url: 'ws://localhost:5001/ws'
});

// 认证
socketTask.send({
  data: JSON.stringify({
    type: 'auth',
    data: { token: 'YOUR_JWT_TOKEN' }
  })
});
```

**地址**: `ws://localhost:5001/ws` ✅

## 📨 消息格式

### 客户端 → 服务端

#### 认证
```json
{
  "type": "auth",
  "data": {
    "token": "jwt_token"
  }
}
```

#### 订阅房间
```json
{
  "type": "subscribe",
  "data": {
    "room_id": "8888"
  }
}
```

#### 心跳
```json
{
  "type": "ping"
}
```

### 服务端 → 客户端

#### 系统消息
```json
{
  "type": "system",
  "event": "connected",
  "data": {
    "connection_id": "123456",
    "user_id": "user_123"
  }
}
```

#### 游戏事件
```json
{
  "type": "event",
  "event": "room.player_joined",
  "room_id": "8888",
  "timestamp": 1708675200,
  "data": {
    "player_count": 4,
    "hint": "玩家2 加入了房间"
  }
}
```

#### 错误消息
```json
{
  "type": "error",
  "event": "subscribe_error",
  "data": {
    "error": "ROOM_NOT_FOUND",
    "message": "房间不存在"
  }
}
```

## 🧪 测试结果

### 原生 WebSocket 测试

```bash
$ python test_native_websocket.py

============================================================
原生 WebSocket 测试（微信小程序兼容）
============================================================
✓ 生成 JWT token
✓ WebSocket 连接成功
✓ 认证成功！
✓ 心跳正常！
✓ 所有测试通过！
============================================================
```

### Socket.IO 测试

```bash
$ python test_websocket_basic.py

============================================================
✓ 连接测试：通过
✓ 订阅测试：通过
✓ 心跳测试：通过
✓ 无效Token测试：通过
============================================================
总计: 4/4 通过
============================================================
```

## 🎯 优势

### 1. 兼容性
- ✅ 支持 Web 端（Socket.IO）
- ✅ 支持微信小程序（原生 WebSocket）
- ✅ 支持其他原生 WebSocket 客户端

### 2. 统一通知
- NotificationService 自动向两种协议的客户端发送通知
- 业务代码无需关心客户端类型
- 消息格式统一

### 3. 向后兼容
- 保留现有 Socket.IO 功能
- 不影响现有 Web 端代码
- 渐进式迁移

### 4. 易于维护
- 代码结构清晰
- 职责分离
- 便于扩展

## 📚 相关文档

- **[MINIPROGRAM_WEBSOCKET_GUIDE.md](MINIPROGRAM_WEBSOCKET_GUIDE.md)** - 微信小程序完整连接指南
- **[FRONTEND_INTEGRATION_GUIDE.md](FRONTEND_INTEGRATION_GUIDE.md)** - 前后端联调指南
- **[PHASE2_COMPLETION_REPORT.md](PHASE2_COMPLETION_REPORT.md)** - Phase 2 完成报告

## 🚀 快速开始

### 1. 启动服务器

```bash
python -m src.main
```

### 2. 测试原生 WebSocket

```bash
python test_native_websocket.py
```

### 3. 微信小程序连接

参考 [MINIPROGRAM_WEBSOCKET_GUIDE.md](MINIPROGRAM_WEBSOCKET_GUIDE.md) 中的完整示例代码。

## 📊 技术栈

| 组件 | 技术 | 用途 |
|------|------|------|
| Socket.IO | Flask-SocketIO | Web 端 WebSocket |
| 原生 WebSocket | Flask-Sock | 微信小程序 WebSocket |
| 通知服务 | NotificationService | 统一消息分发 |
| 认证 | JWT | Token 验证 |

## ✅ 验收标准

- [x] 原生 WebSocket 端点可访问（`/ws`）
- [x] 支持 JWT 认证
- [x] 支持房间订阅/取消订阅
- [x] 支持心跳保活
- [x] 支持权限验证
- [x] 同时向两种协议客户端发送通知
- [x] 测试脚本通过
- [x] 文档完整

---

**原生 WebSocket 地址**: ws://localhost:5001/ws  
**Socket.IO 地址**: ws://localhost:5001/socket.io/

现在微信小程序可以正常连接了！🎉
