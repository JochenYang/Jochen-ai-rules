---
name: agent-teams
description: Create agent teams for parallel collaboration. Triggers on keywords like team, parallel, multi-agent, coordinate, collaborate, review team, multiple perspectives, agent-teams.
---

# Agent Teams Orchestrator

## Critical Rules

**YOU MUST use Claude Code's native agent teams feature to create teammates.**

- **DO**: Directly spawn teammates as described in this skill
- **DO NOT**: Use `bash` or `subprocess` to create parallel agents
- **DO NOT**: Simulate teams by running multiple shell commands
- **DO NOT**: Use `claude` CLI commands in bash to fake parallelism

The agent teams feature is a NATIVE capability of Claude Code. You spawn teammates by directly stating your intent to create them in your response. The platform handles the rest.

## Activation

This skill is **automatically invoked** when:

- User explicitly requests: "use agent-teams to...", "create a team for...", "parallel review..."
- User describes complex multi-dimensional tasks requiring coordination

## Execution Workflow

### Step 1: Analyze Task Requirements

| Criterion                    | Agent Team      | Single Session |
| ---------------------------- | --------------- | -------------- |
| **Parallel work needed**     | ✅ Yes          | ❌ No          |
| **Multiple perspectives**    | ✅ Yes          | ❌ No          |
| **Inter-agent coordination** | ✅ Required     | ❌ Not needed  |
| **Shared context**           | ✅ Full project | ✅ Full        |

**Decision Logic**:

- Parallel + coordination needed → **Create Agent Team**
- Sequential or simple → **Single Session** (do NOT create a team)

### Step 2: Design Team Structure

**Important: Start with Research**

Agent teams work best when they start with:

- Research and investigation
- Review and analysis
- Evaluation and comparison

**Then** move to implementation if needed. Avoid jumping straight to coding in parallel.

Based on task type, select appropriate template as a starting point (adapt to your specific context):

#### Template A: Code Review

**Trigger**: "review", "audit", "check security/performance"

**Roles**:

- `security_auditor`: OWASP Top 10, injection, auth/authz, dependencies
- `performance_engineer`: Complexity, queries, memory, bundle size
- `maintainability_expert`: SOLID, DRY, naming, error handling
- `qa_specialist`: Test coverage, edge cases, race conditions

#### Template B: Feature Development (Complexity-Based)

**Trigger**: "build", "implement", "develop feature"

**Selection Criteria**:

- **Simple** (3-4 roles): Single-page feature, CRUD operations, simple UI
- **Standard** (6 roles): Multi-component feature, API integration, moderate complexity
- **Complex** (8 roles): Full-stack module, database design, deployment requirements

---

**B1: Simple Feature (3-4 roles)**

Use when: Single page, basic CRUD, simple UI components

- `fullstack_developer`: End-to-end implementation (frontend + backend + basic tests)
- `ui_reviewer`: UI/UX validation, interaction flows, visual consistency
- `code_reviewer`: Code quality, best practices, basic security

**Coordination**: Developer implements → UI reviewer validates → Code reviewer ensures quality

---

**B2: Standard Feature (6 roles)**

Use when: Multi-component feature, API integration, cross-layer work

- `system_architect`: API contracts, data models, service boundaries, error propagation
- `frontend_specialist`: Components, state management, responsive layout, accessibility
- `backend_specialist`: Business logic, data validation, transactions, authorization
- `ui_quality_reviewer`: UI/UX validation, interaction flows, visual consistency, usability testing
- `integration_tester`: Cross-layer integration, API contracts, data flow validation, E2E scenarios
- `code_reviewer`: Code quality, best practices, security basics, performance patterns

**Coordination**: Architect defines contracts → Frontend/Backend implement → UI reviewer validates UX → Integration tester verifies end-to-end → Code reviewer ensures quality → Consolidate findings

---

**B3: Complex Feature (8 roles)**

Use when: Full-stack module, database design, deployment, high complexity

- `system_architect`: API contracts, data models, service boundaries, error propagation
- `database_engineer`: Schema design, indexing strategy, migration scripts, query optimization
- `frontend_specialist`: Components, state management, responsive layout, accessibility
- `backend_specialist`: Business logic, data validation, transactions, authorization
- `ui_quality_reviewer`: UI/UX validation, interaction flows, visual consistency, usability testing
- `integration_tester`: Cross-layer integration, API contracts, data flow validation, E2E scenarios
- `code_reviewer`: Code quality, best practices, security basics, performance patterns
- `devops_engineer`: Docker configuration, CI/CD pipeline, monitoring setup, deployment strategy

**Coordination**: Architect + DB engineer define foundation → Frontend/Backend implement → UI reviewer validates UX → Integration tester verifies end-to-end → Code reviewer ensures quality → DevOps prepares deployment → Consolidate all findings

#### Template C: Debugging

**Trigger**: "investigate bug", "find root cause", "why is X failing"

**Roles**:

- `log_analyst`: Trace reconstruction, timeline, patterns
- `code_auditor`: Static analysis, state consistency
- `reproduction_lead`: Minimal repro, environment simulation

#### Template D: Research

**Trigger**: "compare solutions", "evaluate options", "which is better"

**Roles**:

- `solution_a_advocate`: Deep dive into option A
- `solution_b_advocate`: Deep dive into option B
- `decision_synthesizer`: Objective comparison, scoring

