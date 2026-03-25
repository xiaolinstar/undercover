# 谁是卧底 - 微信小程序客户端架构设计

## 📋 项目概述

**目标**: 开发"谁是卧底"微信小程序客户端，与已有的服务端对接。

**服务端项目**: mp-undercover（基于 Flask + Redis）

**客户端项目**: undercover（微信小程序）

**当前状态**: 核心功能已完成，可与服务端联调

**开发范围**:
- ✅ 微信小程序客户端界面开发
- ✅ 小程序与服务端的 API 对接
- ✅ WebSocket 实时通信
- ✅ 游戏逻辑实现
- ✅ 单元测试覆盖（82%+）

**最近更新**:
- 2026-02-23: 完成微信小程序兼容性修复
- 2026-02-23: 统一 API 参数为下划线格式
- 2026-02-23: 添加字段映射函数
- 2026-02-23: 完成游戏流程交互优化

---

## 🏗️ 客户端架构

### 1. 技术栈选型

| 组件 | 技术选型 | 说明 |
|------|---------|------|
| 开发语言 | TypeScript | 类型安全，提升开发效率 |
| 组件框架 | glass-easel | 微信新一代组件框架 |
| 渲染引擎 | Skyline | 高性能渲染引擎 |
| 状态管理 | 自定义 EventChannel + 全局数据 | 轻量级状态管理 |
| UI 组件库 | 自定义组件 | 统一风格，高复用性 |
| 网络请求 | wx.request 封装 | 统一的网络请求层 |
| 实时通信 | wx.connectSocket | WebSocket 连接 |
| 样式语言 | SCSS | 增强样式编写能力 |

### 2. 核心架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                       小程序架构                              │
├─────────────────────────────────────────────────────────────┤
│  视图层 (View Layer)                                         │
│  - WXML 模板                                                 │
│  - WXSS/SCSS 样式                                            │
│  - 自定义组件                                                 │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│  逻辑层 (Logic Layer)                                        │
│  - Page 页面逻辑                                             │
│  - Component 组件逻辑                                         │
│  - Behavior 混入                                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  服务层 (Service Layer)                                      │
│  - 认证服务 (AuthService)                                    │
│  - 房间服务 (RoomService)                                    │
│  - 游戏服务 (GameService)                                    │
│  - WebSocket 服务 (WebSocketService)                         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  工具层 (Utils Layer)                                        │
│  - 网络请求封装 (Request)                                     │
│  - 本地存储 (Storage)                                         │
│  - 游戏逻辑 (GameLogic)                                       │
│  - 数据验证 (Validator)                                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  数据层 (Data Layer)                                         │
│  - 数据模型 (Models)                                          │
│  - 全局状态 (AppData)                                         │
│  - 本地缓存 (Cache)                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 项目结构

```
undercover/
├── miniprogram/
│   ├── app.ts                     # 应用入口
│   ├── app.json                   # 应用配置
│   ├── app.scss                   # 全局样式
│   │
│   ├── pages/                     # 页面
│   │   ├── index/                 # 首页(大厅)
│   │   │   ├── index.ts
│   │   │   ├── index.wxml
│   │   │   ├── index.scss
│   │   │   └── index.json
│   │   ├── login/                 # 登录页
│   │   ├── room/                  # 房间页
│   │   ├── game/                  # 游戏页
│   │   ├── profile/               # 个人中心
│   │   └── logs/                  # 日志页
│   │
│   ├── components/                # 自定义组件
│   │   ├── room-card/             # 房间卡片
│   │   ├── player-card/           # 玩家卡片
│   │   ├── word-display/          # 词语展示
│   │   ├── vote-modal/            # 投票弹窗
│   │   ├── game-status/           # 游戏状态栏
│   │   ├── countdown/             # 倒计时
│   │   └── loading/               # 加载动画
│   │
│   ├── services/                  # 服务层
│   │   ├── auth.service.ts        # 认证服务
│   │   ├── room.service.ts        # 房间服务
│   │   ├── game.service.ts        # 游戏服务
│   │   └── websocket.service.ts   # WebSocket 服务
│   │
│   ├── utils/                     # 工具类
│   │   ├── request.ts             # 网络请求封装
│   │   ├── storage.ts             # 本地存储
│   │   ├── validator.ts           # 数据验证
│   │   ├── game-logic.ts          # 游戏逻辑
│   │   └── constants.ts           # 常量定义
│   │
│   ├── models/                    # 数据模型
│   │   ├── user.model.ts          # 用户模型
│   │   ├── room.model.ts          # 房间模型
│   │   ├── game.model.ts          # 游戏模型
│   │   └── player.model.ts        # 玩家模型
│   │
│   ├── config/                    # 配置
│   │   ├── api.config.ts          # API 配置
│   │   └── game.config.ts         # 游戏配置
│   │
│   ├── behaviors/                 # 行为混入
│   │   ├── auth.behavior.ts       # 认证行为
│   │   └── game.behavior.ts       # 游戏行为
│   │
│   └── assets/                    # 静态资源
│       ├── images/
│       └── icons/
│
├── typings/                       # 类型定义
│   ├── index.d.ts                 # 全局类型
│   └── wechat.d.ts                # 微信 API 类型扩展
│
├── project.config.json            # 项目配置
├── tsconfig.json                  # TS 配置
└── package.json                   # 依赖管理
```

