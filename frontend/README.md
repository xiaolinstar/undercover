# 谁是卧底 - 微信小程序

一款聚会桌游微信小程序客户端，支持多人在线游戏。

## 📖 目录

- [项目简介](#项目简介)
- [技术栈](#技术栈)
- [功能特性](#功能特性)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [开发指令](#开发指令)
- [Mock 模式](#mock-模式)
- [测试](#测试)
- [开发进度](#开发进度)
- [待办事项](#待办事项)
- [相关项目](#相关项目)
- [技术支持](#技术支持)

---

## 项目简介

本项目是"谁是卧底"游戏的微信小程序客户端，与公众号服务端 (mp-undercover) 配合使用。

## 技术栈

- **开发语言**: TypeScript
- **组件框架**: glass-easel
- **渲染引擎**: Skyline
- **样式语言**: SCSS
- **状态管理**: 自定义 EventChannel + 全局数据
- **测试框架**: Jest + ts-jest

## 功能特性

- ✅ 微信一键登录
- ✅ 创建/加入房间
- ✅ WebSocket 实时通信
- ✅ 完整游戏流程（描述、投票、结果）
- ✅ Mock 开发模式
- ✅ 单元测试覆盖（82%+）

## 项目结构

```
undercover/
├── miniprogram/           # 小程序源码
│   ├── config/           # 配置文件
│   ├── mock/             # Mock 数据和服务
│   ├── models/           # 数据模型
│   ├── services/         # 服务层
│   ├── utils/            # 工具类
│   ├── pages/            # 页面
│   ├── components/       # 组件
│   └── app.json          # 应用配置
├── tests/                 # 测试文件
│   ├── utils/            # 工具类测试
│   ├── services/         # 服务层测试
│   └── mock/             # Mock 服务测试
├── typings/              # 类型定义
├── ARCHITECTURE.md       # 架构文档
├── QUICKSTART.md         # 快速开始指南
└── README.md             # 项目说明
```

---

## 快速开始

### 环境要求

- 微信开发者工具（最新稳定版）
- Node.js 16+（用于测试和工具链）

### 安装步骤

**克隆项目**:
```bash
git clone https://github.com/xiaolinstar/undercover.git
cd undercover
```

**安装依赖**:
```bash
npm install
```

**用微信开发者工具打开项目**:
- 选择项目目录
- 填写小程序 AppID: `wxabbdd9d9c1d338ba`

**开发模式配置**:
- 勾选"不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书"

---

## 开发指令

### NPM 脚本

```bash
# 运行测试
npm test

# 运行测试（监听模式）
npm run test:watch

# 运行测试并生成覆盖率报告
npm run test:coverage

# 运行测试（详细输出）
npm run test:verbose
```

### Git 工作流

```bash
# 创建新功能分支
git checkout -b feature/功能名称

# 提交代码
git add .
git commit -m "feat: 添加新功能"

# 推送到远程
git push origin feature/功能名称
```

### 开发建议

**代码规范**:
- 使用 TypeScript 编写代码
- 遵循 ESLint 规则
- 提交前运行测试

**Git 提交规范**:
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具链相关

---

## Mock 模式

项目支持 Mock 开发模式，无需连接服务端即可开发调试。

### 开启 Mock 模式

编辑 `miniprogram/config/api.config.ts`:

```typescript
export const API_CONFIG = {
  USE_MOCK: true,  // 设置为 true 开启 Mock 模式
  // ...
}
```

### 关闭 Mock 模式

```typescript
export const API_CONFIG = {
  USE_MOCK: false,  // 设置为 false 使用真实 API
  BASE_URL: 'https://your-domain.com/api/miniprogram',
  WS_URL: 'wss://your-domain.com/ws',
}
```

### Mock 功能

- ✅ 模拟用户登录
- ✅ 模拟创建/加入房间
- ✅ 模拟游戏流程
- ✅ 随机生成词语对
- ✅ 模拟投票和淘汰
- ✅ 模拟游戏结束判定

### Mock 数据

- 默认房间号: `1234`
- 已有玩家: 测试用户（房主）

---

## 测试

### 测试覆盖率

当前测试覆盖率：

| 类型 | 覆盖率 | 状态 |
|------|--------|------|
| Statements | 82.98% | ✅ 达标 |
| Branches | 79.16% | ✅ 达标 |
| Functions | 82.03% | ✅ 达标 |
| Lines | 82.82% | ✅ 达标 |

### 测试文件

- `tests/utils/storage.test.ts` - 存储工具测试
- `tests/utils/game-logic.test.ts` - 游戏逻辑测试
- `tests/utils/constants.test.ts` - 常量定义测试
- `tests/utils/websocket.test.ts` - WebSocket 工具测试
- `tests/services/auth.service.test.ts` - 认证服务测试
- `tests/services/room.service.test.ts` - 房间服务测试
- `tests/services/game.service.test.ts` - 游戏服务测试
- `tests/mock/room.mock.test.ts` - 房间 Mock 测试
- `tests/mock/game.mock.test.ts` - 游戏 Mock 测试
- `tests/mock/data.test.ts` - Mock 数据测试

### 运行测试

```bash
# 运行所有测试
npm test

# 运行特定测试文件
npm test tests/utils/game-logic.test.ts

# 生成覆盖率报告
npm run test:coverage

# 查看覆盖率报告
open coverage/lcov-report/index.html
```

---

## 开发进度

### ✅ 已完成

- [x] 项目架构搭建
- [x] 基础工具类（request, storage, constants, game-logic）
- [x] 认证服务（登录、登出、用户信息管理）
- [x] 房间服务（创建、加入、查询、离开）
- [x] 游戏服务（开始、查询、投票）
- [x] WebSocket 实时通信
  - [x] 连接管理
  - [x] 断线重连
  - [x] 心跳检测
  - [x] 消息队列
- [x] 游戏流程完善
  - [x] 描述环节（发言输入、历史记录）
  - [x] 投票环节（倒计时、票数显示）
  - [x] 结果展示（胜利动画、身份揭示）
- [x] Mock 数据服务
- [x] 单元测试（覆盖率 82%+）
- [x] 登录页面
- [x] 首页（大厅）
- [x] 房间等待页
- [x] 游戏进行页
- [x] 个人中心
- [x] Git 版本管理
- [x] 自定义组件开发
  - [x] room-card（房间卡片）
  - [x] player-card（玩家卡片）
  - [x] word-display（词语展示）
  - [x] vote-modal（投票弹窗）
  - [x] game-status（游戏状态栏）

### 🚧 开发中

暂无

### 📋 待开发

#### 高优先级

- [ ] 错误处理优化
  - [ ] 统一错误提示
  - [ ] 异常捕获
  - [ ] 日志记录

#### 中优先级

- [ ] 游戏记录查询
- [ ] 玩家统计
- [ ] 房间分享功能
- [ ] 消息通知
- [ ] 性能优化

#### 低优先级

- [ ] 主题切换
- [ ] 多语言支持
- [ ] 离线模式
- [ ] AI 托管

---

## 相关项目

- 服务端项目：[mp-undercover](https://github.com/xiaolinstar/mp-undercover)
- GitHub 仓库：[xiaolinstar/undercover](https://github.com/xiaolinstar/undercover)

---

## 技术支持

### 官方文档

- [微信小程序官方文档](https://developers.weixin.qq.com/miniprogram/dev/framework/)
- [TypeScript 官方文档](https://www.typescriptlang.org/docs/)
- [Skyline 渲染引擎](https://developers.weixin.qq.com/miniprogram/dev/framework/runtime/skyline/)
- [Jest 测试框架](https://jestjs.io/docs/getting-started)

### 项目文档

- [架构设计文档](./ARCHITECTURE.md) - 查看详细架构设计
- [快速开始指南](./QUICKSTART.md) - 查看开发步骤

---

## 常见问题

### Q1: 如何切换 Mock 模式和真实 API？

编辑 `miniprogram/config/api.config.ts`，修改 `USE_MOCK` 字段。

### Q2: 测试覆盖率不达标怎么办？

运行 `npm run test:coverage` 查看详细报告，针对未覆盖的代码添加测试用例。

### Q3: 如何添加新页面？

1. 在 `miniprogram/pages/` 下创建页面目录
2. 创建 `.ts`, `.wxml`, `.scss`, `.json` 四个文件
3. 在 `miniprogram/app.json` 中注册页面

### Q4: 如何对接真实服务端？

1. 关闭 Mock 模式
2. 配置服务端 API 地址
3. 测试接口对接

---

## 许可证

MIT License

---

## 作者

[xiaolinstar](https://github.com/xiaolinstar)

---

## Star History

如果这个项目对你有帮助，请给个 ⭐️ Star 支持一下！
