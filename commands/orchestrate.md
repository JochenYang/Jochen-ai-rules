# Orchestrate Command

Sequential agent workflow for complex tasks. This command coordinates a chain of specialized **Agents** (defined in `.claude/agents/`) to complete features, bug fixes, or refactors.

## Usage

`/orchestrate [workflow-type] [task-description]`

## Critical Rule

**The orchestrator is a COORDINATOR, not an implementer.** It MUST NEVER directly edit code, fix issues, or make changes itself. All implementation and fixes MUST be delegated to the appropriate agent. If you find yourself about to write or modify code, STOP and invoke the correct agent instead.

## Workflow Types

### feature

Full feature implementation workflow:
`dev-planner` → `code-implementer` → `code-reviewer` ↺ (Loop if changes needed)

### feature-tdd

Test-driven feature implementation workflow:
`dev-planner` → `tdd-guide` → `code-reviewer` ↺ (Loop if changes needed)

### bugfix

Deep bug investigation and resolution workflow:
`bug-analyzer` → `tdd-guide` → `code-reviewer` ↺ (Loop if changes needed)

### refactor

Safe refactoring workflow:
`dev-planner` → `code-implementer` → `code-reviewer` ↺ (Loop if changes needed)

### ui-design

Full cycle UI/UX optimization and implementation workflow:
`story-generator` → `ui-sketcher` → `dev-planner` → `code-implementer` → `code-reviewer` ↺ (Loop if changes needed)

### secure-feature

Security-hardened feature implementation workflow (for auth, payment, RBAC, sensitive data):
`dev-planner` → `code-implementer` → `security-reviewer` → `code-reviewer` ↺ (Loop if changes needed)

> **When to use**: Any feature touching authentication, authorization, payments, session management, API keys, PII/sensitive data, or RBAC.

### db-feature

Database schema change + feature implementation workflow:
`dev-planner` → `database-migration` → `code-implementer` → `code-reviewer` ↺ (Loop if changes needed)

> **When to use**: Any feature that requires new tables, schema alterations, index changes, or cross-database migrations.

### performance-audit

Performance profiling and optimization workflow:
`performance-optimizer` → `code-implementer` → `code-reviewer` ↺ (Loop if changes needed)

> **When to use**: Diagnosed performance complaints — slow endpoints, high latency, poor Core Web Vitals, N+1 queries, memory leaks.

### deploy

CI/CD pipeline and infrastructure setup workflow:
`dev-planner` → `devops-engineer` → `code-reviewer` ↺ (Loop if changes needed)

> **When to use**: Setting up or updating Dockerfile, GitHub Actions, Kubernetes configs, monitoring, or deployment pipelines.

## Review Feedback Loop (MANDATORY)

This is the most critical part of the orchestration. Follow these rules with ZERO exceptions.

### Step 1: Parse Reviewer Output

After invoking `code-reviewer`, extract the `Recommendation` field from its output. It will be one of:

- **SHIP** → Workflow complete. Proceed to Final Report.
- **NEEDS WORK** → Issues found. MUST enter repair loop.
- **BLOCKED** → Critical issues. MUST enter repair loop.

### Step 2: Repair Loop (when NOT SHIP)

┌─────────────────────────────────────────────────┐
│ REPAIR LOOP STATE MACHINE │
│ │
│ code-reviewer returns NEEDS WORK or BLOCKED │
│ │ │
│ ▼ │
│ ┌──────────────────────────┐ │
│ │ Identify repair agent: │ │
│ │ - feature/refactor → │ │
│ │ code-implementer │ │
│ │ - feature-tdd/bugfix → │ │
│ │ tdd-guide │ │
│ └──────────┬───────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────────────┐ │
│ │ INVOKE repair agent with │ │
│ │ Review Report as context │◄──────┐ │
│ └──────────┬───────────────┘ │ │
│ │ │ │
│ ▼ │ │
│ ┌──────────────────────────┐ │ │
│ │ Collect HANDOFF from │ │ │
│ │ repair agent │ │ │
│ └──────────┬───────────────┘ │ │
│ │ │ │
│ ▼ │ │
│ ┌──────────────────────────┐ │ │
│ │ INVOKE code-reviewer │ │ │
│ │ with new HANDOFF │ │ │
│ └──────────┬───────────────┘ │ │
│ │ │ │
│ ▼ │ │
│ ┌──────────────────────────┐ │ │
│ │ Recommendation = SHIP? │ │ │
│ │ YES → Exit loop ────────┼──►EXIT│ │
│ │ NO → Loop again ───────┼───┘ │ │
│ └──────────────────────────┘ │ │
│ │ │
│ Max iterations: 3 │ │
│ If max reached → Report BLOCKED │ │
└─────────────────────────────────────────────────┘

