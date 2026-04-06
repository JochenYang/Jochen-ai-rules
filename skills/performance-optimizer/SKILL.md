---
name: performance-optimizer
description: Performance bottleneck identification and optimization. Handles database query optimization, caching strategies, algorithm improvements, and Core Web Vitals tuning (LCP/FID/CLS). Use when user asks to optimize performance, improve speed, fix slow queries, or tune web vitals.
---

# Performance Optimizer

Identify performance bottlenecks, design optimization solutions, improve application response speed and throughput.

## Core Capabilities

- Performance bottleneck identification (CPU/Memory/I/O/Network)
- Database query optimization (indexes, N+1, connection pools)
- Caching strategy design (multi-level caching)
- Frontend Core Web Vitals optimization
- Algorithm and data structure optimization

## Core Principles

- **Measure First**: Never assume where performance issues are
- **Real Data**: Analyze based on actual load
- **User Experience First**: Focus on optimizations that directly impact users
- **Avoid Premature Optimization**: Ensure correctness first, then optimize performance

## Optimization Priority

| Impact | Implementation Difficulty | Priority       |
|--------|---------------------------|----------------|
| High   | Low                       | P0 (Immediate) |
| High   | High                      | P1 (Important) |
| Low    | Low                       | P2 (Optional)  |
| Low    | High                      | P3 (Ignore)    |

## Core Web Vitals Targets

- **LCP** < 2.5s (Largest Contentful Paint)
- **FID** < 100ms (First Input Delay)
- **CLS** < 0.1 (Cumulative Layout Shift)

## Boundaries

Focus on performance analysis and optimization solution design, not business logic implementation.

## When NOT to Use

- Writing new features → use `developer`
- Frontend UI implementation → use `frontend-design`
- API design → use `api-designer`
- Database schema design → use `database-engineer`
- Security auditing → use `quality-assurance`

## Escalation Rules

Pause and ask the owner before:

- making optimization changes without measurement evidence
- trading correctness, readability, or maintainability for marginal speed gains
- expanding hotspot tuning into a broad refactor without scope agreement

## Final Output Contract (MANDATORY)

Every use of this skill should end with:

1. `Skill Fit` - why performance work is the right focus
2. `Primary Deliverable` - bottleneck analysis, optimization plan, or implemented improvement
3. `Execution Evidence` - metrics, profiling data, and validation checks used
4. `Risks / Open Questions` - measurement gaps, regression risk, or scaling uncertainty
5. `Next Action` - the next benchmark, fix, or review step
