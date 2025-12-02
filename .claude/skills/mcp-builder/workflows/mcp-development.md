# MCP 服务器开发工作流

## 流程概览

```
研究规划 → 设计工具 → 实现开发 → 质量验证 → 评估测试
```

---

## 阶段 1：研究与规划

### 1.1 学习 MCP 协议
- 阅读 MCP 协议规范：https://modelcontextprotocol.io/llms-full.txt
- 理解工具注册、调用、响应机制
- 掌握输入 schema 和输出格式

### 1.2 研究目标 API
- 阅读目标服务的完整 API 文档
- 理解认证方式
- 了解速率限制和分页
- 识别关键端点和数据模型

### 1.3 设计工具集
根据 5 大设计原则：
1. **面向工作流**：设计完整任务工具，而非简单 API 包装
2. **优化上下文**：返回高信号信息，支持简洁/详细模式
3. **错误可操作**：提供明确的下一步建议
4. **自然划分**：工具名称反映人类思维
5. **评估驱动**：设计可验证的使用场景

### 1.4 创建实现计划
- 列出要实现的工具清单
- 设计共享工具函数
- 规划错误处理策略
- 定义输入/输出 schema

---

## 阶段 2：实现开发

### 2.1 搭建项目结构

**Python 项目**：
```
mcp-server/
├── server.py          # 主服务器文件
├── requirements.txt   # 依赖
└── .env              # 环境变量
```

**TypeScript 项目**：
```
mcp-server/
├── src/
│   └── index.ts      # 主服务器文件
├── package.json
├── tsconfig.json
└── .env
```

### 2.2 实现核心基础设施
在实现具体工具前，先创建：
- API 请求辅助函数
- 错误处理工具
- 响应格式化函数（JSON/Markdown）
- 分页处理
- 认证/令牌管理

### 2.3 系统化实现工具
对每个工具：
1. 定义输入 schema（Pydantic/Zod）
2. 编写详细的工具描述
3. 实现工具逻辑
4. 添加工具注解（readOnly、destructive 等）

**详细指南**：
- Python：参考 `guides/python_mcp_server.md`
- TypeScript：参考 `guides/node_mcp_server.md`
- 最佳实践：参考 `guides/mcp_best_practices.md`

---

## 阶段 3：质量验证

### 3.1 代码质量审查
- DRY 原则（无重复代码）
- 可组合性（共享逻辑提取）
- 一致性（相似操作返回相似格式）
- 错误处理完整
- 类型安全（Python type hints / TypeScript types）

### 3.2 测试与构建

**Python**：
```bash
# 验证语法
python -m py_compile server.py

# 运行服务器（tmux 中测试）
python server.py
```

**TypeScript**：
```bash
# 构建项目
npm run build

# 验证输出
ls dist/index.js
```

### 3.3 连接测试
使用 `scripts/connections.py` 测试 stdio/sse 连接：
```bash
python scripts/connections.py --stdio server.py
python scripts/connections.py --sse http://localhost:3000
```

---

## 阶段 4：评估测试

### 4.1 创建评估场景
设计 10 个真实、复杂的使用场景：
- 独立（不依赖其他问题）
- 只读（非破坏性操作）
- 复杂（需要多次工具调用）
- 真实（基于实际用例）
- 可验证（有明确答案）
- 稳定（答案不随时间变化）

### 4.2 编写评估用例
创建 XML 格式评估文件：
```xml
<evaluation>
  <qa_pair>
    <question>具体的问题...</question>
    <answer>可验证的答案</answer>
  </qa_pair>
  <!-- 更多 qa_pair... -->
</evaluation>
```

### 4.3 运行评估
```bash
python scripts/evaluation.py \
  --server server.py \
  --eval evaluation.xml
```

**详细指南**：参考 `guides/evaluation.md`

---

## 常见场景

### 场景 1：GitHub MCP 服务器
**工具设计**：
- `search_issues`：搜索问题（支持过滤）
- `create_issue`：创建问题（验证 + 创建）
- `list_pull_requests`：列出 PR（分页支持）

**关键设计**：
- 提供简洁/详细两种响应模式
- 错误消息包含 GitHub 文档链接
- 自动处理分页（返回前 N 个结果）

### 场景 2：数据库查询 MCP
**工具设计**：
- `query_data`：执行安全的只读查询
- `get_schema`：获取表结构
- `explain_query`：查询计划分析

**关键设计**：
- 只允许 SELECT 查询（安全）
- 自动限制返回行数
- Markdown 表格格式化输出

---

## 质量标准

### 代码质量
- 类型完整（Python type hints / TypeScript strict mode）
- 无重复代码
- 错误处理完善
- 文档清晰

### 工具质量
- 描述准确详细
- Schema 约束合理
- 错误消息可操作
- 响应格式一致

### 代理友好度
- 上下文效率高
- 工具发现性好
- 使用直观
- 反馈及时

---

## 快速参考

### MCP 官方资源
- 协议规范：https://modelcontextprotocol.io
- Python SDK：https://github.com/modelcontextprotocol/python-sdk
- TypeScript SDK：https://github.com/modelcontextprotocol/typescript-sdk

### Skill 内部资源
- 最佳实践：`guides/mcp_best_practices.md`
- Python 指南：`guides/python_mcp_server.md`
- TypeScript 指南：`guides/node_mcp_server.md`
- 评估指南：`guides/evaluation.md`
