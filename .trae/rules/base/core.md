---
description: 项目通用规则
globs:
alwaysApply: true
---

# 项目通用规则

- 始终使用中文回复用户，但技术专有名词可保留英文（如 API、Python、DTO等）。
- 使用项目既有风格，不引入新风格，包括代码、文档或交互，默认延用项目中已有的格式、缩进、命名习惯。
- 尽可能少地输出内容，仅提供高信息密度回复，禁止无效寒暄、过度铺垫，只输出对当前任务有直接帮助的信息。
- 遵守[《中文文案排版指北》](https://www.bookstack.cn/read/chinese-copywriting-guidelines/README.md)标准排版格式：中文与英文之间加空格，中文与数字之间加空格；全角标点与其他字符之间不加空格。全中文语境下必须使用全角标点。
- 在安装 Skill、Subagent、Commands、MCP、Hook 时，根据所在项目上下文安装，例如在 TRAE 项目中安装 Skill时，安装到 `.trae/skills/` 目录下，而不是根目录下