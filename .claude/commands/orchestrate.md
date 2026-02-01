# Orchestrate Command

Multi-agent sequential collaboration workflow command.

## Usage

`/orchestrate [workflow-type] [task-description]`

## Workflow Types

### feature

Full feature implementation workflow:

```
dev-planner → tdd-guide → code-reviewer
```

### bugfix

Bug investigation and resolution workflow:

```
bug-analyzer → tdd-guide → code-reviewer
```

### refactor

Safe refactoring workflow:

```
code-reviewer → tdd-guide
```

## Execution Pattern

For each agent in the workflow:

1. **Invoke Agent** - Pass context from the previous agent.
2. **Collect Output** - Generate a structured Handoff document.
3. **Pass to Next** - Relay information through the chain.
4. **Consolidate** - Generate the final orchestration report.

## Handoff Document Format

Agents communicate via Handoff documents:

```markdown
## HANDOFF: [previous-agent] → [next-agent]

### Context

[Summary of work completed by the previous agent]

### Findings

[Key discoveries or technical decisions]

### Files Modified

[List of modified files]

### Open Questions

[Unresolved issues for the next agent]

### Recommendations

[Suggested next steps]
```

## Example: Feature Workflow

```bash
/orchestrate feature "Add user authentication feature"
```

Execution Steps:

1. **Dev Planner Agent**
   - Requirements analysis
   - Implementation planning
   - Dependency identification
   - Output: `HANDOFF: dev-planner → tdd-guide`

2. **TDD Guide Agent**
   - Read planner handoff
   - Write tests first
   - Implement code to pass tests
   - Output: `HANDOFF: tdd-guide → code-reviewer`

3. **Code Reviewer Agent**
   - Review implementation
   - Check for issues
   - Suggest improvements
   - Output: Final Report

## Final Report Format

```
ORCHESTRATION REPORT
====================
Workflow: feature
Task: Add user authentication feature
Agents: dev-planner → tdd-guide → code-reviewer

SUMMARY
-------
[One-paragraph executive summary]

AGENT OUTPUTS
-------------
Dev Planner: [Summary]
TDD Guide: [Summary]
Code Reviewer: [Summary]

FILES CHANGED
-------------
[Complete list of modified files]

TEST RESULTS
------------
[Summary of test passes/failures]

RECOMMENDATION
--------------
[SHIP / NEEDS WORK / BLOCKED]
```

## Parallel Execution

For independent checks, run agents in parallel:

```markdown
### Parallel Phase

Run simultaneously:

- code-reviewer (Quality)
- bug-analyzer (Error Detection)

### Merge Results

Combine outputs into a single report.
```

## Arguments

$ARGUMENTS:

- `feature <description>` - Full feature development workflow
- `bugfix <description>` - Bug resolution workflow
- `refactor <description>` - Code refactoring workflow
- `custom <agents> <description>` - Custom sequence of agents

## Custom Workflow Example

```bash
/orchestrate custom "dev-planner,tdd-guide,code-reviewer" "Redesign cache layer"
```

## Tips

1. **Start with Planner** - Use dev-planner for complex features.
2. **Always Review** - code-reviewer is mandatory before merging.
3. **Keep Handoffs Concise** - Focus on what the next agent needs to know.
4. **Verify Mid-Flow** - Insert verification steps between agents if needed.