````

### Repair Loop Rules

1. **NEVER skip the repair agent.** Do NOT attempt to fix issues yourself. Do NOT summarize the issues and move on. You MUST invoke the agent.
2. **ALWAYS pass the full Review Report** as context to the repair agent using the Repair Handoff format below.
3. **ALWAYS re-invoke `code-reviewer`** after the repair agent completes. Never assume fixes are correct.
4. **Loop cap: 3 iterations.** If after 3 repair→review cycles the recommendation is still not SHIP, output the Final Report with recommendation BLOCKED and list all unresolved issues.
5. **Track iteration count.** Include `Repair Iteration: N/3` in each repair handoff.

### Repair Handoff Format

When passing review feedback back to the repair agent, use this format:

## REPAIR HANDOFF: code-reviewer → [repair-agent]

### Repair Iteration: [N]/3

### Review Recommendation: [NEEDS WORK | BLOCKED]

### Issues to Fix

[Copy the COMPLETE list of issues from the code-reviewer output. Do not summarize or omit any.]

### Severity Breakdown
- Critical: [count and list]
- Major: [count and list]
- Minor: [count and list]

### Files Requiring Changes

[List of files the reviewer flagged]

### Original Task Context

[Brief reminder of the overall task being implemented]

### Previous Handoff Context

[Include relevant context from the implementation handoff so the repair agent has full picture]

### Decision Table

| Reviewer Says                | Orchestrator Action                     | WRONG Action (NEVER DO)                                   |
|------------------------------|-----------------------------------------|-----------------------------------------------------------|
| SHIP                         | Generate Final Report                   | -                                                         |
| NEEDS WORK                   | Invoke repair agent with Repair Handoff | Fix code yourself, skip to report, ask user what to do    |
| BLOCKED                      | Invoke repair agent with Repair Handoff | Fix code yourself, skip to report, ignore and ship anyway |
| 3rd iteration still not SHIP | Generate Final Report as BLOCKED        | Keep looping, fix code yourself                           |

## Execution Pattern (INTERNAL)

### Phase 1: Sequential Agent Chain

1. **Invoke Agent**: Load the agent definition from `.claude/agents/[agent-name].md` and execute it.
2. **Collect Output**: Each Agent MUST produce a structured **HANDOFF** document.
3. **Pass Context**: Relay the handoff document to the next agent in the chain.

### Phase 2: Review Gate

4. **Invoke `code-reviewer`**: Pass the final implementation handoff.
5. **Evaluate Recommendation**: Parse the reviewer's output.
6. **Branch**:
   - If **SHIP** → Phase 3
   - If **NEEDS WORK** or **BLOCKED** → Enter Repair Loop (see above)

### Phase 3: Reporting

7. **Generate Final Report**: Aggregate all agent outputs into the consolidated report.

## Self-Check Before Each Agent Invocation

Before invoking any agent, verify:
- [ ] Am I loading the agent definition from `.claude/agents/[agent-name].md`?
- [ ] Am I passing the previous agent's HANDOFF as context?
- [ ] Am I letting the AGENT do the work (not doing it myself)?

Before generating the Final Report, verify:
- [ ] Did the last `code-reviewer` invocation return **SHIP**? (Or did we hit the 3-iteration cap?)
- [ ] If the reviewer said NEEDS WORK/BLOCKED, did I invoke the repair agent? (If not, STOP and do it now.)

## Handoff Document Format

Agents communicate via internal Handoff documents:

```markdown
## HANDOFF: [previous-agent] → [next-agent]

### Context

[Summary of work completed by the previous agent]

### Findings & Decisions

[Key discoveries, variable states, or technical decisions]

### Files Modified

[List of modified files]

### Open Questions

[Unresolved issues for the next agent]

### Recommendations

[Suggested next steps]
````

## Example: Feature Workflow Execution

```bash
/orchestrate feature "Add user profile editing"
```

1. **Dev Planner Agent**
   - Analyze requirements and create implementation plan
   - Output: `HANDOFF: dev-planner → code-implementer`
2. **Code Implementer Agent**
   - Transform plan into production-ready code
   - Output: `HANDOFF: code-implementer → code-reviewer`
3. **Code Reviewer Agent**
   - Quality, security, and performance audit
   - If SHIP → Output: Final Orchestration Report
   - If NEEDS WORK → **Invoke code-implementer** with Repair Handoff, then re-review
   - If BLOCKED → **Invoke code-implementer** with Repair Handoff, then re-review

## Example: Bugfix Workflow Execution

```bash
/orchestrate bugfix "Fix race condition in Auth module"
```

1. **Bug Analyzer Agent**
   - Deep root cause analysis & Reproduction
   - Output: `HANDOFF: bug-analyzer → tdd-guide`
2. **TDD Guide Agent**
   - Reads analysis & Writes test case to fail first
   - Implements fix
   - Output: `HANDOFF: tdd-guide → code-reviewer`
3. **Code Reviewer Agent**
   - Security & Regression check
   - If SHIP → Output: Final Orchestration Report
   - If NEEDS WORK → **Invoke tdd-guide** with Repair Handoff, then re-review
   - If BLOCKED → **Invoke tdd-guide** with Repair Handoff, then re-review

## Example: UI Design Workflow Execution

```bash
/orchestrate ui-design "Optimize the navigation sidebar for better accessibility"
```

1. **Story Generator Agent**
   - Extract user value and acceptance criteria
2. **UI Sketcher Agent**
   - Design ASCII prototype of the new sidebar
3. **Dev Planner Agent**
   - Create technical implementation plan
4. **Code Implementer Agent**
   - Implement the CSS/HTML changes
5. **Code Reviewer Agent**
   - Verify design fidelity and code quality

## Final Report Format

```markdown
# ORCHESTRATION REPORT

