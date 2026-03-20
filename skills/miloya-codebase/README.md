# miloya-codebase

<p align="center">
  <strong>Language</strong><br/>
  <a href="./README.md">English</a> ·
  <a href="./README_zh.md">简体中文</a>
</p>

`miloya-codebase` is a project context engine for fast repository orientation,
cached handoff, and task-focused code retrieval.

It generates reusable artifacts under `repo/progress/` so a new model, a new
IDE session, or another tool can understand a codebase quickly without
rescanning the whole repository every time.

## What It Solves

Most repo summary tools stop at file trees, language counts, or symbol lists.
That is usually not enough for practical model handoff.

`miloya-codebase` is built to answer the questions that matter during a real
session:

- What kind of project is this?
- Which files should be read first?
- Which areas define the architecture?
- Can the current snapshot be reused safely?
- For a focused question, which files and anchors should be read next?

## Artifacts

The skill writes reusable outputs to:

- `repo/progress/miloya-codebase.json`
- `repo/progress/miloya-codebase.index.json`

These artifacts are designed for model consumption first, not just human
inspection.

## Quick Start

Use the mode that matches the question you need answered:

- `/miloya-codebase`: build or reuse a snapshot for high-level orientation
- `/miloya-codebase refresh`: force a fresh scan after meaningful repo changes
- `/miloya-codebase read`: answer a focused implementation question quickly
- `/miloya-codebase report`: prepare a deeper host-side technical walkthrough

## Modes

### `/miloya-codebase`

Default mode.

Behavior:

- generates a snapshot when none exists
- reuses the cached snapshot when the source fingerprint is unchanged
- returns a repo overview optimized for fast understanding

Use it when:

- entering a project for the first time
- switching models or IDEs
- rebuilding a high-level mental map of the repo

### `/miloya-codebase refresh`

Force-refresh mode.

Behavior:

- ignores cache reuse
- rescans the repository
- overwrites the existing snapshot

Use it when:

- the codebase changed significantly
- the current snapshot is stale
- you explicitly want a fresh scan

### `/miloya-codebase read`

Focused retrieval mode.

Behavior:

- consumes the existing snapshot and index
- skips forced regeneration
- returns a lightweight retrieval payload with:
  - `files`
  - `snippets`
  - `flowAnchors`
  - `nextHops`
  - `searchScope`
  - `hotspots`
  - `externalContext`

Use it when:

- the snapshot already exists
- you need a quick answer for a specific implementation question
- you want to preserve tokens and avoid a full rescan

`read` is optimized for quick implementation summaries:

- lead with the core conclusion
- show the call entry when available
- surface 3-4 core files
- surface 3-5 anchors worth reading next
- stop before it turns into a long technical report

### `/miloya-codebase report`

Deep-analysis mode.

Behavior:

- consumes the existing snapshot and index when available
- generates the snapshot first only if it is missing
- returns a `deep-pack` for host-side deep report generation

Use it when:

- you want a full technical walkthrough
- you need a broader call chain or architecture trace
- you want to keep the parent thread lightweight and delegate the deeper work

## Why It Is More Useful Than A File Tree

A file tree tells you where files exist.

A context engine should also tell you:

- where a model should start
- which files are worth the tokens
- which modules carry the strongest architectural signal
- whether the saved context is still valid
- how to approach a concrete task without opening the whole repository

That is the main difference this skill is designed around.

## Snapshot Contents

The snapshot and index expose several layers of context:

- `summary`: project identity, tech stack, entry points, dominant languages
- `workspace`: monorepo and package layout hints
- `analysis`: analyzer engines, warnings, and fallback details
- `contextHints`: recommended start file, read order, high-signal areas
- `importantFiles`: ranked files worth reading first
- `chunkCatalog`: reusable anchors for retrieval
- `graph`: dependency edges, module relationships, hotspots
- `retrieval`: task list, retrieval metadata, project vocabulary
- `contextPacks`: prebuilt task-oriented reading packs
- `externalContext`: recent changes, docs, conventions
- `apiRoutes`, `dataModels`, `keyFunctions`: extracted code structure
- `freshness` and `sourceFingerprint`: cache safety and reuse checks

## Retrieval Model

`miloya-codebase` uses a hybrid retrieval flow instead of plain grep or a pure
embedding-backed semantic search stack:

- snapshot and index reuse
- chunk-based keyword retrieval
- graph-aware expansion
- important-file boosting
- task-oriented read packs
- multilingual query expansion
- project-vocabulary-driven term expansion

This makes `read` fast enough for handoff workflows while still being useful
for focused implementation questions.

## Installation

This repository keeps the distributable skill under `./miloya-codebase/`.

Repository layout in this repo:

```text
.
├─ README.md
├─ README_zh.md
└─ miloya-codebase/
   ├─ SKILL.md
   ├─ scripts/
   ├─ tests/
   └─ references/
```

Packaged or installed skill layout:

```text
miloya-codebase/
  SKILL.md
  scripts/
    generate.py
```

Recommended development layout:

```text
miloya-codebase/
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

Keep generated outputs out of versioned source where possible:

- `repo/progress/`
- `node_modules/`
- `dist/`
- `build/`
- `__pycache__/`
- `*.pyc`

## Manual Script Usage

From this repository root, use:

```bash
python miloya-codebase/scripts/generate.py <project_path>
python miloya-codebase/scripts/generate.py <project_path> --force
python miloya-codebase/scripts/generate.py <project_path> --read
python miloya-codebase/scripts/generate.py <project_path> --read --task feature-delivery --query "skill download flow"
python miloya-codebase/scripts/generate.py <project_path> --report --task bugfix-investigation --query "message routing"
```

If the skill is installed elsewhere, replace `miloya-codebase/` with the
actual skill directory.

## Accuracy Boundary

This tool is optimized for practical context transfer.

It is strong at:

- fast repository orientation
- cached model handoff
- high-signal reading order
- focused code retrieval
- large-repo navigation

It is not designed to be:

- a compiler-grade cross-language indexer
- a replacement for exact repo search in every case
- an embedding-backed semantic search engine

Some extraction still depends on heuristics or regex fallback, especially when
JS/TS AST analysis is unavailable in the analyzed project.

In other words, this tool is designed to get a model oriented fast and point it
at the right code, not to replace exact search in every edge case.

## Development And Validation

Run tests with:

```bash
python -m unittest miloya-codebase.tests.test_generate
```

Current validation covers:

- self-reference exclusion
- route false-positive prevention
- Python AST extraction
- JS/TS fallback reporting
- snapshot reuse and invalidation
- chunk and index generation
- task-oriented retrieval
- read/report payload structure
- multilingual query expansion

## Current Status

The current implementation is suitable for active context-engine use in real
projects:

- reusable snapshot and index generation
- graph-aware retrieval and task packs
- `read` for lightweight implementation lookup
- `report` for deep-pack generation
- regression coverage for core behaviors

## Limitations

- some route, model, and function extraction is still heuristic
- `read` is a skill mode, not a full replacement for exact code search
- retrieval quality is high for common flows, but long-tail domain language can
  still benefit from direct repo search
- the design target is practical, reusable understanding rather than absolute
  precision

## License

Use this skill according to the host repository's license and internal
distribution rules.
