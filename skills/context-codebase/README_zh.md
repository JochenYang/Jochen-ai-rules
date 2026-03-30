# context-codebase

<p align="center">
  <strong>语言</strong><br/>
  <a href="./README.md">English</a> ·
  <a href="./README_zh.md">简体中文</a>
</p>

`context-codebase` 是一个用于仓库快速理解、缓存式上下文交接和任务定向检索的
Context Engine。

它会在项目内的 `repo/progress/` 下生成可复用产物，让新的模型、新的 IDE 会话
或其他工具无需每次都重新全量扫描仓库，也能快速建立项目上下文。

## 它解决什么问题

很多仓库分析工具只停留在文件树、语言统计或符号列表层面，这对真实协作中的模
型交接并不够。

`context-codebase` 关注的是更实际的问题：

- 这是什么类型的项目？
- 应该先读哪些文件？
- 哪些区域最能代表整体架构？
- 当前快照是否还能安全复用？
- 当我问一个具体实现问题时，应该先看哪些文件和锚点？

## 产物

skill 会生成并复用以下文件：

- `repo/progress/context-codebase.json`
- `repo/progress/context-codebase.index.json`

这些产物首先是给模型消费的，不只是给人类查看。

## 快速开始

按问题类型选择模式即可：

- `/context-codebase`：生成或复用快照，用于建立整体认知
- `/context-codebase refresh`：在仓库明显变化后强制重扫
- `/context-codebase read`：快速回答具体实现问题
- `/context-codebase report`：为宿主侧生成更深入的技术分析输入

## 模式

### `/context-codebase`

默认模式。

行为：

- 快照不存在时生成新快照
- 源码指纹未变化时复用已有快照
- 返回适合快速理解仓库的高层概览

适用场景：

- 第一次进入项目
- 切换模型或切换 IDE
- 快速恢复对仓库的整体认知

### `/context-codebase refresh`

强制刷新模式。

行为：

- 不复用缓存
- 重新扫描仓库
- 覆盖现有快照

适用场景：

- 代码发生明显变化
- 当前快照已经过时
- 你明确想要重新扫描一遍

### `/context-codebase read`

定向检索模式。

行为：

- 直接消费已有快照和索引
- 跳过强制重建
- 返回轻量检索 payload，包含：
  - `files`
  - `snippets`
  - `flowAnchors`
  - `nextHops`
  - `searchScope`
  - `hotspots`
  - `externalContext`

适用场景：

- 快照已经存在
- 你要回答一个具体实现问题
- 想节省 token，不做全量重扫

`read` 的定位是“快速实现摘要”，不是长篇技术报告：

- 先给一句话结论
- 再给调用入口
- 再列 3 到 4 个核心文件
- 再列 3 到 5 个关键锚点
- 停在“足够继续深读代码”的边界

### `/context-codebase report`

深度分析模式。

行为：

- 优先消费已有快照和索引
- 只有快照缺失时才先生成
- 返回 `deep-pack`，供宿主侧生成长报告

适用场景：

- 需要完整技术分析
- 需要更长的调用链或架构追踪
- 想让主线程保持轻量，把深度工作交给下游

## 为什么它比普通文件树更有用

普通文件树只能回答“文件在哪里”。

真正有价值的 Context Engine 还应该回答：

- 模型应该从哪里开始读
- 哪些文件最值得消耗 token
- 哪些模块承载了最强的架构信号
- 当前缓存上下文是否仍然可信
- 遇到一个具体问题时，应该先走哪条阅读路径

这正是这个 skill 的核心设计目标。

## 快照包含什么

快照和索引大致分为几层信息：