---

## 🎨 页面设计

### 1. 页面流程图

```
启动 → 检查登录状态
         ↓
    未登录 → 登录页 → 首页
         ↓           ↓
    已登录 → 首页(大厅)
                  ↓
         ┌────────┴────────┐
         ↓                 ↓
     创建房间          加入房间
         ↓                 ↓
         └────────┬────────┘
                  ↓
              房间等待页
                  ↓
              开始游戏
                  ↓
              游戏进行页
                  ↓
              游戏结束
                  ↓
              返回首页
```

### 2. 页面详细设计

**登录页**:

**功能**:
- 微信一键登录
- 获取用户信息
- 保存登录状态

**UI 元素**:
- 游戏标题和 Logo
- 微信登录按钮
- 加载状态提示

**首页/大厅**:

**功能**:
- 显示用户信息
- 创建房间入口
- 加入房间入口（输入房间号）
- 显示历史战绩
- 游戏规则说明

**UI 元素**:
- 用户头像和昵称
- 创建房间按钮
- 加入房间按钮（弹窗输入房间号）
- 游战绩卡片
- 规则说明入口

**房间等待页**:

**功能**:
- 显示房间信息（房间号）
- 显示玩家列表
- 房主可以开始游戏
- 普通玩家可以退出房间
- 实时更新玩家列表

**UI 元素**:
- 房间号显示（可分享）
- 玩家列表（头像、昵称、序号）
- 开始游戏按钮（仅房主）
- 退出房间按钮
- 等待提示

**游戏进行页**:

**功能**:
- 显示当前游戏状态
- 显示玩家的词语
- 显示当前轮次和玩家
- 描述环节
- 投票环节
- 显示投票结果
- 显示淘汰信息
- 游戏结束判定

**UI 元素**:
- 游戏状态栏
- 玩家列表（显示状态）
- 词语卡片（仅显示自己的词语）
- 描述提示
- 投票弹窗
- 结果展示

**个人中心**:

**功能**:
- 显示用户信息
- 显示游戏统计
- 游戏记录查询
- 设置选项

**UI 元素：**
- 用户头像和昵称
- 游戏统计卡片
- 游戏记录列表
- 设置按钮

---

## 🧩 组件设计

**room-card（房间卡片）**:

**用途**: 在首页展示房间信息

**Props**:
```typescript
{
  roomId: string        // 房间 ID
  roomCode: string      // 房间号
  playerCount: number   // 当前玩家数
  maxPlayers: number    // 最大玩家数
  status: 'waiting' | 'playing' | 'finished'
  createdAt: string     // 创建时间
}
```

待办：丰富隐藏字段

**Events**:
- `onJoin`: 加入房间

**player-card（玩家卡片）**:

**用途**: 显示玩家信息

**Props**:
```typescript
{
  playerNumber: number      // 玩家序号
  nickname: string          // 昵称
  avatar: string            // 头像
  isOwner: boolean          // 是否房主
  isAlive: boolean          // 是否存活
  currentAction?: string    // 当前操作
}
```

**Events**:
- `onVote`: 投票给该玩家

**word-display（词语展示）**:

**用途**: 显示玩家的词语

**Props**:
```typescript
{
  word: string              // 词语
  role: 'civilian' | 'spy'  // 角色
  visible: boolean          // 是否可见
}
```

**Events**:
- `onToggle`: 切换显示/隐藏

**vote-modal（投票弹窗）**:

**用途**: 投票选择

**Props**:
```typescript
{
  visible: boolean          // 是否显示
  players: Player[]         // 可投票玩家列表
  currentPlayer: number     // 当前玩家序号
}
```

**Events**:
- `onVote`: 投票选择
- `onCancel`: 取消投票

