# Snapshot Schema

Use this reference when you need field-level details about the generated
snapshot or retrieval payload.

Positioning reminder:

- snapshot = reusable repo context artifact
- `read` = retrieval payload built from snapshot and index
- `report` = `deep-pack` built from snapshot and index
- none of these modes imply a full rescan unless the mode explicitly requires it

## Snapshot Path

- Snapshot: `{project}/repo/progress/miloya-codebase.json`
- Index state: `{project}/repo/progress/miloya-codebase.index.json`

## Representative Snapshot Shape

```json
{
  "version": "3.0",
  "generatedAt": "2026-03-18T...",
  "projectPath": "/path/to/project",
  "sourceFingerprint": "sha256...",
  "freshness": {
    "stale": false,
    "reason": "source fingerprint unchanged",
    "newestSourceMtime": "2026-03-18T...",
    "snapshotPath": "repo/progress/miloya-codebase.json"
  },
  "git": {
    "branch": "main",
    "commit": "abc123",
    "status": "clean"
  },
  "summary": {
    "name": "project-name",
    "type": "web-api | frontend | monorepo | cli | ...",
    "description": "Short README-derived project summary",
    "techStack": ["React", "Node.js"],
    "entryPoints": ["src/index.ts"],
    "totalFiles": 234,
    "totalLines": 12840,
    "dominantLanguages": [{ "language": "TypeScript", "files": 120 }],
    "importantPaths": ["package.json", "src/index.ts"]
  },
  "workspace": {
    "isMonorepo": false,
    "rootManifests": ["package.json"],
    "packages": []
  },
  "analysis": {
    "engines": {
      "Python": "python-ast",
      "TypeScript": "typescript-regex-fallback"
    },
    "filesByEngine": {
      "python-ast": 3,
      "typescript-regex-fallback": 6
    },
    "warnings": ["typescript compiler unavailable; used regex fallback"]
  },
  "index": {
    "stateVersion": "1.0",
    "statePath": "repo/progress/miloya-codebase.index.json",
    "fileCount": 234,
    "chunkCount": 980,
    "reusedSnapshot": false
  },
  "contextHints": {
    "readOrder": ["package.json", "src/index.ts"],
    "recommendedStart": "package.json",
    "highSignalAreas": ["./", "src/"],
    "monorepo": false,
    "description": "Short README-derived project summary"
  },
  "importantFiles": [
    {
      "path": "src/index.ts",
      "role": "API surface",
      "language": "TypeScript",
      "lines": 180,
      "score": 152,
      "whyImportant": "entry point, 4 API routes, 3 exports"
    }
  ],
  "graph": {
    "stats": {
      "files": 234,
      "symbols": 540,
      "dependencyEdges": 620
    }
  },
  "retrieval": {
    "defaultTask": "understand-project",
    "availableTasks": [
      "understand-project",
      "feature-delivery",
      "bugfix-investigation",
      "code-review",
      "onboarding"
    ]
  }
}
```

## Consumption Order

When reading an existing snapshot or presenting a freshly generated one,
consume fields in this order:

1. `summary`, `workspace`, `analysis`, `freshness`, `git`
2. `contextHints`, `importantFiles`, `modules`
3. `graph`, especially `stats`, `moduleDependencies`, `hotspots`, `packages`
4. `contextPacks` and `retrieval`
5. `externalContext`
6. `representativeSnippets`, `apiRoutes`, `dataModels`, `keyFunctions`

Do not stop at the overview layer. The engine is most useful when graph,
task packs, and external context are surfaced together.

## Output Notes

- `analysis` reports which analyzers were used and whether any language fell back
- `index` and `chunkCatalog` support incremental indexing and retrieval
- `graph`, `retrieval`, `contextPacks`, and `externalContext` support task-aware context assembly
- `freshness` and `sourceFingerprint` determine whether a cached snapshot can be reused safely
- `importantFiles` ranks the highest-signal files for model reading order
- `representativeSnippets` provides short anchor snippets from those files
