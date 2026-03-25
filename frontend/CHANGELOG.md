# 更新日志

所有重要的更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## 未发布

**新增**:
- WebSocket 实时通信
  - 连接管理（connect、disconnect）
  - 心跳检测（30 秒间隔）
  - 断线重连（最多 5 次）
  - 消息队列（离线消息缓存）
  - 事件订阅机制
- 游戏流程完善
  - 描述环节：发言输入弹窗、历史记录
  - 投票环节：倒计时、票数实时显示
  - 游戏结束：胜利动画、身份揭示
- 完整的项目架构文档
- 快速开始指南
- Mock 开发模式
- 单元测试框架
- 测试覆盖率报告（82%+）

**待开发**:
- 错误处理优化
- 游戏记录查询
- 玩家统计功能
- 房间分享功能

## 1.0.0 - 2025-02-14

**新增**:
- 项目基础架构
  - TypeScript 配置
  - SCSS 样式支持
  - Skyline 渲染引擎
  - glass-easel 组件框架
- 核心功能
  - 微信登录功能
  - 房间创建和加入
  - 游戏流程管理
  - 投票系统
  - 游戏结束判定
- 页面开发
  - 登录页面
  - 首页（大厅）
  - 房间等待页
  - 游戏进行页
  - 个人中心
- 服务层
  - AuthService（认证服务）
  - RoomService（房间服务）
  - GameService（游戏服务）
- 工具类
  - Request（网络请求封装）
  - Storage（本地存储）
  - Constants（常量定义）
  - GameLogic（游戏逻辑）
- Mock 服务
  - MockAuthService（Mock 认证）
  - MockRoomService（Mock 房间）
  - MockGameService（Mock 游戏）
  - Mock 数据生成
- 测试
  - Jest 配置
  - 测试环境设置
  - 单元测试（70+ 测试用例）
  - 测试覆盖率 70%+
- 文档
  - README.md
  - ARCHITECTURE.md
  - QUICKSTART.md
  - CHANGELOG.md
- 版本管理
  - Git 初始化
  - .gitignore 配置
  - 首次提交

**技术栈**:
- TypeScript 5.x
- 微信小程序基础库 2.32.3
- Jest 29.7.0
- SCSS
- Skyline 渲染引擎

## 版本规划

**1.1.0（计划中）**:
- 错误处理优化
- 游戏记录查询
- 玩家统计
- 性能优化

**1.2.0（计划中）**:
- 房间分享
- 消息通知
- 主题切换

**2.0.0（远期规划）**:
- 多语言支持
- 离线模式
- AI 托管
