# context-codebase

<p align="center">
  <strong>快速 · 零依赖 · Skill 原生</strong><br/>
  <sub>项目上下文引擎 — 仓库理解与代码检索</sub><br/><br/>
  <a href="./README.md">English</a> ·
  <a href="./README_zh.md">简体中文</a><br/>
</p>

---

`context-codebase` 是一个项目上下文引擎，生成可复用快照，支持快速仓库理解
和任务定向代码检索。可在任何 AI 编程助手中作为 skill 使用 —— 无需模型下载、
无需向量计算、零外部依赖（仅需 Python 标准库 + SQLite）。

```text
扫描 → 正则分块 → FTS5 BM25 → 排序 → Git 统计 → 模糊搜索 → 快照
```

**产出**：`context-codebase.json` · `context-codebase.index.json` · `context-codebase.db`

---

## 快速开始

| 命令 | 用途 |
|------|------|
| `/context-codebase` | 生成或复用快照 → 仓库高层概览 |
| `/context-codebase read` | 消费快照 → 定向文件与代码片段检索 |
| `/context-codebase refresh` | 仓库变化后增量刷新 |
| `/context-codebase report` | 深入技术分析（委派给子 agent） |

---

## 核心能力

| 层级 | 提供什么 |
|------|---------|
| **检索** | FTS5 BM25 关键词检索（SQLite）— 毫秒级精确匹配 |
| **分块** | 正则 60 行窗口 + 锚点重叠，所有语言通吃 |
| **导航** | 依赖图 · 重要性排序 · 热点检测 · 入口文件提示 |
| **符号搜索** | FuzzySymbolSearcher — IDE 风格 camelCase/snake_case 模糊匹配 |
| **Git 集成** | 变更频率 · 热点 · churn · 作者追踪 |
| **缓存** | 源码指纹复用 — 未变动仓库跳过重建 |

---

## 快照结构

```
summary → workspace → analysis → contextHints → importantFiles
chunkCatalog → graph → retrieval → contextPacks → externalContext
apiRoutes → dataModels → keyFunctions → freshness → gitStats → symbolIndex
```

---

## 检索模型

关键词驱动，无语义嵌入：

- **BM25** — FTS5 全文检索，词汇精确匹配
- **图扩展** — 高评分 chunk 的依赖图邻居
- **重要性加权** — 关键配置和入口文件排名更高
- **最近变更加权** — 近期修改文件在 bugfix/review 场景优先
- **任务包** — 按任务类型预构建阅读计划

大型项目（~100 万行代码）快照生成目标在 7 分钟内完成。

> **注意**：大型项目首次创建快照可能耗时数分钟，因为需要全量源码扫描和 FTS5
> 索引写入。进度信息会输出到 stderr。后续运行会复用缓存产物，秒级完成。

---

## 准确性边界

| :white_check_mark: 擅长 | :x: 不擅长 |
|--------------------------|-----------|
| 快速仓库认知 | 编译器级跨语言索引 |
| 缓存式模型交接 | 所有场景下替代精确搜索 |
| 高信号阅读顺序 | 语义/向量检索 |
| 定向代码检索 | 实时文件监控 |
| 大仓库导航层 | IDE 级符号解析 |

---

## CLI 用法

```bash
# 生成快照
python context-codebase/scripts/generate.py <项目路径>

# 增量刷新
python context-codebase/scripts/generate.py <项目路径> refresh

# 定向检索
python context-codebase/scripts/generate.py <项目路径> --read --task bugfix-investigation --query "认证 中间件"

# 深度报告
python context-codebase/scripts/generate.py <项目路径> --report --task feature-delivery --query "支付 流程"
```

CLI 约定：`stdout` = JSON 负载，`stderr` = 警告和进度。

---

## 安装结构

```
context-codebase/
├── SKILL.md              ← skill 入口
├── scripts/
│   ├── generate.py        ← 主管线
│   └── context_engine/    ← 分析器、检索、FTS5、Git、模糊搜索
├── tests/
│   └── test_enhanced.py
└── references/
```

生成产物位于 `{项目}/repo/progress/` 目录——建议不纳入版本管理。

---

## 开发

```bash
python -m unittest context-codebase.tests.test_enhanced -v
```

---

## 许可

请遵循宿主仓库的许可证和内部发布规范使用。
