---
name: miloya-codebase
description: Project context engine for repo orientation, cached handoff, and task-focused code retrieval. Usage: /miloya-codebase [refresh|read|report]
---

# miloya-codebase

Project context engine for fast repo orientation, cached handoff, and
task-focused code retrieval.

Artifacts:

- Snapshot: `{project}/repo/progress/miloya-codebase.json`
- Index state: `{project}/repo/progress/miloya-codebase.index.json`

## When To Use

Use this skill when you need to:

- understand a codebase quickly
- refresh a reusable project snapshot
- retrieve focused files and snippets for a concrete question
- prepare a deep technical walkthrough from a cached project context

## Modes

### `/miloya-codebase`

Default entry.

Behavior:

- Generate a new snapshot when none exists
- Reuse the cached snapshot when the source fingerprint is unchanged
- Return a project overview optimized for fast model understanding

Use it when:

- entering a project for the first time
- switching to a new model or IDE
- you want a general repo overview

### `/miloya-codebase refresh`

Force regenerate the snapshot.

Behavior:

- Ignore cache reuse
- Re-scan the project and overwrite the existing snapshot

Use it when:

- the codebase changed significantly
- you suspect the snapshot is stale
- you explicitly do not want cache reuse

### `/miloya-codebase read`

Focused retrieval mode.

Behavior:

- Consume the existing snapshot and index
- Skip forced regeneration logic
- Return a retrieval-oriented payload with:
  - `files`
  - `snippets`
  - `flowAnchors`
  - `nextHops`
  - `searchScope`
  - `hotspots`
  - `externalContext`

Use it when:

- the snapshot already exists
- you want fast file and snippet retrieval for a specific question
- you want to preserve tokens and avoid rescanning

Host requirements:

- Explicitly say read mode is consuming the existing snapshot and index
- Do not imply the repo is being rescanned
- Start from `files`, `snippets`, `nextHops`, and `searchScope`
- Do not jump to repo-wide search first

Preferred opening:

- `我将直接读取已有快照和索引，不重新扫描仓库。`
- `我会先用 read payload 里的 files、snippets 和 nextHops 做定点读取，不先做全仓搜索。`

Avoid:

- `我先重新加载项目上下文。`
- `我先重新扫描仓库。`

Read answer contract:

- Treat `read` as a quick implementation summary, not a deep technical report
- Use this order when the payload has enough evidence:
  1. one-sentence conclusion
  2. call entry
  3. core implementation files
  4. key anchors
  5. one-sentence implementation summary
- Prefer 3-4 core files and 3-5 anchors
- Prioritize entry points and execution flow before type definitions or tables
- Stop once the next model can continue reading code efficiently
- Leave exhaustive tracing, edge cases, and broader architecture to `report`

### `/miloya-codebase report`

Deep-analysis mode.

Behavior:

- Consume the existing snapshot and index when present
- Generate a snapshot first only when missing
- Return a `deep-pack` for host-side deep report generation
- Treat `deep-pack` generation as the default stopping point for the parent thread

Use it when:

- you want a full technical report
- you want a complete call chain or architecture trace
- you want to preserve the parent thread token budget

Host requirements:

- Explicitly say report mode is consuming the existing snapshot and index
- Mention snapshot generation only if the snapshot is actually missing
- Prefer delegating `deep-pack` to a subagent or delegated worker
- Do not continue parent-thread `Read` / `Search` expansion after the pack is
  generated unless delegation is unavailable

Preferred opening:

- `我将基于已有快照和索引生成 deep-pack，不重新扫描仓库。`
- `如果宿主支持 subagent，我会优先把 deep-pack 交给子任务处理。`
- `在可委派的情况下，我会停在 deep-pack 边界，不在主线程继续展开长报告。`

Avoid:

- `我先重新分析整个仓库再写报告。`
- `deep-pack 已生成，现在我继续在主线程读取关键文件并输出完整长报告。`

