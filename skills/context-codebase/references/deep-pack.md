# Deep Pack Contract

Use this reference when the host runs `/context-codebase report`.

`report` should return a `deep-pack` rather than a finished essay. The pack is
the stable boundary between the context engine and the host.

Boundary reminder:

- `read` should stop at a quick implementation summary
- `report` should stop at a structured `deep-pack` when delegation is available
- the host decides whether to expand the pack into a longer report

## Minimum Expected Fields

- `mode=report`
- `reportMode=deep-pack`
- `questionType`
- `summary`
- `coreFiles`
- `snippets`
- `flowAnchors`
- `nextHops`
- `constraints`
- `recommendedReportShape`
- `hostHints`

## Host Responsibilities

- Prefer delegating `deep-pack` consumption to a subagent when available
- Keep the parent thread lightweight and summary-oriented
- Fall back to same-thread report generation only when delegation is unavailable
- Do not treat `report` as permission to immediately expand into repo reads on
  the parent thread after the pack is returned

## Parent Thread Rule

When delegation exists:

- generate the `deep-pack`
- hand it to the delegated worker
- stop at the pack boundary on the parent thread

Do not do this on the parent thread when delegation is available:

- `Read` more repo files
- run additional repo-wide `Search`
- expand into a full long report

## Recommended Host Flow

1. Run `generate.py ... --report ...`
2. Inspect `coreFiles`, `snippets`, `flowAnchors`, and `recommendedReportShape`
3. If a subagent or delegated worker exists, pass the pack there
4. If no delegation exists, generate a bounded deep report from the pack

## Report Constraints

Typical pack constraints include:

- prefer evidence over speculation
- avoid repo-wide search unless necessary
- preserve parent-thread tokens
- keep file, snippet, anchor, and next-hop counts bounded
- prefer returning summary first