**game-status（游戏状态栏）**:

**用途**: 显示游戏当前状态

**Props**:
```typescript
{
  status: 'describing' | 'voting' | 'finished'
  currentRound: number      // 当前轮次
  currentPlayer?: number    // 当前玩家
  countdown?: number        // 倒计时
}
```

**countdown（倒计时）**:

**用途**: 倒计时显示

**Props**:
```typescript
{
  seconds: number           // 倒计时秒数
  onComplete?: () => void   // 完成回调
}
```

---

## 🔌 API 接口对接

### 1. API 配置

```typescript
// config/api.config.ts
export const API_CONFIG = {
  USE_MOCK: false,  // Mock 模式开关
  BASE_URL: 'http://localhost:5001/api/v1',
  WS_URL: 'ws://localhost:5001/ws',  // 原生 WebSocket
  TIMEOUT: 10000,
}

export const API_ENDPOINTS = {
  // 认证相关
  LOGIN: '/auth/login',
  UPDATE_USERINFO: '/auth/update-userinfo',
  GET_USER_STATS: '/auth/user-stats',
  
  // 房间相关 (参数: max_players, room_code, room_id)
  CREATE_ROOM: '/room/create',     // 参数: max_players
  JOIN_ROOM: '/room/join',         // 参数: room_code (4位数字)
  GET_ROOM: '/room/:roomId',       // 路径参数: roomId (UUID)
  LEAVE_ROOM: '/room/leave',       // 参数: room_id
  
  // 游戏相关 (参数: room_id, target_player_id)
  START_GAME: '/game/start',       // 参数: room_id
  GET_STATUS: '/game/status',      // 参数: room_id
  VOTE: '/game/vote',              // 参数: room_id, target_player_id
}
```

> **注意：** 服务端使用下划线命名 (snake_case)，前端使用驼峰命名 (camelCase)。
> `RoomService` 中已实现字段映射函数 `mapRoomData()` 自动转换。

### 2. 字段映射

| 服务端字段 | 前端字段 | 说明 |
|-----------|---------|------|
| `room_id` | `roomId` | 房间唯一标识 (UUID) |
| `room_code` | `roomCode` | 4位房间号，用于分享 |
| `owner_id` | `ownerId` | 房主 ID |
| `max_players` | `maxPlayers` | 最大玩家数 |
| `created_at` | `createdAt` | 创建时间 |
| `player_id` | `playerId` | 玩家 ID |
| `is_owner` | `isOwner` | 是否房主 |
| `is_ready` | `isReady` | 是否准备 |

### 2. 接口调用示例

#### 2.1 认证服务

```typescript
// services/auth.service.ts
import { request } from '../utils/request'

export class AuthService {
  /**
   * 微信登录
   */
  static async login(): Promise<LoginResult> {
    // 获取微信登录 code
    const { code } = await wx.login()
    
    // 发送到服务器
    const result = await request.post(API_ENDPOINTS.LOGIN, { code })
    
    // 保存 token
    wx.setStorageSync('token', result.token)
    wx.setStorageSync('openid', result.openid)
    
    return result
  }
  
  /**
   * 检查登录状态
   */
  static checkLogin(): boolean {
    const token = wx.getStorageSync('token')
    return !!token
  }
}
```

#### 2.2 房间服务

```typescript
// services/room.service.ts
import { request } from '../utils/request'

export class RoomService {
  /**
   * 创建房间
   */
  static async createRoom(maxPlayers: number = 12): Promise<Room> {
    return await request.post(API_ENDPOINTS.CREATE_ROOM, { maxPlayers })
  }
  
  /**
   * 加入房间
   */
  static async joinRoom(roomCode: string): Promise<Room> {
    return await request.post(API_ENDPOINTS.JOIN_ROOM, { roomCode })
  }
  
  /**
   * 获取房间信息
   */
  static async getRoom(roomId: string): Promise<Room> {
    return await request.get(API_ENDPOINTS.GET_ROOM.replace(':roomId', roomId))
  }
  
  /**
   * 离开房间
   */
  static async leaveRoom(roomId: string): Promise<void> {
    await request.post(API_ENDPOINTS.LEAVE_ROOM, { roomId })
  }
}
```

### 3. WebSocket 连接

