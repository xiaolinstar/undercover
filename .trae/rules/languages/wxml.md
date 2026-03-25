---
description: 微信小程序 WXML 编写规范
globs: **/*.wxml
alwaysApply: false
---

# WXML 规则

- 标签和属性名使用小写
- 属性值用双引号包围
- 自闭合标签使用 `<tag />` 格式
- 数据绑定使用 `{{}}`，避免复杂逻辑
- 布尔属性使用 `attr="{{condition}}"` 格式
- 列表渲染必须设置 `wx:key`
- 组件标签名和类名使用 kebab-case 格式
- 事件绑定使用 `bind:` 前缀
- 避免内联样式，统一在 WXSS 中定义
