# Performance Optimization Rules

Guidelines for model selection and context window management.

## Model Selection Strategy

Always choose the appropriate model based on task complexity and cost efficiency.

### Claude 3.5 Haiku (Speed/Low Cost)

- **Use Cases**: Simple bug fixes (single file), unit test generation, documentation updates, code refactoring (routine/local), lint error fixing.
- **Trigger**: Tasks expected to take < 10 tool calls and involve < 3 files.

### Claude 3.5 Sonnet (Standard/High Precision)

- **Use Cases**: Majority of development tasks, complex feature implementation, orchestration between agents, multi-file refactoring, performance optimization.
- **Trigger**: Default choice for active development and feature implementation.

### Claude 3 Opus (Complex Logic/Architectural Decisions)

- **Use Cases**: New project architecture design, complex algorithm derivation, security auditing of critical components, high-level planning.
- **Trigger**: High complexity tasks where Sonnet's output needs verification or fails to solve the problem.

## Model Upgrade Policy

1. Start with the most efficient model suitable for the task.
2. If a model fails twice on the same problem, upgrade to a more capable model (e.g., Haiku → Sonnet).
3. If an agent workflow involves complex state tracking, prefer Sonnet even for individual tasks.

## Context Window Management

To prevent context overflow and performance degradation:

### 1. Minimal Working Set

- Only load files directly relevant to the current task.
- Unload files from memory once implementation/analysis is complete.

### 2. Strategic Compaction

- Summarize conversation history every 20-30 turns.
- Keep only the final state and critical decisions in the summary.
- Avoid large-scale refactoring or cross-file changes at the end of the context window (> 80% usage).

### 3. Build Issue Mitigation

- Resolve compile errors and lint issues immediately to prevent error propagation.
- If a build fails, focus 100% on the fix before proceeding with other changes.

## Usage during Orchestration

When using `/orchestrate`:

- Use **Sonnet** for the orchestrator to maintain state across agents.
- Individual agents may use **Haiku** for simple implementation steps to save tokens.

## Verification Checklist

- [ ] Is the current model appropriate for the task complexity?
- [ ] Has the context been compacted recently?
- [ ] Are redundant files removed from the working set?
- [ ] Are build status and lint warnings under control?