```typescript
// services/websocket.service.ts
export class WebSocketService {
  private socket: WechatMiniprogram.SocketTask | null = null
  private reconnectTimer: number | null = null
  private heartbeatTimer: number | null = null
  
  /**
   * 连接 WebSocket
   */
  connect(token: string): void {
    this.socket = wx.connectSocket({
      url: `${WS_URL}?token=${token}`,
      success: () => {
        console.log('WebSocket 连接成功')
        this.startHeartbeat()
      },
      fail: (err) => {
        console.error('WebSocket 连接失败', err)
        this.reconnect()
      }
    })
    
    this.socket.onMessage((res) => {
      const message = JSON.parse(res.data as string)
      this.handleMessage(message)
    })
    
    this.socket.onClose(() => {
      console.log('WebSocket 连接关闭')
      this.stopHeartbeat()
      this.reconnect()
    })
  }
  
  /**
   * 发送消息
   */
  send(event: string, data: any): void {
    if (this.socket) {
      this.socket.send({
        data: JSON.stringify({ event, data })
      })
    }
  }
  
  /**
   * 心跳检测
   */
  private startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      this.send('ping', {})
    }, 30000) as unknown as number
  }
  
  /**
   * 断线重连
   */
  private reconnect(): void {
    this.reconnectTimer = setTimeout(() => {
      const token = wx.getStorageSync('token')
      if (token) {
        this.connect(token)
      }
    }, 5000) as unknown as number
  }
  
  /**
   * 处理消息
   */
  private handleMessage(message: any): void {
    switch (message.event) {
      case 'player_joined':
        // 玩家加入
        break
      case 'game_started':
        // 游戏开始
        break
      case 'vote_start':
        // 开始投票
        break
      case 'game_finished':
        // 游戏结束
        break
    }
  }
}
```

---

## 📊 数据模型

### 1. User 模型

```typescript
// models/user.model.ts
export interface User {
  userId: string
  openid: string
  nickname: string
  avatar: string
  gamesPlayed: number
  gamesWon: number
  createdAt: string
}
```

### 2. Room 模型

```typescript
// models/room.model.ts
export interface Room {
  roomId: string
  roomCode: string
  ownerId: string
  players: Player[]
  maxPlayers: number
  status: 'waiting' | 'playing' | 'finished'
  createdAt: string
}
```

### 3. Player 模型

```typescript
// models/player.model.ts
export interface Player {
  playerId: string
  playerNumber: number
  nickname: string
  avatar: string
  isOwner: boolean
  isAlive: boolean
}
```

### 4. Game 模型

```typescript
// models/game.model.ts
export interface Game {
  roomId: string
  status: 'describing' | 'voting' | 'finished'
  currentRound: number
  currentPlayer?: number
  word?: string
  role?: 'civilian' | 'spy'
  players: Player[]
  winner?: 'civilian' | 'spy'
  spies?: number[]
}
```

---

## 🎮 游戏流程

### 1. 游戏状态流转

```
创建房间 → 等待玩家加入 → 开始游戏
                            ↓
                      发放词语
                            ↓
                      描述环节(轮流)
                            ↓
                      投票环节
                            ↓
                      判定结果
                        ↓        ↓
                    淘汰玩家   游戏结束
                        ↓
                    下一轮
```

### 2. 游戏规则逻辑

```typescript
// utils/game-logic.ts
export class GameLogic {
  /**
   * 判断游戏是否结束
   */
  static checkGameEnd(players: Player[]): {
    ended: boolean
    winner?: 'civilian' | 'spy'
  } {
    const alivePlayers = players.filter(p => p.isAlive)
    const aliveSpies = alivePlayers.filter(p => p.role === 'spy')
    
    // 如果卧底全部被淘汰，平民胜利
    if (aliveSpies.length === 0) {
      return { ended: true, winner: 'civilian' }
    }
    
    // 如果卧底人数 >= 平民人数，卧底胜利
    const aliveCivilians = alivePlayers.filter(p => p.role === 'civilian')
    if (aliveSpies.length >= aliveCivilians.length) {
      return { ended: true, winner: 'spy' }
    }
    
    return { ended: false }
  }
  
  /**
   * 投票结果统计
   */
  static countVotes(votes: Record<number, number>): {
    eliminated: number
    voteCounts: Record<number, number>
  } {
    const voteCounts: Record<number, number> = {}
    
    // 统计票数
    Object.values(votes).forEach(target => {
      voteCounts[target] = (voteCounts[target] || 0) + 1
    })
    
    // 找出票数最多的玩家
    let maxVotes = 0
    let eliminated = 0
    Object.entries(voteCounts).forEach(([player, count]) => {
      if (count > maxVotes) {
        maxVotes = count
        eliminated = parseInt(player)
      }
    })
    
    return { eliminated, voteCounts }
  }
}
```

---

