---
description: Docker Compose 规则
globs: **/docker-compose*.yml, **/docker-compose*.yaml
alwaysApply: false
---

# Docker Compose 规则

- 参考 [Compose Specification](https://github.com/compose-spec/compose-spec)
- version 字段可选（Docker Compose 1.27.0+ 推荐省略，使用最新格式）
- 优先使用更现代的 `compose.yml`，其次使用 `docker-compose.yml`
- 指定非默认文件使用 `.` 而不是 `-` 分隔符，例如 `compose.dev.yml` 而不是 `docker-compose-dev.yml`
- 为所有关键服务配置健康检查
- 使用条件依赖（service_started、service_healthy）
- 推荐使用 `env_file` 加载环境变量，避免硬编码敏感信息
- 使用命名卷进行数据持久化
- 配置适当的资源限制（cpus、memory）
- 使用相对路径引用文件和目录
- 为生产环境配置重启策略（restart: always）
- 使用自定义网络隔离不同服务
- 配置日志轮转，避免磁盘空间耗尽
- 不要在 Compose 文件中硬编码密码和密钥
