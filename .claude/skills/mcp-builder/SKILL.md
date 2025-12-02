---
name: mcp-builder
description: 开发 MCP 服务器：设计面向 AI 代理的工具、实现 Python/TypeScript 服务器、创建评估测试。支持集成 GitHub/Notion/Slack 等第三方服务，包含完整开发模板和自动化脚本
---

# MCP 服务器开发工具

构建高质量的 Model Context Protocol 服务器，为 AI 代理提供外部工具能力。

## 核心能力

- MCP 协议理解和服务器架构设计
- Python/TypeScript SDK 实现
- 面向 AI 代理的工具 schema 设计
- 评估测试创建和验证

## 技术栈

| 语言       | SDK                | 验证库      | 运行时      |
|------------|--------------------|-------------|-------------|
| Python     | MCP Python SDK     | Pydantic v2 | asyncio     |
| TypeScript | MCP TypeScript SDK | Zod         | Node.js 18+ |

## 可执行工具

以下脚本可直接运行，无需读取源码：

- `scripts/evaluation.py` - 运行 MCP 服务器评估测试
- `scripts/connections.py` - 测试服务器连接状态

## 设计原则

1. **面向工作流**：构建完整任务工具，而非简单 API 包装
2. **优化上下文**：返回高信号信息，避免数据倾销
3. **可操作错误**：错误消息引导代理正确使用
4. **评估驱动**：早期创建评估场景，基于代理反馈迭代

## 边界

专注于 MCP 服务器开发和工具设计，不处理第三方 API 开发和客户端集成。

## 详细参考

- `workflows/mcp-development.md` - 完整开发流程
- `guides/mcp_best_practices.md` - MCP 最佳实践
- `guides/python_mcp_server.md` - Python 实现指南
- `guides/node_mcp_server.md` - TypeScript 实现指南
- `guides/evaluation.md` - 评估创建指南

## 官方文档

- MCP 协议：https://modelcontextprotocol.io
- Python SDK：https://github.com/modelcontextprotocol/python-sdk
- TypeScript SDK：https://github.com/modelcontextprotocol/typescript-sdk