## 🚀 开发路线图

### 阶段一：基础架构搭建 ✅ 已完成

**目标**: 搭建小程序基础架构

**任务清单**:
- [x] 项目初始化
- [x] 创建目录结构
- [x] 封装网络请求（request.ts）
- [x] 封装 WebSocket（websocket.ts）
- [x] 实现认证逻辑（auth.service.ts）
- [x] 创建基础组件（room-card, player-card, word-display, vote-modal, game-status）
- [x] Mock 开发模式
- [x] 单元测试框架（Jest + ts-jest）
- [x] 测试覆盖率 82%+

**阶段二：核心页面开发** ✅ 已完成

**目标**: 完成核心页面开发

**任务清单**:
- [x] 登录页面（微信一键登录）
- [x] 首页/大厅（创建/加入房间）
- [x] 房间等待页（实时玩家列表）
- [x] 游戏进行页（描述、投票、结果）
- [x] 个人中心（用户信息、统计）

**阶段三：游戏功能实现** ✅ 已完成

**目标**: 实现完整游戏流程

**任务清单**:
- [x] 创建/加入房间
- [x] 玩家列表实时更新（WebSocket）
- [x] 游戏开始流程
- [x] 描述环节（发言输入、历史记录）
- [x] 投票功能（倒计时、票数显示）
- [x] 游戏结果展示（胜利动画、身份揭示）
- [x] WebSocket 实时通信
  - [x] 连接管理
  - [x] 心跳检测（30 秒）
  - [x] 断线重连（最多 5 次）
  - [x] 消息队列

**阶段四：优化与测试** 🚧 进行中

**目标**: 优化体验，完善功能

**任务清单**:
- [x] UI 美化（自定义导航栏、动画效果）
- [x] 微信小程序兼容性修复
- [x] API 参数格式统一（下划线格式）
- [x] 字段映射 (服务端下划线 → 前端驼峰)
- [ ] 错误处理优化
  - [ ] 统一错误提示组件
  - [ ] 全局异常捕获
  - [ ] 日志记录
- [ ] 性能优化
- [ ] 数据缓存

**阶段五：功能扩展** 📋 待开发

**目标**: 扩展游戏功能

**任务清单**:
- [ ] 游戏记录查询
- [ ] 玩家统计（胜率、场次）
- [ ] 房间分享功能
- [ ] 消息通知
- [ ] 主题切换（暗色模式）

## 📊 当前进度

| 模块 | 状态 | 完成度 |
|------|------|--------|
| 基础架构 | ✅ 完成 | 100% |
| 核心页面 | ✅ 完成 | 100% |
| 游戏功能 | ✅ 完成 | 100% |
| WebSocket | ✅ 完成 | 100% |
| 单元测试 | ✅ 完成 | 82% 覆盖率 |
| 错误处理 | 🚧 进行中 | 30% |
| 性能优化 | 📋 待开发 | 0% |
| 功能扩展 | 📋 待开发 | 0% |

**总体进度：约 75%**

## 📝 开发规范

**代码规范**:

**TypeScript**: 使用 ESLint + Prettier

**命名规范**:
- 页面：小写字母，中划线分隔（`room-detail`）
- 组件：小写字母，中划线分隔（`player-card`）
- 变量：驼峰命名（`playerList`）
- 常量：全大写，下划线分隔（`API_BASE_URL`）
- 类型/接口：帕斯卡命名（`Player`, `GameState`）

**Git 提交规范**:

```
feat: 新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式调整
refactor: 重构
test: 测试相关
chore: 构建/工具链相关
```

**目录规范**:

- 每个页面/组件必须包含四个文件：`.ts`, `.wxml`, `.scss`, `.json`
- 公共组件放在 `components/` 目录
- 业务逻辑放在 `services/` 目录
- 工具函数放在 `utils/` 目录
- 类型定义放在 `models/` 或 `typings/` 目录

## 🎯 预期成果

**功能完整**:
- 完整的游戏流程
- 实时多人游戏
- 稳定的网络连接

**体验优秀**:
- 流畅的界面交互
- 美观的 UI 设计
- 友好的错误提示

**代码质量**:
- 清晰的项目结构
- 完善的类型定义
- 良好的代码复用

## 📞 技术支持

- [微信小程序官方文档](https://developers.weixin.qq.com/miniprogram/dev/framework/)
- [TypeScript 官方文档](https://www.typescriptlang.org/docs/)
- [Skyline 渲染引擎](https://developers.weixin.qq.com/miniprogram/dev/framework/runtime/skyline/)
