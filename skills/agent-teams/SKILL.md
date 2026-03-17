---
name: agent-teams
description: Create agent teams for parallel collaboration. Use when user mentions team, parallel, multi-agent, coordinate, collaborate, review team, multiple perspectives, or says "agent-teams".
---

# Agent Teams Orchestrator

## Critical Rules

**Use Claude Code's NATIVE agent teams feature.** Agent teams are a first-class capability built into Claude Code — do NOT simulate them with bash subprocesses or CLI commands.

- **DO**: Directly describe the team you want to create in natural language. The platform spawns teammates natively.
- **DO NOT**: Use `bash`, `subprocess`, or `claude` CLI to create parallel agents.
- **DO NOT**: Simulate teams by running multiple shell commands.

## When to Use Agent Teams vs Subagents vs Single Session

Agent teams add coordination overhead and use significantly more tokens. Choose wisely:

| Scenario                                                      | Use                | Why                                                |
| ------------------------------------------------------------- | ------------------ | -------------------------------------------------- |
| Teammates need to **share findings and challenge each other** | **Agent Teams**    | Peer-to-peer messaging, shared task list           |
| Quick, focused workers that **report back independently**     | **Subagents**      | Lower overhead, no inter-agent coordination needed |
| Sequential tasks, same-file edits, many dependencies          | **Single Session** | No parallelism benefit                             |

**Key difference**: Subagents can only report back to the parent. Agent team teammates message each other directly, self-claim tasks, and self-coordinate.

**Decision rule**: If workers need to communicate with each other → Agent Teams. If not → Subagents or Single Session.

## How Agent Teams Work

- **Team lead**: Your main session. Coordinates work, assigns tasks, synthesizes results.
- **Teammates**: Separate Claude Code instances, each with its own context window. They can read/write files, run commands, and message other teammates and the lead.
- **Shared task list**: Central work items with dependency tracking. Tasks auto-unblock when dependencies finish. Teammates self-claim available tasks.
- **Mailbox**: Inter-agent messaging. Lead ↔ teammates, teammate ↔ teammate.

**Critical**: Teammates do NOT inherit the lead's conversation history. Whatever context they need, the lead must provide in the spawn prompt. Be generous with initial briefing.

## Execution Workflow

### Step 1: Assess the Task

Before creating a team, ask:

1. Can this be done in a single session? → Do it yourself.
2. Does it benefit from parallel work? → Continue.
3. Do workers need to communicate with each other? → Agent Teams. If not → Subagents.
4. Are the subtasks naturally independent (different files/modules)? → Good fit for teams.

**Best use cases for agent teams**:

- Multi-perspective code review (security + performance + maintainability)
- Cross-layer coordination (frontend + backend + tests, each owned by a different teammate)
- Competing hypotheses / research from different angles
- Data-parallel work (each teammate handles a segment)
- Large feature development with naturally separable components

**Poor fit**:

- Sequential tasks with strong dependencies
- Multiple teammates editing the same file (causes conflicts)
- Simple tasks a single session handles fine

### Step 2: Design the Team

**Start with research, then implement.** Agent teams work best when they begin with investigation, review, and analysis — then move to implementation if needed.

**Principles from the C compiler project**:

1. **Task decomposition is everything**: Break work into modules that can be independently developed and tested. Each teammate should own distinct files/directories.
2. **Write clear, high-quality acceptance criteria**: Agents self-orient from scratch with no prior context. Tests and clear specs keep them on track without human oversight.
3. **Minimize team size**: Each teammate = separate context window = more tokens. Use the fewest teammates that cover the work.
4. **Avoid file conflicts**: Assign different files/directories to different teammates. Never have two teammates edit the same file.
5. **Provide rich context in spawn prompts**: Include specific file paths, relevant standards, expected output format. Vague prompts produce vague results.

**Select the right team structure based on task type:**

> **IMPORTANT**: Every team MUST include a `challenge_agent`. This role is not optional — it improves quality by challenging assumptions and finding blind spots that specialists miss.

#### For Code Review / Audit

Roles (4-5 teammates):

- `security_auditor`: OWASP Top 10, injection, auth/authz, dependency vulnerabilities
- `performance_engineer`: Complexity, N+1 queries, memory, caching, bundle size
- `maintainability_expert`: SOLID, DRY, naming, error handling, test coverage
- `challenge_agent`: Dedicated skeptic — challenges assumptions, finds blind spots, questions each reviewer's conclusions (REQUIRED in every team)
- `qa_specialist` (optional): Edge cases, race conditions, error paths

Coordination: Work independently → challenge_agent questions everyone's findings → cross-check each other's findings → consolidate into single report.

#### The Challenge Agent Role

