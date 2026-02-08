---
name: agent-teams
description: Autonomous workflow to analyze tasks and create Agent Teams for parallel collaboration. Auto-invoked when user requests team-based work.
---

# Agent Teams Orchestrator

## Activation

This skill is **automatically invoked** when:

- User explicitly requests: "use agent-teams to...", "create a team for...", "parallel review..."
- User describes complex multi-dimensional tasks requiring coordination

## Execution Workflow

When this skill is activated, follow this procedure:

### Step 1: Analyze Task Requirements

Evaluate the task against these criteria:

| Criterion                    | Team Needed     | Sub-agent OK  | Single Session |
| ---------------------------- | --------------- | ------------- | -------------- |
| **Parallel work**            | ✅ Yes          | ✅ Yes        | ❌ No          |
| **Inter-agent coordination** | ✅ Required     | ❌ Not needed | ❌ Not needed  |
| **Multiple perspectives**    | ✅ Yes          | ⚠️ Maybe      | ❌ No          |
| **Shared context**           | ✅ Full project | ⚠️ Partial    | ✅ Full        |

**Decision Logic**:

- If parallel + coordination needed → **Create Agent Team**
- If parallel but independent → **Use Subagents**
- If sequential or simple → **Single Session**

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

### Step 3: Execute Team Creation

**Execute this pattern directly** (do not output as text):

```text
[Brief analysis: Why team is needed]

Create an agent team to [objective].

Spawn [N] teammates:
- [role_name]: "[Goal]. Focus: [key areas]. Output: [deliverable format]."
- [role_name]: "[Goal]. Focus: [key areas]. Output: [deliverable format]."
...

Coordination:
- [How teammates will collaborate]
- [Cross-check/review requirements]
- [Consolidation method]

Wait for teammates to finish.
```

**Execution Example** (you call these, not output them):

```text
This task requires parallel security, performance, and maintainability review. Creating a code review team.

Create an agent team to review PR #142.

Spawn three reviewers:
- security_auditor: "Audit src/auth for vulnerabilities. Focus: JWT handling, SQL injection, IDOR, sensitive data. Output: Security findings with severity ratings."
- performance_engineer: "Analyze src/api queries. Focus: N+1 problems, missing indexes, inefficient algorithms. Output: Optimization recommendations."
- maintainability_expert: "Review code quality. Focus: SOLID violations, naming issues, error handling gaps. Output: Refactoring suggestions."

Coordination:
- Each reviewer works independently on their domain
- Security and performance experts cross-check each other's recommendations
- All findings consolidated into review_report.md

Wait for teammates to finish.
```

### Step 4: Monitor & Coordinate

After team creation:

1. **Assign tasks** to specific teammates using `Ask [teammate]`
2. **Broadcast** general updates to all teammates
3. **Wait** for completion before proceeding
4. **Consolidate** results into a summary document
5. **Clean up** the team when done

## Role Definition Standards

When defining roles, always include:

- **Clear goal**: What this teammate should accomplish
- **Focus areas**: Specific aspects to examine (3-5 items)
- **Output format**: How to deliver results (report, spec, diagram, etc.)

**Good Example**:

```
security_auditor: "Audit authentication flow for vulnerabilities. Focus: Token storage, session management, CSRF protection, password hashing, rate limiting. Output: Security assessment with CVSS scores."
```

**Bad Example**:

```
security_guy: "Check security stuff"
```

## Coordination Patterns

### Pattern 1: Independent → Cross-Check

```text
Have them work independently for [time], then:
- [Role A] reviews [Role B]'s work for [specific concern]
- [Role B] reviews [Role A]'s work for [specific concern]
- Consolidate into [output]
```

### Pattern 2: Competing Hypotheses

```text
Each teammate investigates a different hypothesis:
- [Hypothesis 1]: [Description]
- [Hypothesis 2]: [Description]
- [Hypothesis 3]: [Description]

Have them debate and try to disprove each other's theories.
Converge on the most likely root cause.
```

### Pattern 3: Sequential Handoff

```text
Phase 1: [Role A] produces [deliverable]
Phase 2: [Role B] uses [deliverable] to create [next deliverable]
Phase 3: [Role C] validates both and produces [final output]
```

## Task Assignment Modes

**Mode 1: Lead Assigns**
Lead explicitly assigns tasks to specific teammates using `Ask [teammate]`.
Use when tasks require specific expertise or sequencing.

**Mode 2: Self-Claiming**
Teammates automatically pick up unassigned, unblocked tasks from the shared task list.
Use when tasks are well-defined and independent.

## Optional Team Controls

**Plan Approval**: Require teammates to get approval before making changes.

- Use for high-risk modifications (database schema, auth logic, etc.)
- Example: "Spawn an architect teammate to refactor the authentication module. Require plan approval before they make any changes."

**Delegate Mode**: Allow teammates to work more autonomously with less lead oversight.

- Use when teammates have clear, independent objectives
- Reduces coordination overhead

## Communication Commands

| Command                        | When to Use                | Example                                                   |
| ------------------------------ | -------------------------- | --------------------------------------------------------- |
| `Ask [teammate]`               | Direct a specific teammate | `Ask security_auditor to verify the token rotation logic` |
| `Broadcast`                    | Message all teammates      | `Broadcast "Prioritize the payment module"`               |
| `Wait for teammates to finish` | After assigning all tasks  | Always use before consolidating results                   |
| `Clean up the team`            | Work is complete           | **Mandatory** at the end                                  |

## Critical Reminders

- **No session resume**: `/resume` doesn't restore teammates → Save results to files
- **File conflicts**: Assign different files to different teammates
- **Token cost**: Each teammate = separate session → Keep team size minimal
- **Always wait**: Don't proceed until teammates finish
- **Always cleanup**: Terminate team when done

## Quick Decision Tree

```
User requests team-based work
    ↓
Analyze: Parallel + Coordination needed?
    ↓ Yes
Select template (Review/Feature/Debug/Research)
    ↓
Execute team creation
    ↓
Monitor → Consolidate → Cleanup
```

## Example: Full Workflow

**User Input**: "Use agent-teams to design a new payment processing module with security and performance in mind."

**AI Response**:

```text
This requires parallel expertise in architecture, security, and performance. Creating a feature development team.

Create an agent team to design payment processing module.

Spawn three specialists:
- system_architect: "Design payment module architecture. Focus: API contracts, data flow, service boundaries, error handling, idempotency. Output: Architecture diagram + API spec."
- security_auditor: "Design security controls. Focus: PCI-DSS compliance, encryption at rest/transit, tokenization, audit logging, fraud detection hooks. Output: Security design doc."
- performance_engineer: "Design for scale. Focus: Transaction throughput, database indexing, caching strategy, async processing, monitoring. Output: Performance requirements doc."

Coordination:
- All work independently for 20 minutes
- Security auditor reviews architecture for vulnerabilities
- Performance engineer validates architecture for bottlenecks
- Architect consolidates all feedback into final design spec

Wait for teammates to finish.
```

---
