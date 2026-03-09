# WebSocket 实时通知系统 - 任务列表（单实例简化版）

## Phase 1: 基础设施搭建 ✅

### 1. 环境准备和依赖安装
- [x] 1.1 更新 requirements.txt 添加 WebSocket 相关依赖
  - flask-socketio==5.3.6
  - python-socketio==5.11.1
  - eventlet==0.35.2
- [x] 1.2 更新 .env.example 添加 WebSocket 配置项
- [x] 1.3 更新 settings.py 添加 WebSocket 配置类

### 2. SocketIO 初始化
- [x] 2.1 在 app_factory.py 中初始化 SocketIO（单实例模式）
- [x] 2.2 配置 CORS 和异步模式（eventlet）
- [x] 2.3 创建 WebSocket 模块目录 (src/websocket/)

### 3. NotificationService 实现
- [x] 3.1 创建 NotificationService 类 (src/services/notification_service.py)
- [x] 3.2 实现 notify_room() 方法（使用 socketio.emit）
- [x] 3.3 添加事件消息格式化工具函数
- [x] 3.4 在 app_factory.py 中初始化 NotificationService

### 4. WebSocket 事件处理器
- [x] 4.1 创建 WebSocket 处理器文件 (src/websocket/handlers.py)
- [x] 4.2 实现 connect 事件处理（JWT 认证）
- [x] 4.3 实现 disconnect 事件处理
- [x] 4.4 实现 subscribe 事件处理（房间订阅）
- [x] 4.5 实现 unsubscribe 事件处理
- [x] 4.6 实现 ping/pong 心跳机制
- [x] 4.7 在 app_factory.py 中注册 WebSocket 处理器

### 5. 事件定义
- [x] 5.1 创建事件类型常量文件 (src/websocket/events.py)
- [x] 5.2 定义房间事件类型（player_joined, player_left）
- [x] 5.3 定义游戏事件类型（started, ended）
- [x] 5.4 定义投票事件类型（submitted）

## Phase 2: 业务集成 ✅

### 6. GameService 集成通知
- [x] 6.1 在 GameService.__init__() 中注入 NotificationService
- [x] 6.2 在 join_room() 中添加 room.player_joined 通知
- [x] 6.3 在 start_game() 中添加 game.started 通知
- [x] 6.4 在 vote_player() 中添加 vote.submitted 通知
- [x] 6.5 在 _check_game_end() 中添加 game.ended 通知

### 7. HTTP API 增强
- [x] 7.1 增强 GET /api/game/sync/{room_id} 接口
  - 添加 updated_at 字段（版本控制）
  - 添加 my_info 字段（当前用户信息）
  - 优化响应数据结构
- [x] 7.2 添加权限验证（用户必须在房间内）

## Phase 3: 安全和错误处理 ✅

### 8. 认证和授权
- [x] 8.1 实现 WebSocket JWT 认证装饰器
- [x] 8.2 实现房间订阅权限验证
- [x] 8.3 添加连接速率限制（防止滥用）

### 9. 错误处理
- [x] 9.1 定义 WebSocket 错误码常量
- [x] 9.2 实现统一的错误响应格式
- [x] 9.3 添加订阅失败错误处理
- [x] 9.4 添加认证失败错误处理

## Phase 4: 监控和日志 ✅

### 10. 基础监控
- [x] 10.1 添加连接数统计（内存计数器）
- [x] 10.2 添加消息发送统计
- [x] 10.3 添加错误统计

### 11. 日志
- [x] 11.1 添加 WebSocket 连接日志
- [x] 11.2 添加房间订阅日志
- [x] 11.3 添加消息发送日志
- [x] 11.4 添加错误日志

## Phase 5: 测试

### 12. 单元测试
- [ ] 12.1 测试 NotificationService.notify_room()
- [ ] 12.2 测试事件消息格式化函数
- [ ] 12.3 测试 JWT 认证逻辑
- [ ] 12.4 测试权限验证逻辑

### 13. 集成测试
- [ ] 13.1 测试 WebSocket 连接流程（认证 -> 连接 -> 订阅）
- [ ] 13.2 测试房间事件通知（玩家加入 -> 所有订阅者收到）
- [ ] 13.3 测试游戏事件通知（游戏开始 -> 所有玩家收到）
- [ ] 13.4 测试断线重连和订阅恢复

### 14. 手动测试
- [ ] 14.1 使用 Postman/wscat 测试 WebSocket 连接
- [ ] 14.2 测试小程序客户端连接
- [ ] 14.3 测试多客户端同时订阅同一房间
- [ ] 14.4 测试网络断开重连场景

## Phase 6: 部署和文档

### 15. 部署配置
- [ ] 15.1 更新 Dockerfile 支持 WebSocket
- [ ] 15.2 配置 Nginx WebSocket 代理
- [ ] 15.3 更新 docker-compose.yml
- [ ] 15.4 配置 Gunicorn + eventlet 启动（单 worker）

### 16. 文档编写
- [ ] 16.1 更新 README.md 添加 WebSocket 说明
- [ ] 16.2 编写 WebSocket API 文档
- [ ] 16.3 编写客户端接入指南（小程序示例）
- [ ] 16.4 更新 Swagger 文档

### 17. 测试验证和清理（必需）
- [ ] 17.1 运行所有单元测试并确保通过
  ```bash
  python -m pytest tests/ -v
  ```
- [ ] 17.2 验证测试覆盖率
  ```bash
  python -m pytest tests/ --cov=src --cov-report=term-missing
  ```
- [ ] 17.3 清理 Docker 进程
  ```bash
  docker-compose down
  ```
- [ ] 17.4 验证代码格式
  ```bash
  ruff check src/
  ```
- [ ] 17.5 更新开发规范文档

## Phase 7: 未来扩展（待办，不在当前范围）

### 17. 多实例支持（未来）
- [ ] 17.1 配置 Redis 消息队列
- [ ] 17.2 更新 NotificationService 使用 Redis Pub/Sub
- [ ] 17.3 实现跨实例消息分发
- [ ] 17.4 压力测试多实例部署

### 18. 高级功能（未来）
- [ ] 18.1 实现消息优先级
- [ ] 18.2 实现离线消息存储
- [ ] 18.3 实现消息去重
- [ ] 18.4 添加 Prometheus 指标

---

**总计**: 18 个主要任务，约 75 个子任务
**预估工期**: 1-2 周（1 名开发者）
**优先级**: Phase 1-6 为当前范围，Phase 7 为未来扩展

## 任务执行建议

1. **按顺序执行**: Phase 1 -> Phase 2 -> ... -> Phase 6
2. **每个 Phase 完成后测试**: 确保功能正常再进入下一阶段
3. **Phase 7 暂不实施**: 等单实例稳定运行后再考虑多实例扩展
4. **重点关注**: Phase 1-2（核心功能）和 Phase 5（测试）

## 开发规范（重要）

### 代码提交前必须完成

1. **运行所有单元测试**
   ```bash
   python -m pytest tests/ -v
   ```
   - 确保所有测试通过（排除已知遗留问题）
   - 当前已知问题：`tests/api_test.py::ApiIntegrationTest::test_full_game_flow`

2. **清理 Docker 进程**
   ```bash
   docker-compose down
   ```

3. **验证代码格式**
   ```bash
   ruff check src/
   ```

### 详细规范

请参考：[开发规范文档](DEVELOPMENT_GUIDELINES.md)