The `challenge_agent` (or `devil_advisor`) is a dedicated skeptic that improves team quality:

**Responsibilities:**
- Question assumptions made by other teammates
- Identify blind spots and edge cases others missed
- Challenge design decisions from different angles
- Act as a "red team" to stress-test conclusions

**Why it matters:**
- Specialists focus on their domain → miss cross-cutting concerns
- A dedicated skeptic catches what everyone else overlooked
- Forces explicit reasoning instead of implicit assumptions

**Example prompt:**
```
challenge_agent: "Review all findings from security_auditor, performance_engineer, and maintainability_expert. Question their conclusions: What assumptions are they making? What edge cases did they miss? What would make this code fail in production? Output: challenges.md with ranked concerns by severity."
```

#### For Feature Development

Scale roles by complexity:

**Simple (4 roles)**: Single-page, basic CRUD

- `fullstack_developer`: End-to-end implementation
- `ui_reviewer`: UX validation, interaction flows
- `challenge_agent`: Challenges design decisions, identifies edge cases and risks (REQUIRED in every team)
- `code_reviewer`: Quality, best practices, security

**Standard (5-6 roles)**: Multi-component, API integration

- `system_architect`: API contracts, data models, service boundaries
- `frontend_specialist`: Components, state management, accessibility
- `backend_specialist`: Business logic, validation, authorization
- `integration_tester`: Cross-layer verification, E2E scenarios
- `challenge_agent`: Challenges design decisions, identifies edge cases and risks (REQUIRED in every team)
- `code_reviewer`: Quality, patterns, security

**Complex (6-8 roles)**: Full-stack module, database design, deployment

- Add `database_engineer`, `devops_engineer` to Standard roles

Coordination: Architect defines contracts → Specialists implement in parallel → Testers verify → Reviewer ensures quality → Consolidate.

#### For Debugging / Investigation

Roles (3-4 teammates):

- `log_analyst`: Trace reconstruction, timeline, patterns
- `code_auditor`: Static analysis, state consistency, root cause hypotheses
- `reproduction_lead`: Minimal repro, environment simulation
- `challenge_agent`: Challenges each investigator's hypothesis, pushes for more evidence (REQUIRED in every team)

Coordination: Each investigates a different hypothesis → challenge_agent questions conclusions → debate and disprove → converge on root cause.

#### For Research / Evaluation

Roles (3-4 teammates):

- `advocate_a`: Deep dive into option A — strengths, weaknesses, real-world examples
- `advocate_b`: Deep dive into option B
- `synthesizer`: Objective comparison, scoring matrix, recommendation
- `challenge_agent`: Challenges each advocate's reasoning, questions assumptions (REQUIRED in every team)

Coordination: Advocates research independently → challenge_agent questions conclusions → synthesizer produces final analysis.

### Step 3: Create the Team

**Tell Claude what you want in natural language. Be specific about roles and scope.**

Use this pattern:

```
[Brief analysis of why a team is needed]

Create an agent team to [objective].

Spawn [N] teammates:
- [role_name]: "[Goal sentence]. Focus: [specific areas with file paths if applicable]. Output: [deliverable file/format]."
- [role_name]: "[Goal sentence]. Focus: [specific areas]. Output: [deliverable file/format]."
...

Coordination:
- [How teammates collaborate and cross-check]
- [File ownership: who writes where]
- [How results are consolidated]

Wait for teammates to finish.
```

**Role definition quality matters:**

Good:

```
security_auditor: "Audit src/auth/ for security vulnerabilities. Focus: JWT token storage in src/auth/token.ts, session management in src/auth/session.ts, CSRF protection, password hashing, rate limiting. Output: security_review.md with findings sorted by CVSS severity."
```

Bad:

```
security_guy: "Check security stuff"
```

### Step 4: Coordinate the Team

As lead agent, manage using:

| Action            | How                            | When                                   |
| ----------------- | ------------------------------ | -------------------------------------- |
| Direct a teammate | `Ask [teammate]`               | Assign specific work or ask for status |
| Message all       | `Broadcast`                    | Share updates affecting everyone       |
| Wait              | `Wait for teammates to finish` | Before consolidating results — always  |
| Clean up          | `Clean up the team`            | When done — mandatory, no exceptions   |

**Assignment modes**:

- **Lead assigns**: Explicitly assign tasks with `Ask [teammate]`. Use for sequenced or specialized work.
- **Self-claiming**: Teammates auto-pick unblocked tasks from the shared list. Use for independent, well-defined tasks.

**Optional controls**:

- **Plan approval**: Require teammates to get approval before making changes. Use for high-risk modifications (database schema, auth logic).
- **Delegate mode**: Teammates work more autonomously with less lead oversight. Use when objectives are clear and independent.