- `summary`：项目身份、技术栈、入口点、主语言
- `workspace`：monorepo 与包结构提示
- `analysis`：分析器、回退信息、警告
- `contextHints`：推荐起始文件、阅读顺序、高信号区域
- `importantFiles`：优先阅读文件
- `chunkCatalog`：可复用的检索锚点
- `graph`：依赖关系、模块关系、热点区域
- `retrieval`：任务列表、检索元数据、项目词汇表
- `contextPacks`：按任务预构建的阅读包
- `externalContext`：最近变更、文档、团队约定
- `apiRoutes`、`dataModels`、`keyFunctions`：提取出的代码结构
- `freshness`、`sourceFingerprint`：缓存是否可复用

## 检索模型

`context-codebase` 不是纯 grep，也不是纯 embedding 语义搜索。当前使用的是混合
检索流程：

- 快照与索引复用
- 基于 chunk 的关键词召回
- 图扩展
- 高价值文件加权
- 面向任务的阅读包
- 多语言 query 扩展
- 基于项目词汇表的本地术语扩展

这让 `read` 在保持轻量的同时，仍然能回答不少具体实现问题。

## 安装结构

当前仓库中，可分发的 skill 源文件位于 `./context-codebase/`。

本仓库的目录结构：

```text
.
├─ README.md
├─ README_zh.md
└─ context-codebase/
   ├─ SKILL.md
   ├─ scripts/
   ├─ tests/
   └─ references/
```

安装后或分发后的 skill 结构：

```text
context-codebase/
  SKILL.md
  scripts/
    generate.py
```

推荐开发结构：

```text
context-codebase/
  SKILL.md
  scripts/
    generate.py
    context_engine/
  tests/
    test_generate.py
  references/
  README.md
  README_zh.md
```

建议不要把这些生成物纳入版本管理：

- `repo/progress/`
- `node_modules/`
- `dist/`
- `build/`
- `__pycache__/`
- `*.pyc`

## 脚本直接使用

在当前仓库根目录下，可直接这样运行：

```bash
python context-codebase/scripts/generate.py <项目路径>
python context-codebase/scripts/generate.py <项目路径> --force
python context-codebase/scripts/generate.py <项目路径> --read
python context-codebase/scripts/generate.py <项目路径> --read --task feature-delivery --query "skill download flow"
python context-codebase/scripts/generate.py <项目路径> --report --task bugfix-investigation --query "message routing"
```

如果 skill 安装在别的位置，把这里的 `context-codebase/` 替换成实际 skill 目录即可。

## 准确性边界

这个工具优化的是“实用的上下文迁移效率”。

它擅长：

- 快速建立仓库认知
- 缓存式模型交接
- 给出高信号阅读顺序
- 做定向实现检索
- 为大型仓库提供导航层

它并不是：

- 编译器级的跨语言索引器
- 每个场景下都替代精确代码搜索的工具
- embedding 驱动的黑盒语义搜索

部分提取仍然依赖启发式或 regex fallback，尤其是在 JS/TS AST 不可用时。

换句话说，它的目标是帮助模型尽快找对代码和阅读路径，而不是在所有边缘场景下
替代精确搜索。

## 开发与验证

运行测试：

```bash
python -m unittest context-codebase.tests.test_generate
```

当前测试覆盖：

- 排除对自身产物的自引用扫描
- 路由误报防护
- Python AST 提取
- JS/TS fallback 报告
- 快照复用与失效
- chunk 与索引生成
- 任务定向检索
- read/report payload 结构
- 多语言 query 扩展

## 当前状态

当前实现已经适合真实项目里的 context-engine 场景：

- 可复用快照和索引生成
- 图感知检索与任务包
- `read` 用于轻量实现定位
- `report` 用于 deep-pack 生成
- 核心行为已有回归测试

## 已知限制

- 某些语言的路由、模型和函数提取仍带有启发式成分
- `read` 是 skill 模式，不是精确搜索的完全替代品
- 常见流程的检索效果已经较好，但长尾领域词汇仍可能需要 repo search 补充
- 设计目标不是绝对精确，而是高效、可靠、可复用的项目理解

## 许可

请遵循宿主仓库的许可证和内部发布规范使用。
