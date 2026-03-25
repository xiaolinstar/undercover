---
description: 微信小程序开发的约定和最佳实践
globs: **/*.wxml, **/*.wxss, **/*.ts, **/*.json
alwaysApply: false
---

# 微信小程序规则

## 核心原则

- 使用 TypeScript 进行类型安全的开发
- 使用组件化开发，提高代码复用性
- 使用 Promise/async-await 处理异步操作
- 使用分包加载优化小程序启动性能
- 遵循微信小程序官方 API 规范
- 使用云开发或自建后端进行数据交互
- 实现统一的错误处理和用户提示
- 使用微信小程序原生能力（如登录、支付、分享）

## 项目结构

```
miniprogram/
├── app.json                # 小程序配置文件
├── app.ts                  # 小程序入口文件
├── app.scss                # 全局样式
├── sitemap.json            # 站点地图配置
├── pages/                  # 页面目录
├── components/             # 组件目录
├── services/               # 服务层（API 调用）
├── models/                 # 数据模型
├── types/                  # 类型定义
├── utils/                  # 工具函数
├── config/                 # 配置文件
├── assets/                 # 静态资源
└── mock/                   # 模拟数据（开发环境）
```

## 页面和组件规则

- 每个页面包含 4 个文件：.ts、.wxml、.scss、.json
- 每个组件包含 4 个文件：.ts、.wxml、.scss、.json
- 使用 TypeScript 定义页面和组件的属性、数据、方法
- 使用生命周期函数管理页面和组件状态
- 组件通过 properties 接收数据，通过 events 向外通信

