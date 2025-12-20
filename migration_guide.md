# 架构迁移指南

本文档说明如何从旧版架构迁移到新版面向对象架构。

## 主要变化

### 1. 目录结构调整
```
# 旧版结构
app.py (包含所有逻辑)

# 新版结构
src/
├── main.py              # 应用入口
├── app_factory.py       # 应用工厂
├── models/             # 模型层
├── services/           # 服务层
├── repositories/       # 仓储层
├── config/            # 配置层
└── utils/             # 工具层
```

### 2. 功能模块化
- **房间管理**：从函数式重构为Room模型和服务
- **用户管理**：从函数式重构为User模型和服务
- **游戏逻辑**：从全局函数重构为GameService类
- **消息处理**：从全局函数重构为MessageService类

### 3. 数据访问抽象
- 引入仓储模式（Repository Pattern）
- RoomRepository处理房间数据持久化
- UserRepository处理用户数据持久化

## 迁移步骤

### 1. 依赖更新
确保requirements.txt包含所有必要依赖：
```
Flask==3.1.2
gunicorn==23.0.0
redis==7.1.0
pytest==9.0.2
pytest-cov==7.0.0
coverage==7.13.0
```

### 2. 环境配置
更新.env文件适配新架构：
```
WECHAT_TOKEN=your_token_here
WECHAT_APP_ID=your_app_id_here
WECHAT_APP_SECRET=your_app_secret_here
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your_secret_key_here
```

### 3. Docker配置更新
Dockerfile更新应用入口：
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.main:app"]
```

### 4. 代码迁移对照表

| 旧版函数 | 新版组件 | 说明 |
|---------|---------|------|
| create_room() | GameService.create_room() | 房间创建逻辑迁移 |
| join_room() | GameService.join_room() | 房间加入逻辑迁移 |
| start_game() | GameService.start_game() | 游戏开始逻辑迁移 |
| show_word() | GameService.show_word() | 词语显示逻辑迁移 |
| handle_vote_by_index() | GameService.vote_player() | 投票逻辑迁移 |
| show_status() | GameService.show_status() | 状态显示逻辑迁移 |
| get_room()/save_room() | RoomRepository | 数据访问层抽象 |
| get_user()/save_user() | UserRepository | 数据访问层抽象 |

## 新架构优势

### 1. 可维护性提升
- 代码组织更清晰，遵循单一职责原则
- 业务逻辑与数据访问分离
- 配置集中管理，便于调整

### 2. 可测试性增强
- 各层组件可独立单元测试
- 依赖注入便于mock测试
- 完整的测试覆盖

### 3. 可扩展性改善
- 插件化设计支持功能扩展
- 配置驱动便于参数调整
- 模块化架构支持微服务拆分

## 回滚方案

如需回滚到旧版架构：
1. 恢复app.py文件
2. 恢复Dockerfile中的应用入口
3. 删除src目录
4. 恢复旧版测试文件

## 验证清单

迁移完成后验证以下功能：
- [ ] 房间创建和加入
- [ ] 游戏开始和词语分配
- [ ] 状态查看和词语显示
- [ ] 投票功能
- [ ] 游戏结束判断
- [ ] 微信消息处理
- [ ] 所有单元测试通过
- [ ] 集成测试通过