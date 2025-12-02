---
name: artifacts-builder
description: 快速构建 React 交互式原型和单文件 HTML demo，使用 shadcn/ui 组件库一键打包，适用于产品演示、设计验证、交互测试。支持 40+ 组件可直接在浏览器预览和分享
---

# 前端原型构建工具

快速构建可分享的交互式原型，用于演示和产品验证。

## 核心能力

- React + TypeScript 交互式原型
- 40+ shadcn/ui 组件即用
- 单文件 HTML 打包分享
- 浏览器直接预览

## 技术栈

- **框架**：React 18 + TypeScript + Vite
- **样式**：Tailwind CSS + shadcn/ui
- **打包**：Parcel + html-inline

## 可执行工具

以下脚本可直接运行，无需读取源码：

- `scripts/init-artifact.sh` - 初始化项目结构
- `scripts/bundle-artifact.sh` - 打包成单文件 HTML

## 设计规范

 **禁止"AI 风格"设计**：

-  禁止使用渐变色背景
-  避免过度居中布局
-  避免纯白大圆角
-  避免默认 Inter 字体
-  使用纯色和明确的色彩层次

## 边界

专注于交互式原型构建，不用于生产环境代码。完整应用请使用 developer skill。

## 详细参考

- `workflows/artifact-building.md` - 完整构建流程
- `guides/quick-start.md` - 快速上手指南