### Step 3: Spawn the Team

**You are the lead agent.** To create the team, directly state in your response what teammates to spawn, their roles, goals, and how they coordinate. The Claude Code platform will interpret this and create the teammates natively.

**Required format — use this EXACTLY:**

Create an agent team to [objective].

Spawn [N] teammates:

[role_name]: "[Goal sentence]. Focus: [key areas]. Output: [deliverable format]."
[role_name]: "[Goal sentence]. Focus: [key areas]. Output: [deliverable format]."
...
Coordination:

[How teammates collaborate]
[Cross-check requirements]
[Consolidation method]
Wait for teammates to finish.

**Each role definition MUST include:**

- **Clear goal**: One sentence on what to accomplish
- **Focus areas**: 3-5 specific aspects to examine
- **Output format**: How to deliver results (report, spec, code file, etc.)

**Good role definition**:  
security_auditor: "Audit authentication flow for vulnerabilities. Focus: Token storage, session management, CSRF protection, password hashing, rate limiting. Output: Security assessment with CVSS scores in security_report.md."

**Bad role definition**:  
security*guy: "Check security stuff"*

### Step 4: Coordinate the Team

As lead agent, you manage the team using these native commands:

| Command                        | When to Use                   | Example                                                   |
| ------------------------------ | ----------------------------- | --------------------------------------------------------- |
| `Ask [teammate]`               | Direct a specific teammate    | `Ask security_auditor to verify the token rotation logic` |
| `Broadcast`                    | Message all teammates at once | `Broadcast "Prioritize the payment module"`               |
| `Wait for teammates to finish` | After assigning all tasks     | Always use before consolidating results                   |
| `Clean up the team`            | Work is complete              | **Mandatory** at the end of every team session            |

**Task Assignment Modes:**

- **Lead Assigns**: You explicitly assign tasks to specific teammates using `Ask [teammate]`. Use for tasks requiring specific expertise or sequencing.
- **Self-Claiming**: Teammates automatically pick up unassigned, unblocked tasks. Use when tasks are well-defined and independent.

**Optional Controls:**

- **Plan Approval**: Require teammates to get your approval before making changes. Use for high-risk modifications (database schema, auth logic, etc.).
- **Delegate Mode**: Allow teammates to work more autonomously. Use when teammates have clear, independent objectives.

### Step 5: Consolidate & Cleanup

After all teammates finish:

1. **Collect** all results and deliverables
2. **Cross-reference** findings between teammates for conflicts or gaps
3. **Synthesize** into a unified summary document
4. **Report** to the user with key findings and recommendations
5. **Clean up the team** — this is MANDATORY

## Coordination Patterns

### Pattern 1: Independent → Cross-Check

Have them work independently, then:

[Role A] reviews [Role B]'s work for [specific concern]
[Role B] reviews [Role A]'s work for [specific concern]
Consolidate into [output file]

### Pattern 2: Competing Hypotheses

Each teammate investigates a different hypothesis:

Have them debate and try to disprove each other's theories.
Converge on the most likely root cause.

### Pattern 3: Sequential Handoff

Phase 1: [Role A] produces [deliverable]
Phase 2: [Role B] uses [deliverable] to create [next deliverable]
Phase 3: [Role C] validates both and produces [final output]

## Critical Reminders

- **NEVER use bash subprocesses** — always use native agent teams
- **No session resume**: `/resume` doesn't restore teammates → Save all results to files
- **File conflicts**: Assign different files to different teammates — never have two teammates edit the same file
- **Token cost**: Each teammate = separate context window → Keep team size minimal (prefer fewer, more capable roles)
- **Always wait**: Don't proceed until all teammates finish
- **Always cleanup**: Terminate the team when done — no exceptions
- **Save state to files**: Teammates should write their outputs to files so results survive session end

## Quick Decision Tree

User requests team-based work
↓
Can this be done in a single session? → Yes → Do it yourself, no team needed
↓ No
Analyze: How many parallel perspectives needed?
↓
Select template (Review / Feature / Debug / Research)
↓
Determine complexity → Choose role count (3-8)
↓
Spawn team using native agent teams (NOT bash)
↓
Coordinate → Wait → Consolidate → Cleanup

## Full Example

**User Input**: "Use agent-teams to review the authentication module for security and performance issues."

**Expected AI Response**:

This requires parallel expertise in security and performance analysis. I'll create a review team.

Create an agent team to review the authentication module.

Spawn three reviewers:

- security_auditor: "Audit src/auth/ for security vulnerabilities. Focus: JWT handling, password hashing, session management, CSRF protection, rate limiting. Output: Security findings with severity ratings in security_review.md."
- performance_engineer: "Analyze src/auth/ for performance issues. Focus: N+1 queries, missing indexes, token validation overhead, caching opportunities, connection pooling. Output: Performance recommendations in performance_review.md."
- maintainability_expert: "Review src/auth/ for code quality. Focus: SOLID violations, error handling gaps, naming consistency, test coverage, documentation. Output: Refactoring suggestions in maintainability_review.md."

Coordination:

- Each reviewer works independently on their domain
- Security auditor cross-checks performance recommendations for security implications
- Performance engineer validates security suggestions won't create bottlenecks
- All findings consolidated into auth_review_summary.md

Wait for teammates to finish.
