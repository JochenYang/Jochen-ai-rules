# context-codebase

<p align="center">
  <strong>Fast · Zero-dependency · Skill-native</strong><br/>
  <sub>Project context engine for repo orientation and code retrieval</sub><br/><br/>
  <a href="./README.md">English</a> ·
  <a href="./README_zh.md">简体中文</a><br/>
</p>

---

`context-codebase` is a project context engine that generates reusable snapshots
for fast repository understanding and task-focused code retrieval. Works as a
skill in any AI coding agent — no model downloads, no vector computation, no
external dependencies beyond Python stdlib + SQLite.

```text
Scan → Regex Chunk → FTS5 BM25 → Rank → Git Stats → Fuzzy Search → Snapshot
```

**Output**: `context-codebase.json` · `context-codebase.index.json` · `context-codebase.db`

---

## Quick Start

| Command | Purpose |
|---------|---------|
| `/context-codebase` | Generate or reuse snapshot → high-level repo overview |
| `/context-codebase read` | Consume snapshot → focused file & snippet retrieval |
| `/context-codebase refresh` | Incremental update after repo changes |
| `/context-codebase report` | Deep technical walkthrough (delegates to sub-agent) |

---

## Core Capabilities

| Layer | What It Provides |
|-------|-----------------|
| **Retrieval** | FTS5 BM25 keyword search (SQLite) — millisecond-level exact matching |
| **Chunking** | Regex-based 60-line windows with anchor-point overlap, works for all languages |
| **Navigation** | Dependency graph · importance ranking · hotspot detection · entry-point hints |
| **Symbol Search** | FuzzySymbolSearcher — IDE-style camelCase/snake_case fuzzy matching |
| **Git Integration** | Change frequency · hotspots · churn · author tracking |
| **Cache** | Source-fingerprint reuse — unchanged repos skip regeneration |

## Snapshot Layers

```
summary → workspace → analysis → contextHints → importantFiles
chunkCatalog → graph → retrieval → contextPacks → externalContext
apiRoutes → dataModels → keyFunctions → freshness → gitStats → symbolIndex
```

---

## Retrieval Model

Keyword-driven, no semantic embedding:

- **BM25** — FTS5 full-text search for lexical precision
- **Graph expansion** — dependency neighbors around high-scoring chunks
- **Importance boost** — key configs and entry-point files ranked higher
- **Recent-change boost** — recently modified files prioritized for bugfix/review tasks
- **Task packs** — pre-built reading plans per task type

Large projects (~1M LOC) target sub-7-minute snapshot generation.

> **Note**: First-time snapshot generation on large projects may take several
> minutes due to full-source scanning and FTS5 indexing. Progress is printed to
> stderr. Subsequent runs reuse cached artifacts and complete in seconds.

---

## Accuracy Boundary

| :white_check_mark: Strong at | :x: Not designed for |
|------------------------------|----------------------|
| Fast repo orientation | Compiler-grade cross-language indexing |
| Cached model handoff | Exact search in every edge case |
| High-signal reading order | Semantic/embedding search |
| Focused code retrieval | Real-time file monitoring |
| Large-repo navigation layer | IDE symbol resolution |

---

## CLI Usage

```bash
# Generate snapshot
python context-codebase/scripts/generate.py <project_path>

# Refresh index
python context-codebase/scripts/generate.py <project_path> refresh

# Task-focused retrieval
python context-codebase/scripts/generate.py <project_path> --read --task bugfix-investigation --query "auth middleware"

# Deep report
python context-codebase/scripts/generate.py <project_path> --report --task feature-delivery --query "payment flow"
```

CLI contract: `stdout` = JSON payload, `stderr` = warnings and progress.

---

## Installation

```
context-codebase/
├── SKILL.md              ← skill entry point
├── scripts/
│   ├── generate.py        ← main pipeline
│   └── context_engine/    ← analyzers, retrieval, FTS5, git, fuzzy search
├── tests/
│   └── test_enhanced.py
└── references/
```

Generated artifacts live under `{project}/repo/progress/` — keep them out of version control.

---

## Development

```bash
python -m unittest context-codebase.tests.test_enhanced -v
```

---

## License

Follow the host repository's license and internal distribution rules.
