# 微信小程序 WebSocket 连接指南

## 🎯 问题解决

**问题**: 微信小程序的 `wx.connectSocket` 只支持原生 WebSocket 协议，不支持 Socket.IO。

**解决方案**: 服务端现已同时支持两种 WebSocket 协议：
- **Socket.IO**: `ws://localhost:5001/socket.io/` （用于 Web 端）
- **原生 WebSocket**: `ws://localhost:5001/ws` （用于微信小程序）✅

## 📡 微信小程序连接方式

### 1. WebSocket 连接地址

```
ws://localhost:5001/ws
```

**生产环境**:
```
wss://your-domain.com/ws
```

### 2. 连接流程

#### 步骤 1: 获取 JWT Token

首先通过 HTTP API 登录获取 token：

```javascript
// 小程序登录
wx.login({
  success: (res) => {
    // 调用后端登录接口
    wx.request({
      url: 'http://localhost:5001/api/v1/auth/login',
      method: 'POST',
      data: {
        code: res.code
      },
      success: (loginRes) => {
        const token = loginRes.data.data.token;
        // 使用 token 连接 WebSocket
        connectWebSocket(token);
      }
    });
  }
});
```

#### 步骤 2: 建立 WebSocket 连接

```javascript
let socketTask = null;

function connectWebSocket(token) {
  socketTask = wx.connectSocket({
    url: 'ws://localhost:5001/ws',
    success: () => {
      console.log('WebSocket 连接成功');
    },
    fail: (err) => {
      console.error('WebSocket 连接失败', err);
    }
  });

  // 监听连接打开
  socketTask.onOpen(() => {
    console.log('WebSocket 已打开');
    
    // 发送认证消息
    socketTask.send({
      data: JSON.stringify({
        type: 'auth',
        data: {
          token: token
        }
      }),
      success: () => {
        console.log('认证消息已发送');
      }
    });
  });

  // 监听消息
  socketTask.onMessage((res) => {
    try {
      const message = JSON.parse(res.data);
      handleMessage(message);
    } catch (e) {
      console.error('消息解析失败', e);
    }
  });

  // 监听错误
  socketTask.onError((err) => {
    console.error('WebSocket 错误', err);
  });

  // 监听关闭
  socketTask.onClose(() => {
    console.log('WebSocket 已关闭');
    // 可以实现自动重连
    setTimeout(() => {
      connectWebSocket(token);
    }, 3000);
  });
}
```

#### 步骤 3: 处理消息

```javascript
function handleMessage(message) {
  const { type, event, data } = message;

  switch (type) {
    case 'system':
      handleSystemMessage(event, data);
      break;
    case 'event':
      handleGameEvent(event, data);
      break;
    case 'error':
      handleError(event, data);
      break;
    default:
      console.log('未知消息类型', message);
  }
}

function handleSystemMessage(event, data) {
  switch (event) {
    case 'connected':
      console.log('认证成功', data);
      // 认证成功后，订阅房间
      subscribeRoom('8888');
      break;
    case 'subscribed':
      console.log('订阅成功', data);
      break;
    case 'pong':
      console.log('心跳响应');
      break;
  }
}

function handleGameEvent(event, data) {
  switch (event) {
    case 'room.player_joined':
      console.log('玩家加入', data);
      // 更新 UI
      updatePlayerList();
      break;
    case 'game.started':
      console.log('游戏开始', data);
      // 跳转到游戏页面
      wx.navigateTo({
        url: '/pages/game/game'
      });
      break;
    case 'vote.submitted':
      console.log('投票提交', data);
      // 更新投票状态
      updateVoteStatus();
      break;
    case 'game.ended':
      console.log('游戏结束', data);
      // 显示结果
      showGameResult(data);
      break;
  }
}

function handleError(event, data) {
  console.error('错误', event, data);
  wx.showToast({
    title: data.message || '发生错误',
    icon: 'none'
  });
}
```

#### 步骤 4: 订阅房间

