# 快速开始 - WebSocket 测试

## 最简单的测试方法（3 步）

### 1. 启动 Redis

```bash
docker-compose up -d redis
```

验证 Redis 是否启动：
```bash
docker-compose ps
```

应该看到：
```
NAME                  IMAGE              STATUS
undercover-redis      redis:7.0-alpine   Up
```

### 2. 启动应用

```bash
# 安装依赖（首次运行）
pip install -r requirements.txt

# 启动应用
python -m src.main
```

看到这个输出说明成功：
```
Application starting in dev mode
SocketIO initialized in eventlet mode
WebSocket handlers registered
 * Running on http://0.0.0.0:5001
```

### 3. 测试 WebSocket（新开一个终端）

```bash
python test_websocket_basic.py
```

预期看到：
```
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

## 常见问题

### Q: 提示 "Connection refused"

**A:** 确保应用正在运行（步骤 2）

### Q: 提示 "Redis connection error"

**A:** 确保 Redis 正在运行：
```bash
docker-compose up -d redis
```

### Q: 提示 "ModuleNotFoundError: No module named 'flask_socketio'"

**A:** 安装依赖：
```bash
pip install -r requirements.txt
```

### Q: 提示 "ModuleNotFoundError: No module named 'eventlet'"

**A:** 安装 eventlet：
```bash
pip install eventlet==0.35.2
```

## 停止服务

```bash
# 停止应用：Ctrl+C

# 停止 Redis
docker-compose down
```

## 下一步

测试通过后，可以继续 Phase 2 的开发，或者查看详细文档：
- [Phase 1 完整文档](WEBSOCKET_PHASE1_README.md)
- [设计文档](.kiro/specs/websocket-notification-system/design.md)
