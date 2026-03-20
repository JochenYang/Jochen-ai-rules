# Response Contract

This contract keeps `read` and overview answers aligned with the same product
boundary used in the README and SKILL docs:

- `read` = quick implementation summary
- project overview = high-signal repo orientation
- `report` = deeper host-side expansion from `deep-pack`

Use this reference when summarizing the snapshot for a user or turning a
`read` payload into an explanation.

## Required Sections For Read

Treat `read` as a quick implementation summary for fast code understanding.
The answer should help the next model know where to read first and what the
main path does, without expanding into a long report.

Preferred section order:

1. `一句话结论`
   - State the core implementation file and the main execution path.
2. `调用入口`
   - Name the UI, API, CLI, IPC, route, or command entry when available.
3. `核心实现`
   - List 3-4 high-value files and explain each file in one sentence.
4. `关键锚点`
   - Surface 3-5 functions, methods, commands, or anchors worth reading next.
5. `一句话总结`
   - Summarize the implementation approach in one sentence.

Read-specific rules:

- Prefer entry points and execution flow before data models or type summaries
- Do not expand into a full architecture essay
- Avoid long tables unless the source structure is naturally tabular
- Stop once a model can continue code reading efficiently
- Leave edge cases, exhaustive tracing, and broad explanation to `report`

## Required Sections For Project Overview

When summarizing a snapshot, produce a Chinese report that uses the snapshot as
evidence instead of improvising from file names alone.

Minimum sections:

1. `项目定位`
   - State project type, main stack, repo/workspace shape
   - Distinguish fact from inference
2. `架构边界`
   - Explain major runtime or package boundaries using `summary`, `workspace`,
     `modules`, and `graph`
   - For Electron-style apps, explicitly call out `main`, `renderer`, preload,
     or extension boundaries when supported by the snapshot
3. `核心关系`
   - Use `graph.moduleDependencies`, `graph.hotspots`, `importantFiles`, and
     `entryPoints` to describe how important modules connect
4. `任务入口`
   - Surface at least 3 task-oriented reading paths from `contextPacks`
   - Preferred tasks: `understand-project`, `feature-delivery`,
     `bugfix-investigation`, `code-review`, `onboarding`
5. `置信度与回退项`
   - Report analyzer engines from `analysis.engines`
   - Quote fallback reasons from `analysis.warnings`
   - Distinguish high-confidence facts from heuristic inferences
6. `补充上下文`
   - Use `externalContext` to mention recent changes, docs, decisions, or team
     conventions when available

## Facts, Inference, And Fallback

- Label direct snapshot facts as `事实`
- Label architecture or role judgments as `推断`
- Label analyzer limitations as `回退`
- Never invent reasons that are not supported by the snapshot
- If TypeScript analysis falls back, do not say `缺少 tsconfig` unless the
  snapshot explicitly proves that; prefer the exact warning from `analysis`
- If the repo is dirty, mention it briefly but do not let it dominate the
  summary unless the task is bugfix or review

## Task-Oriented Presentation

When `contextPacks` are present, do not only list important files. Convert them
into actionable reading guides:

- `understand-project`: where a new model should start and why
- `feature-delivery`: which files are likely to contain implementation patterns
- `bugfix-investigation`: which files are close to recent changes or execution paths
- `code-review`: which files form the immediate risk surface
- `onboarding`: which files best explain conventions and structure

Each task entry should include:

- 1 sentence goal
- 3-6 files
- a brief `why these files` explanation using pack reasons, hotspots, or graph links

## Quality Bar

Avoid stopping at:

- project name
- tech stack
- file count
- a flat list of important files

The final answer should help the next model understand:

- where the architectural boundaries are
- which modules are central
- how to start reading for a specific task
- which parts of the snapshot are high-confidence versus heuristic