```javascript
function subscribeRoom(roomId) {
  if (!socketTask) {
    console.error('WebSocket 未连接');
    return;
  }

  socketTask.send({
    data: JSON.stringify({
      type: 'subscribe',
      data: {
        room_id: roomId
      }
    }),
    success: () => {
      console.log('订阅请求已发送', roomId);
    }
  });
}
```

#### 步骤 5: 取消订阅

```javascript
function unsubscribeRoom(roomId) {
  if (!socketTask) {
    return;
  }

  socketTask.send({
    data: JSON.stringify({
      type: 'unsubscribe',
      data: {
        room_id: roomId
      }
    })
  });
}
```

#### 步骤 6: 心跳保活

```javascript
let heartbeatTimer = null;

function startHeartbeat() {
  heartbeatTimer = setInterval(() => {
    if (socketTask) {
      socketTask.send({
        data: JSON.stringify({
          type: 'ping'
        })
      });
    }
  }, 30000); // 每 30 秒发送一次
}

function stopHeartbeat() {
  if (heartbeatTimer) {
    clearInterval(heartbeatTimer);
    heartbeatTimer = null;
  }
}

// 在连接成功后启动心跳
socketTask.onOpen(() => {
  // ... 认证代码 ...
  startHeartbeat();
});

// 在关闭时停止心跳
socketTask.onClose(() => {
  stopHeartbeat();
});
```

## 📦 完整示例代码

### WebSocket 管理类

```javascript
// utils/websocket.js
class WebSocketManager {
  constructor() {
    this.socketTask = null;
    this.token = null;
    this.heartbeatTimer = null;
    this.reconnectTimer = null;
    this.isConnected = false;
    this.eventHandlers = {};
  }

  // 连接
  connect(token) {
    this.token = token;
    
    this.socketTask = wx.connectSocket({
      url: 'ws://localhost:5001/ws'
    });

    this.socketTask.onOpen(() => {
      console.log('WebSocket 已打开');
      this.authenticate();
    });

    this.socketTask.onMessage((res) => {
      this.handleMessage(res.data);
    });

    this.socketTask.onError((err) => {
      console.error('WebSocket 错误', err);
      this.isConnected = false;
    });

    this.socketTask.onClose(() => {
      console.log('WebSocket 已关闭');
      this.isConnected = false;
      this.stopHeartbeat();
      this.reconnect();
    });
  }

  // 认证
  authenticate() {
    this.send({
      type: 'auth',
      data: {
        token: this.token
      }
    });
  }

  // 发送消息
  send(data) {
    if (!this.socketTask) {
      console.error('WebSocket 未连接');
      return;
    }

    this.socketTask.send({
      data: JSON.stringify(data),
      success: () => {
        console.log('消息已发送', data);
      },
      fail: (err) => {
        console.error('消息发送失败', err);
      }
    });
  }

  // 处理消息
  handleMessage(data) {
    try {
      const message = JSON.parse(data);
      const { type, event } = message;

      if (type === 'system' && event === 'connected') {
        this.isConnected = true;
        this.startHeartbeat();
        this.emit('connected', message.data);
      } else if (type === 'event') {
        this.emit(event, message);
      } else if (type === 'error') {
        this.emit('error', message);
      }
    } catch (e) {
      console.error('消息解析失败', e);
    }
  }

  // 订阅房间
  subscribeRoom(roomId) {
    this.send({
      type: 'subscribe',
      data: {
        room_id: roomId
      }
    });
  }

  // 取消订阅
  unsubscribeRoom(roomId) {
    this.send({
      type: 'unsubscribe',
      data: {
        room_id: roomId
      }
    });
  }

  // 心跳
  startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      this.send({ type: 'ping' });
    }, 30000);
  }

  stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  // 重连
  reconnect() {
    if (this.reconnectTimer) {
      return;
    }

    this.reconnectTimer = setTimeout(() => {
      console.log('尝试重连...');
      this.reconnectTimer = null;
      if (this.token) {
        this.connect(this.token);
      }
    }, 3000);
  }

  // 事件监听
  on(event, handler) {
    if (!this.eventHandlers[event]) {
      this.eventHandlers[event] = [];
    }
    this.eventHandlers[event].push(handler);
  }

  // 触发事件
  emit(event, data) {
    const handlers = this.eventHandlers[event] || [];
    handlers.forEach(handler => handler(data));
  }

  // 关闭连接
  close() {
    this.stopHeartbeat();
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.socketTask) {
      this.socketTask.close();
      this.socketTask = null;
    }
    this.isConnected = false;
  }
}

// 导出单例
export default new WebSocketManager();
```

