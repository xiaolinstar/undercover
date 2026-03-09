# 手动测试脚本

这个目录包含需要手动运行的测试脚本，这些脚本不会被 pytest 自动执行。

## 为什么需要手动测试？

这些测试脚本需要：
- 实际运行的服务器（localhost:5001）
- WebSocket 连接
- 真实的网络通信

它们不适合在自动化测试中运行，因为会导致测试卡住或失败。

## 测试脚本

### 1. manual_websocket_basic.py

测试 Socket.IO WebSocket 的基础功能：
- 连接测试
- 房间订阅
- 心跳机制
- 无效 Token 验证

**运行方式：**
```bash
# 1. 先启动服务器
cd backend
python -m src.main

# 2. 在另一个终端运行测试
python tests/manual/manual_websocket_basic.py
```

### 2. manual_native_websocket.py

测试原生 WebSocket（用于微信小程序）：
- 原生 WebSocket 连接
- Token 认证
- 消息收发

**运行方式：**
```bash
# 1. 安装依赖
pip install websocket-client

# 2. 启动服务器
python -m src.main

# 3. 在另一个终端运行测试
python tests/manual/manual_native_websocket.py
```

### 3. manual_api_test.py

测试 REST API 端点：
- 用户认证
- 房间管理
- 游戏操作

**运行方式：**
```bash
# 1. 启动服务器
python -m src.main

# 2. 在另一个终端运行测试
python tests/manual/manual_api_test.py
```

## 注意事项

1. 确保 `.env` 文件中的配置正确
2. 确保 Redis 服务正在运行（如果需要）
3. 确保服务器端口 5001 未被占用
4. 这些测试会修改服务器状态，不要在生产环境运行

## 自动化测试

如果需要运行自动化测试（不包括这些手动测试），请使用：

```bash
cd backend
python -m pytest
```

这将只运行 `tests/unit` 和 `tests/integration` 目录下的测试。
