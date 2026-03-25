# 谁是卧底桌游发牌器服务端 - 架构设计与开发规范

## 1. 技术栈概述

- **语言及框架**: Python 3.10+, Flask
- **数据库**: MySQL 8.0+ (持久化存储用户、历史战绩、题库等)
- **缓存与状态**: Redis 7.0+ (高频房间状态存储、分布式锁、会话缓存)
- **ORM与防注入**: SQLAlchemy / Core
- **数据序列化与验证**: Pydantic 或 Marshmallow
- **Web服务器**: Gunicorn + Nginx

## 2. 总体架构设计

采用分层架构（Layered Architecture）实现各层职责单一，降低耦合：

- **接入层 (API / Controller Layer)**: 接收HTTP/WebSocket请求，路由分发，参数初步提取及输入校验，将包装好的结果以统一格式返回。
- **业务逻辑层 (Service Layer)**: 存放核心游戏逻辑（如建房规则、词汇分配、投票逻辑、胜负判定等）。
- **数据访问层 (Repository / DAO Layer)**: 独立封装对MySQL数据库和Redis的操作。业务层不直接编写SQL，避免数据层变动波及业务层。
- **核心支撑层 (Core / Utils)**: 提供日志采集、异常处理、配置管理、安全认证、基础算法等公共基础能力。

**推荐项目目录结构：**

```text
src/
├── api/             # API 控制器与路由层 (Blueprint)
├── services/        # 业务逻辑服务层 (RoomService, GameEngine, 等)
├── models/          # 数据库实体映射模型 (SQLAlchemy Models)
├── cache/           # 缓存设计与Redis操作封装
├── schemas/         # 数据校验结构定义 (Pydantic / Dataclasses)
├── core/            # 核心机制 (配置、全局异常、安全认证基类)
│   ├── config.py
│   ├── exceptions.py
│   └── logger.py
├── utils/           # 基础通用工具类 (发牌随机算法、时间转换、ID生成)
└── main.py          # Flask 应用及中间件初始化入口
```

## 3. 核心机制详细设计

### 3.1 统一 API 响应格式

所有RESTful接口的响应信息必须保持一致的JSON结构，前端解析无歧义：

```json
{
  "code": 200, // 处理结果代码 (200=业务成功，非200=各类业务错误)
  "message": "success", // 面向开发者的提示信息或终端用户Toast文案
  "data": {} // 接口响应的数据内容包
}
```

### 3.2 异常处理规范 (Exception Handling)

- **Fail-Fast 原则**: 逻辑校验必须最前置，遇到不合法输入或不满足前置状态的情况（如玩家不在房间），尽早抛出业务异常 (Early Throw)。
- **自定义异常基类**: 定义 `BaseBusinessException`，所有业务异常继承于该类并预设错误码。
- **常见业务异常类**:
  - `RoomNotFoundException` (房间不存在或已过期)
  - `InvalidGameStateException` (游戏状态不允许该操作，如已开始不可重新发牌)
  - `PlayerVoteException` (非法投票)
- **全局拦截 (Late Catch)**: 在应用初始化时通过 Flask 的 `@app.errorhandler` 注册全局捕获。各级服务方法中**禁止吞掉**本可抛出的异常，交由全局拦截器统一转换成上述的HTTP格式化返回给客户端，并同时兼顾告警和日志打印。

### 3.3 日志规范 (Logging)

- **日志分级**:
  - `INFO`: 主要的业务状态流转抓取 (如：房间创建成功、发牌完毕、游戏结束并结算)。
  - `WARN`: 客户端不良交互引起的可恢复或预期中异常 (如密码错误、尝试加入满员房间)。
  - `ERROR`: 脏数据、数据库失联、第三方调用异常等非预期严重错误。
- **链路追踪与格式化**: 生产环境要求输出 **JSON格式** 日志。应用中间件(Middleware)需在拦截每个HTTP/WS请求之初，生成唯一的 `trace_id`，利用 Python 3.7+ 的 `contextvars` 特性，透传至所有子日志方法中。日志结构包括：`timestamp`, `level`, `trace_id`, `request_id`, `module`, `message`, `error_stack`。

### 3.4 缓存与状态管理策略 (Redis)

卧底游戏有着极高频的状态刷新（投票进展、存活状态等），属于强实时需求。

- **高频状态存在Redis**: 房间对局的核心状态存入 Redis Hash/String 结构，减少MySQL压力。对局正常或异常结束后，再将最终结算历史落库到 MySQL。
- **并发与分布式锁**: 在"玩家同时抢座加入房间"或"同时提交选票"这类竞争条件下，依靠 Redis 的分布式锁以房间ID为Key进行锁控制，避免状态被穿透导致数据不一致。
- **词库预发**: 为加速发牌响应，游戏词库定期从 MySQL 加载热点数据预热至 Redis Set，并使用抽取命令进行发牌计算。

