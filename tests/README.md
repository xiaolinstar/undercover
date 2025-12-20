# 测试说明

## 测试结构

```
tests/
├── README.md                 # 测试说明文档
├── conftest.py              # pytest配置文件
├── unit/                    # 单元测试
│   ├── src/
│   │   ├── models/          # 模型测试
│   │   │   ├── test_room.py
│   │   │   └── test_user.py
│   │   ├── services/        # 服务测试
│   │   │   └── test_game_service.py
│   │   └── repositories/    # 仓储测试
│   └── __init__.py
├── integration/             # 集成测试
│   ├── src/
│   │   └── test_game_flow.py
│   └── __init__.py
└── __init__.py
```

## 测试类型

### 单元测试 (Unit Tests)
- **目的**：测试单个函数或类的功能
- **范围**：模型、服务、工具类等独立组件
- **特点**：使用mock对象隔离外部依赖

### 集成测试 (Integration Tests)
- **目的**：测试多个组件协同工作的功能
- **范围**：完整的业务流程、API接口等
- **特点**：使用真实的依赖组件（如Redis）

## 运行测试

### 运行所有测试
```bash
python -m pytest tests/ -v
```

### 运行单元测试
```bash
python -m pytest tests/unit/ -v
```

### 运行集成测试
```bash
python -m pytest tests/integration/ -v
```

### 运行特定测试文件
```bash
python -m pytest tests/unit/src/models/test_room.py -v
```

## 测试环境配置

测试需要以下环境变量：
- `REDIS_URL`: Redis连接地址（默认：redis://localhost:6379/0）
- `WECHAT_TOKEN`: 微信Token（测试时可使用任意值）
- `WECHAT_APP_ID`: 微信AppID（测试时可使用任意值）
- `WECHAT_APP_SECRET`: 微信AppSecret（测试时可使用任意值）

## 测试覆盖率

运行测试时可以生成覆盖率报告：
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

这将生成HTML格式的覆盖率报告，可以在浏览器中查看。

## 测试最佳实践

1. **测试命名**：使用`test_`前缀，描述性名称
2. **测试独立性**：每个测试应独立运行，不依赖其他测试
3. **测试数据**：使用测试专用数据，避免影响生产数据
4. **断言明确**：使用明确的断言，避免模糊的比较
5. **异常处理**：测试正常情况和异常情况
6. **边界条件**：测试边界值和特殊情况