### 使用示例

```javascript
// pages/room/room.js
import wsManager from '../../utils/websocket';

Page({
  data: {
    roomId: '',
    players: []
  },

  onLoad(options) {
    this.setData({
      roomId: options.roomId
    });

    // 获取 token（从缓存或登录）
    const token = wx.getStorageSync('token');
    
    // 连接 WebSocket
    wsManager.connect(token);

    // 监听连接成功
    wsManager.on('connected', (data) => {
      console.log('连接成功', data);
      // 订阅房间
      wsManager.subscribeRoom(this.data.roomId);
    });

    // 监听玩家加入
    wsManager.on('room.player_joined', (message) => {
      console.log('玩家加入', message);
      wx.showToast({
        title: message.data.hint,
        icon: 'none'
      });
      // 刷新玩家列表
      this.loadPlayers();
    });

    // 监听游戏开始
    wsManager.on('game.started', (message) => {
      console.log('游戏开始', message);
      wx.showToast({
        title: message.data.hint,
        icon: 'success'
      });
      // 跳转到游戏页面
      wx.navigateTo({
        url: '/pages/game/game?roomId=' + this.data.roomId
      });
    });

    // 监听错误
    wsManager.on('error', (message) => {
      console.error('错误', message);
      wx.showToast({
        title: message.data.message,
        icon: 'none'
      });
    });
  },

  onUnload() {
    // 取消订阅
    wsManager.unsubscribeRoom(this.data.roomId);
  },

  loadPlayers() {
    // 通过 HTTP API 获取玩家列表
    wx.request({
      url: `http://localhost:5001/api/v1/room/${this.data.roomId}`,
      header: {
        'Authorization': 'Bearer ' + wx.getStorageSync('token')
      },
      success: (res) => {
        this.setData({
          players: res.data.data.players
        });
      }
    });
  }
});
```

## 🔍 消息格式

### 客户端发送

#### 认证
```json
{
  "type": "auth",
  "data": {
    "token": "your_jwt_token"
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

#### 取消订阅
```json
{
  "type": "unsubscribe",
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

### 服务端响应

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
  "event": "auth_error",
  "data": {
    "error": "INVALID_TOKEN",
    "message": "Token 无效"
  }
}
```

## ⚠️ 常见问题

### 1. 连接失败

**问题**: WebSocket 连接失败

**解决**:
- 检查 URL 是否正确：`ws://localhost:5001/ws`
- 确认服务器正在运行
- 检查网络连接

### 2. 认证失败

**问题**: 收到 `auth_error` 消息

**解决**:
- 确认 token 是否有效
- 检查 token 是否过期
- 确认 SECRET_KEY 配置正确

### 3. 订阅失败

**问题**: 收到 `subscribe_error` 消息

**解决**:
- 确认房间 ID 正确
- 确认用户已加入房间
- 检查权限

### 4. 收不到消息

**问题**: 订阅成功但收不到事件

**解决**:
- 确认已正确订阅房间
- 检查事件监听器是否正确注册
- 查看服务器日志

## 📞 技术支持

如果遇到问题：

1. 查看服务器日志
2. 使用微信开发者工具的网络面板查看 WebSocket 通信
3. 检查消息格式是否正确
4. 参考完整示例代码

---

**原生 WebSocket 地址**: ws://localhost:5001/ws  
**Socket.IO 地址**: ws://localhost:5001/socket.io/ （Web 端）

现在微信小程序可以正常连接了！🎉