Workflow: [type] | Task: [description]
Agents: [Path taken, including repair loop iterations]
Review Iterations: [N] (1 = passed first time, 2+ = required repairs)

## SUMMARY

[One-paragraph executive summary of the mission]

## AGENT OUTPUTS

- Agent 1: [summary]
- Agent 2: [summary]
- Code Review #1: [NEEDS WORK - summary of issues]
- Repair #1: [summary of fixes]
- Code Review #2: [SHIP - summary]

## FILES CHANGED

[Complete list of modified files]

## TEST RESULTS

[Summary of test passes/failures and coverage]

## REVIEW HISTORY

| Iteration | Recommendation | Issues Found | Issues Fixed |
| --------- | -------------- | ------------ | ------------ |
| 1         | NEEDS WORK     | 3 critical   | -            |
| 2         | SHIP           | 0            | 3            |

## RECOMMENDATION

[SHIP / NEEDS WORK / BLOCKED]
```

## Parallel Execution

For independent checks, run agents in parallel:

```markdown
### Parallel Phase

Run simultaneously:

- code-reviewer (Quality)
- bug-analyzer (Deep Analysis)

### Merge Results

Combine outputs into a single consolidated report.
```

## Available Agents

Located in `.claude/agents/`:

- **dev-planner**: Architecture and high-level strategy planning
- **code-implementer**: Production-ready code implementation
- **bug-analyzer**: Bug investigation, root cause analysis, and code exploration
- **tdd-guide**: Test-driven implementation specialist
- **code-reviewer**: Quality, security, and performance auditor
- **story-generator**: User story generation from requirements
- **ui-sketcher**: UI/UX design and prototyping
- **security-reviewer**: OWASP-based deep security audit (used in `secure-feature` workflow)
- **database-migration**: Schema change & data migration specialist (used in `db-feature` workflow)
- **performance-optimizer**: Full-stack performance profiling and optimization (used in `performance-audit` workflow)
- **devops-engineer**: CI/CD, Docker, Kubernetes, and infrastructure setup (used in `deploy` workflow)

## Arguments

$ARGUMENTS:

- `feature <description>` - Planning → Code Implementation → Review
- `feature-tdd <description>` - Planning → TDD Implementation → Review
- `bugfix <description>` - Deep Exploration → TDD Fix → Review
- `refactor <description>` - Planning → Code Implementation → Review
- `ui-design <description>` - Story Generation → UI Prototyping → Planning → Implementation → Review
- `secure-feature <description>` - Planning → Implementation → Security Audit → Review (for auth/payment/RBAC/PII)
- `db-feature <description>` - Planning → DB Migration → Implementation → Review (for schema changes)
- `performance-audit <description>` - Profiling → Optimization Implementation → Review (for performance issues)
- `deploy <description>` - Planning → DevOps Setup → Review (for CI/CD, Docker, K8s, infrastructure)
- `custom <agents> <description>` - Custom sequence of agents (e.g. "dev-planner,code-implementer,code-reviewer")

## Tips

1. **Handoffs are mandatory**: Ensure state is passed between agents
2. **Planner first**: For multi-file changes, always start with `dev-planner`
3. **Choose the right workflow**:
   - Use `feature` for standard implementation
   - Use `feature-tdd` when test coverage is critical
   - Use `bugfix` for debugging and fixing issues
4. **Code implementer vs TDD guide**:
   - `code-implementer` for general feature development
   - `tdd-guide` for test-first development or bug fixes
5. **Bug analysis**: `bug-analyzer` provides deep execution flow analysis for complex bugs
6. **Review loops are automatic**: Do not manually intervene in the repair loop. Let the agents handle it.
