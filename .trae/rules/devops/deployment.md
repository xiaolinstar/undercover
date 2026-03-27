---
description: 项目部署规则
globs:
alwaysApply: true
---

# 项目部署规则

## 环境分离

- 项目分为三个环境：开发环境、预发布环境、生产环境
- 使用配置文件来区分环境差异
- 生产环境要做特殊环境变量检查，如 `appid`, `secret` 等