## Execution Semantics

The entrypoint is always `scripts/generate.py`, but the mode determines whether
source code is scanned or cached artifacts are consumed:

- default mode: may generate a snapshot or reuse a cached one
- `refresh`: always rescans and overwrites the cached snapshot
- `read`: consumes the existing snapshot and index to build a retrieval payload
- `report`: consumes the existing snapshot and index to build a `deep-pack`

Important clarifications:

- Seeing `python ... generate.py ... --read` or `--report` does not mean the
  repo is being rescanned
- `freshness.reason` inside a `read` or `report` payload describes how the
  current snapshot was produced previously; it does not mean the current
  invocation regenerated the snapshot
- `git.status=dirty` means the worktree has uncommitted changes; it does not
  automatically prove that the snapshot fingerprint changed

## Retrieval Workflow

For `read`:

1. Inspect `files`, `snippets`, `flowAnchors`, `nextHops`, and `searchScope`
2. Read suggested files directly when possible
3. Only widen to repo search if the payload is insufficient
4. Exclude `repo/progress/`, `node_modules/`, `dist/`, `build/`, and
   `__pycache__/` when widening search

For `report`:

1. Inspect `coreFiles`, `snippets`, `flowAnchors`, and `recommendedReportShape`
2. If the host supports subagents, pass the `deep-pack` there
3. Stop at the pack boundary on the parent thread when delegation is available
4. Fall back to same-thread deep reporting only when delegation is unavailable

## Query Guidance

For focused questions, prefer `--task` with a UTF-8 safe query channel.

On Windows or any environment where non-ASCII query text may become mojibake:

- Prefer `--query-escaped <ascii_only_query>`
- Then `--query-file <utf8_file>`
- Then `--query-stdin`
- Avoid raw `--query` for non-ASCII input when the shell is unreliable

## Manual Script Usage

Replace `{skill_dir}` with the actual installed skill path. In this repository,
that path is `miloya-codebase/`.

```bash
python {skill_dir}/scripts/generate.py <project_path>
python {skill_dir}/scripts/generate.py <project_path> --force
python {skill_dir}/scripts/generate.py <project_path> --read
python {skill_dir}/scripts/generate.py <project_path> --read --task feature-delivery --query "skill lifecycle runtime"
python {skill_dir}/scripts/generate.py <project_path> --read --task feature-delivery --query-escaped "\\u6280\\u80fd\\u7ba1\\u7406\\u5668\\u5982\\u4f55\\u5b9e\\u73b0"
python {skill_dir}/scripts/generate.py <project_path> --read --task feature-delivery --query-file query.txt
python {skill_dir}/scripts/generate.py <project_path> --report --task feature-delivery --query "skill download flow"
cat query.txt | python {skill_dir}/scripts/generate.py <project_path> --read --task feature-delivery --query-stdin
```

Windows-safe example:

```powershell
python {skill_dir}/scripts/generate.py <project_path> --read --task feature-delivery --query-escaped "\\u6280\\u80fd\\u4e0b\\u8f7d\\u6d41\\u7a0b"
```

## References

Read these only when needed:

- [references/snapshot-schema.md](references/snapshot-schema.md)
  - read when you need field-level snapshot or retrieval payload details
- [references/response-contract.md](references/response-contract.md)
  - read when you need the full presentation contract for overview or read-mode outputs
- [references/deep-pack.md](references/deep-pack.md)
  - read when you need the `report` protocol, host delegation rules, or deep-pack fields

## Core Rules

- Exclude generated/vendor noise such as `.git`, `node_modules`, `dist`,
  `build`, `__pycache__`, and `repo/progress`
- Avoid self-referential scans of the skill's own output
- Prefer cached artifacts over rescanning whenever the mode allows it
- Use `read` for focused retrieval and `report` for deep-pack generation
- Keep the parent thread lightweight in `report` mode when delegation exists