### Step 5: Consolidate & Clean Up

After all teammates finish:

1. **Collect** all deliverables from output files
2. **Cross-reference** findings between teammates — look for conflicts, gaps, and duplicates
3. **Synthesize** into a unified summary
4. **Report** to the user with key findings and recommendations
5. **Clean up the team** — MANDATORY

## Lessons from the C Compiler Project

These patterns come from Anthropic's experiment where 16 agents built a 100,000-line C compiler:

1. **When tasks are naturally independent, parallelization is trivial**: Each agent picks a different failing test or module to work on. The shared task list handles coordination.

2. **Giant monolithic tasks cause agents to get stuck**: Unlike hundreds of independent tests, a single massive task can't be parallelized. Break big deliverables into smaller, testable chunks.

3. **Tests are the primary coordination mechanism**: With high-quality tests, agents stay on track without human oversight. New commits can't break existing code if CI enforces it.

4. **Agents have no prior context on each session**: Each agent starts fresh. Write clear README/CLAUDE.md files so agents can self-orient quickly. Include file paths, architecture notes, and conventions.

5. **Agents waste time without constraints**: Without guardrails, agents will spend hours running tests or exploring tangents. Provide fast feedback loops (quick test samples, clear progress indicators).

6. **File-based coordination works**: Agents "lock" tasks by writing files. Git merge conflicts serve as tiebreakers. Save all results to files since session state doesn't persist.

## Hooks for Agent Teams

Use hooks to enforce rules automatically:

- **TeammateIdle**: Runs when a teammate is about to go idle. Exit with code 2 to send feedback and keep them working.
- **TaskCompleted**: Runs when a task is being marked complete. Exit with code 2 to prevent completion and send feedback (e.g., run additional validation).

## Critical Reminders

- **No session resume**: `/resume` doesn't restore teammates → Always save results to files
- **File conflicts**: Assign different files to different teammates — this is the biggest pitfall
- **Token cost**: Each teammate = separate context window → Keep team size minimal
- **Context**: Teammates don't inherit lead's conversation history → Provide full context in spawn prompts
- **Always wait**: Don't consolidate until all teammates finish
- **Always clean up**: Terminate the team when done — no exceptions

## Full Example

**User**: "Use agent-teams to review the authentication module for security, performance, and code quality."

**Response**:

This task benefits from parallel specialized review — three independent perspectives on the same code, with cross-checking. Creating a review team.

Create an agent team to review the authentication module.

Spawn three reviewers:

- security_auditor: "Audit src/auth/ for security vulnerabilities. Focus: JWT handling in src/auth/token.ts, password hashing in src/auth/crypto.ts, session management in src/auth/session.ts, CSRF protection, rate limiting. Output: Write findings with severity ratings to reviews/security_review.md."
- performance_engineer: "Analyze src/auth/ for performance issues. Focus: N+1 queries in src/auth/queries.ts, token validation overhead, caching opportunities, connection pooling in src/auth/db.ts. Output: Write optimization recommendations to reviews/performance_review.md."
- maintainability_expert: "Review src/auth/ for code quality issues. Focus: SOLID violations, error handling gaps, naming consistency, test coverage in tests/auth/. Output: Write refactoring suggestions to reviews/maintainability_review.md."

Coordination:

- Each reviewer works independently on their domain — no file conflicts since all write to separate output files
- Security auditor cross-checks performance recommendations for security implications
- Performance engineer validates security suggestions won't create bottlenecks
- All findings consolidated into reviews/auth_review_summary.md

Wait for teammates to finish.

## Troubleshooting

### Issue: Teammates not responding
Cause: Context window limit or message delivery delay
Solution:
- Verify teammate is still running (check task status)
- Resend message with more explicit instructions
- If stuck, terminate and respawn the teammate

### Issue: File conflicts between teammates
Cause: Multiple teammates assigned to same files
Solution:
- Immediately stop the team
- Redistribute file ownership so each file has exactly one owner
- Resume with clear ownership boundaries

### Issue: Teammate produces generic/low-quality output
Cause: Vague role definition in spawn prompt
Solution:
- Be specific about: file paths, focus areas, output format, quality bar
- Example: "Write security findings to reviews/sec.md with CVSS severity ratings"

### Issue: Team never finishes (infinite loop)
Cause: Unclear completion criteria or circular dependencies
Solution:
- Define explicit exit conditions in coordination section
- Set maximum task count or time limit
- If stuck, manually intervene with "Please summarize your progress and stop"

### Issue: Results not consolidating properly
Cause: Teammates wrote to wrong files or formats differ
Solution:
- Always specify exact output file paths and format in role definitions
- Lead agent should create consolidation template before spawning team
- Review intermediate outputs before final consolidation
