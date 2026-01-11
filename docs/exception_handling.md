# 异常处理指南

## 1. 概述

本项目采用统一的异常处理策略和结构化日志系统，旨在提供健壮的错误处理机制、清晰的异常层级结构以及详尽的调试信息。

### 1.1 设计目标

1. **清晰的分类**：通过模块化文件结构和类层级，明确异常的业务含义。
2. **统一的范式**：定义表示层、应用层、领域层和基础设施层的标准处理方式。
3. **可追踪性**：通过唯一的错误码和结构化日志，快速定位问题根源。
4. **用户友好**：向终端用户提供清晰、无害的错误提示，同时在后台记录详细堆栈。

## 2. 异常类体系

### 2.1 文件结构

异常类按照功能域进行了模块化拆分：

```
src/exceptions/
├── __init__.py           # 导出所有异常类（推荐导入入口）
├── base.py              # 基础异常类 (BaseGameException)
├── domain.py            # 领域异常基类 (DomainException)
├── room.py              # 房间相关异常
├── game.py              # 游戏相关异常
├── user.py              # 用户相关异常
├── infrastructure.py    # 基础设施异常
└── validation.py        # 验证异常
```

### 2.2 异常层次结构

```
BaseGameException
├── DomainException (领域业务异常)
│   ├── RoomException
│   │   ├── RoomNotFoundError
│   │   ├── RoomFullError
│   │   ├── RoomStateError
│   │   └── RoomPermissionError
│   ├── GameException
│   │   ├── GameNotStartedError
│   │   ├── GameAlreadyStartedError
│   │   ├── GameEndedError
│   │   ├── InsufficientPlayersError
│   │   ├── InvalidPlayerStateError
│   │   ├── PlayerEliminatedError
│   │   └── InvalidPlayerIndexError
│   └── UserException
│       ├── UserNotFoundError
│       ├── UserNotInRoomError
│       └── UserAlreadyInRoomError
├── InfrastructureException (技术设施异常)
│   ├── RepositoryException
│   │   ├── DataAccessError
│   │   ├── SerializationError
│   │   └── CacheError
│   └── ExternalServiceException
│       ├── WeChatAPIError
│       └── RedisConnectionError
└── ValidationException (输入验证异常)
    ├── InvalidInputError
    ├── InvalidRoomIdError
    └── InvalidCommandError
```

### 2.3 异常类属性

所有自定义异常类都继承自 `BaseGameException`，具备以下标准属性：

```python
@dataclass
class BaseGameException(Exception):
    message: str                    # 用户友好的错误消息
    error_code: str                 # 唯一错误码 (如 ROOM-NOT_FOUND-001)
    details: Optional[Dict] = None  # 详细上下文信息（用于日志，不展示给用户）
    cause: Optional[Exception] = None  # 原始异常（用于异常链）
```

## 3. 错误码规范

错误码格式：`{模块}-{类型}-{序号}`

*   **模块**: ROOM, GAME, USER, REPO, SYS, VALID
*   **类型**: NOT_FOUND, INVALID, PERMISSION, STATE, CONN
*   **示例**:
    *   `ROOM-NOT_FOUND-001`: 房间不存在
    *   `GAME-STATE-002`: 游戏已开始
    *   `SYS-CONN-001`: Redis连接错误
    *   `VALID-INPUT-001`: 输入无效

## 4. 异常处理范式

### 4.1 分层处理策略

| 层级 | 职责 | 处理策略 |
| :--- | :--- | :--- |
| **表示层** (Web/API) | 只有这一层直接面向用户 | **捕获所有异常**。将异常转换为HTTP响应或微信XML消息。记录错误日志。 |
| **应用层** (Service) | 业务流程编排 | **捕获已知异常**（领域/基础设施），转换为业务结果（如 `False, "错误消息"`）。抛出未预期异常。 |
| **领域层** (Model/Logic) | 核心业务规则 | **只抛出，不捕获**。抛出具体的 `DomainException`。 |
| **基础设施层** (Repo) | 数据与外部交互 | **捕获技术异常**（如 `redis.ConnectionError`），包装为 `InfrastructureException` 后向上抛出。 |

### 4.2 代码示例

#### 基础设施层 (捕获并包装)

```python
# src/repositories/room_repository.py
def save(self, room: Room) -> None:
    try:
        # Redis 操作
        self.redis.set(key, data)
    except redis.ConnectionError as e:
        # 将底层 Redis 异常转换为项目定义的异常
        raise RedisConnectionError("保存房间失败", cause=e)
```

#### 领域层 (直接抛出)

```python
# src/models/room.py
def join(self, user):
    if self.is_full():
        raise RoomFullError(self.room_id, self.max_players)
```

#### 应用层 (业务处理)

```python
# src/services/game_service.py
def join_room(self, user_id, room_id):
    try:
        room = self.room_repo.get(room_id)
        room.join(user_id)
        return True, "加入成功"
    except RoomFullError as e:
        # 已知业务错误：记录警告日志，返回友好提示
        logger.warning(f"加入失败: {e.message}")
        return False, e.message
    except RedisConnectionError as e:
        # 系统错误：记录错误日志，返回通用提示
        log_exception(logger, e)
        return False, "系统繁忙，请稍后重试"
```

## 5. 日志规范

### 5.1 日志工具

使用 `src/utils/logger.py` 提供的工具：

```python
from src.utils.logger import setup_logger, log_exception, log_business_event

logger = setup_logger(__name__)
```

### 5.2 记录原则

*   **INFO**: 关键业务事件 (如：房间创建、游戏开始、用户登录)。使用 `log_business_event`。
*   **WARNING**: 预期的业务异常 (如：用户输入错误、房间已满)。
*   **ERROR**: 基础设施故障、未预期的系统错误。使用 `log_exception`。

### 5.3 环境变量

*   `LOG_LEVEL`: 控制日志级别 (默认 INFO)
*   `ENABLE_FILE_LOGGING`: 是否写入文件 (默认 False)

## 6. 开发指南

### 如何添加新异常？

1.  **确定类型**：它属于哪个领域？(Game? User? Repo?)
2.  **选择文件**：找到 `src/exceptions/` 下对应的文件。
3.  **定义类**：继承相应的基类 (如 `GameException`)，并分配唯一的 `error_code`。
4.  **导出**：确保它在 `src/exceptions/__init__.py` 中被导出。

```python
# src/exceptions/game.py
class GameTimeoutError(GameException):
    def __init__(self, room_id):
        super().__init__(
            message="游戏操作超时",
            error_code="GAME-STATE-004",  # 确保不重复
            details={'room_id': room_id}
        )
```
