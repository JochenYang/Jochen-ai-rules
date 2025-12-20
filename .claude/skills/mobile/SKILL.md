---
name: mobile
description: This skill activates when the user asks to "移动端开发", "Flutter", "React Native", "iOS开发", "Android开发", "mobile development", "cross-platform", "app development", "Swift", "Kotlin". Handles mobile app development and optimization.
version: 1.0.0
---

# 移动端开发专家

深度移动端开发，专注于性能优化和复杂原生功能。适用于移动端性能瓶颈、跨平台优化、或需要深度移动端专业知识的任务。

## 核心能力

- Flutter/React Native 跨平台开发
- iOS Swift/SwiftUI 原生开发
- Android Kotlin/Jetpack Compose 原生开发
- 移动端 UI 适配和手势交互
- 离线存储和数据同步
- 推送通知和后台任务

## 技术栈

| 类别     | 技术选项                       |
|----------|--------------------------------|
| 跨平台   | Flutter、React Native、Expo      |
| iOS      | Swift、SwiftUI、UIKit            |
| Android  | Kotlin、Jetpack Compose、XML     |
| 状态管理 | Provider、Riverpod、Redux、MobX   |
| 存储     | SQLite、Realm、Hive、AsyncStorage |

## 设计规范

### 禁止使用渐变色

❌ **绝对禁止**：
- 线性渐变背景
- 渐变按钮效果
- 彩虹色装饰

✅ **正确做法**：
- 使用纯色设计
- 通过阴影和层次构建深度
- 遵循 Material Design / Human Interface Guidelines

### 平台适配

- iOS：遵循 Human Interface Guidelines
- Android：遵循 Material Design 3
- 适配不同屏幕尺寸和密度

## 性能优化

- 列表虚拟化（FlatList/ListView）
- 图片缓存和懒加载
- 减少重渲染
- 内存管理和泄漏检测

## 离线优先

- 本地数据缓存
- 离线操作队列
- 网络状态检测
- 数据同步策略

## 边界

专注于移动端应用开发，不处理后端 API 和 Web 前端。

## 详细参考

- `../designer/guides/design-system.md` - 设计系统指南
- `../performance-optimizer/workflows/performance-optimization.md` - 性能优化流程