### 3.5 数据库设计建议 (MySQL)

设计以保障一致性和易于未来分析为主：

- **公共字段**: 重要业务表必须包含 `id`、`created_at`、`updated_at`、`is_deleted`(软删除标识)。
- **核心表规划**:
  - `users`: 玩家基础信息表
  - `word_pairs`: 题库词对表 (包含平民词、卧底词，建议增加`难度`、`主题如春节类`标签关联)
  - `game_records`: 游戏对局大局记录表
  - `player_match_history`: 单人战绩统计关联表

### 3.6 可观测性要求 (Observability)

构建现代服务端的“Metrics-Logs-Traces”三大支柱以保障发牌器的长期运行稳定性：

1. **指标体系 (Metrics)**: 提供专门的 `/metrics` 监控端点（如集成 `prometheus_client`）。需重点暴露：接口各类状态码频率、P95/P99 核心接口(发牌、投票)响应延迟、活跃并发房间数、Redis/数据库连接池使用率。
2. **中心化日志 (Logs)**: 建议使用 ELK、EFK 或 Loki 技术栈。通过采集器抓取容器的标准输出日志，支撑异常快速排查。
3. **分布式追踪 (Traces)**: 接入 OpenTelemetry 标准。无论请求是落在了 MySQL 查询、Redis 调用还是外部接口，链路必须能够完整画出甘特图级调用瀑布，精准定位性能卡点。

## 4. 日常开发纪律与准则

1. **类型提示强制 (Type Hints)**: 函数参数和返回值全面使用 Python Type Hints，提升代码防腐性和IDE审查能力。
2. **静态检查**: 使用 `Ruff` 或 `Flake8` 进行提交前的格式化校验，严禁强推存在 Lint Warning 的代码。
3. **单元测试与 Mock**: 对于核心策略（**词汇分配黑盒算法**、**根据房间人数动态结算胜利方阵营算法**）必须编写 pytest 独立单元测试用例。外部依赖(MySQL/Redis)在测试时必须通过 mock 注入来屏蔽。
4. **环境变量与配置提取**: 绝不硬编码任何敏感凭证。所有受环境影响的配置项必须抽离到 `.env`，并在 `config.py` 中用 Pydantic 的 `BaseSettings` 提供强类型映射校验。

## 5. 客户端开发优先路径 (Client-First Roadmap)

由于客户端（微信小程序/App）需立刻进入并行开发，后端的优先级调整为**“接口契约（API Contract）驱动与数据存取结构化”**。工作拆分和优先级重新规划如下：

### 第一步：锁定核心数据模型 (Data Schema) - 即刻可用作Mock

明确核心实体的属性，供前端及数据库构建：

- **User (用户)**: `id, openid, nickname, avatar_url, total_games, wins`
- **WordPair (卧底词对)**: `id, civilian_word, undercover_word, category(主题), difficulty`
- **Room (高频缓存在Redis中)**:

  ```json
  {
    "room_id": "8888",
    "host_id": 1001,
    "status": "WAITING/PLAYING/VOTING/FINISHED",
    "config": { "player_count": 6, "undercover_count": 1, "whiteboard_count": 0 },
    "players": [
       {"uid": 1001, "seat": 1, "is_ready": true, "is_alive": true, "word": "xxx(仅自己可见)", "role": 1}
    ]
  }
  ```

### 第二步：核心 API 契约定义与 Mock 响应层 (API Contracts)

优先产出并实现以下五大核心控制流接口（仅返回固定/Mock数据，让客户端先跑通网络层校验）：

1. **登录与授权**
   - `POST /api/auth/login`：使用微信/平台 `code` 换取 `token` 及用户信息。
2. **建房与加入**
   - `POST /api/room/create`：设置玩家数与规则，返回 `room_id`。
   - `POST /api/room/join`：根据 `room_id` 加入并占座，返回房间最新 `players`。
3. **游戏准备与发牌**
   - `POST /api/game/ready`：落座玩家点击准备。
   - `POST /api/game/start`：房主发起，服务端为所有人发牌（下发各自词汇及初始轮次信息）。
4. **长轮询/WebSocket 机制**
   - `GET /api/game/sync/:room_id` (或 `WS` 协议)：客户端定时刷新，获取谁正在发言、谁已被淘汰、游戏是否进入投票阶段。
5. **投票阶段**
   - `POST /api/game/vote`：投出出局者目标，当全员或读秒结束时流转状态并清算存活人数。

### 第三步：Mock 替换为真实业务引擎 (Actual Implementation)

- **底层打通**：连接真实 MySQL 和 Redis。
- **发牌算法实装**：接入题库，实现真实的发牌配比及词汇洗牌。
- **投票算法实装**：统计票数，并判断平票/流局及游戏胜利判断（平民获胜还是卧底获胜）。
