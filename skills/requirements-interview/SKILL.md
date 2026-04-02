---
name: requirements-interview
description: Conduct deep multi-round requirements interviews to produce executable SPEC, PRD, and PLAN drafts. Use when user says "clarify requirements", "采访需求", "extract requirements", "define scope", "analyze needs", or when requirements are ambiguous and need interactive clarification. Do NOT use when requirements are already complete.
---

# Requirements Interview

Run structured, multi-round requirement interviews, then convert answers into actionable documents.

## When to Use

Use this skill when:
- Requirements are incomplete, ambiguous, or contradictory.
- The user asks to "clarify requirements" through Q&A.
- You need interview-driven outputs (SPEC/PRD/PLAN), not only a static PRD.

Do not use this skill when:
- The user already provided clear and complete requirements.
- The user only needs a standard PRD summary (use `product-manager`).

## Inputs

- Existing `SPEC.md` (optional)
- Existing `PRD.md` (optional)
- Existing `PLAN.md` (optional)

## Tool Strategy

Primary: AskUserQuestionTool (or equivalent interactive question tool).

Fallback: If the tool is unavailable, continue with plain conversational questions and keep the same interview structure.

## Core Rules

1. Ask deep, non-trivial questions (avoid obvious yes/no prompts).
2. Minimum 2 rounds of clarification unless user explicitly stops.
3. After each round, update assumptions and unresolved items.
4. Separate confirmed facts from hypotheses.
5. Do not skip final document outputs.

## Interview Dimensions (Mandatory)

Cover these areas:
- Business goals and success metrics
- Target users and key scenarios
- Scope boundaries and explicit non-goals
- UX expectations and acceptance criteria
- Technical constraints and integration boundaries
- Security/compliance/performance requirements
- Risks, tradeoffs, and alternatives
- Milestones, priority, and delivery sequence

## Workflow

1. Read existing `SPEC.md`/`PRD.md`/`PLAN.md` if they exist.
2. Summarize known facts and gaps.
3. Run interview round 1 with focused open questions.
4. Update SPEC/PRD/PLAN drafts.
5. Run interview round 2+ until requirements are actionable.
6. Produce final deliverables and a concise uncertainty log.

## Outputs

Always provide or update:
- `SPEC.md`: problem definition, scope, constraints, acceptance checks
- `PRD.md`: user value, requirements, priorities, success metrics
- `PLAN.md`: implementation phases, dependencies, risks, test strategy

## Completion Criteria

- Requirements are implementation-ready.
- Key assumptions and tradeoffs are explicit.
- Acceptance criteria are testable.
- Open questions are listed with owner and next action.

## Handoff Guidance

If implementation is next:
- handoff to `dev-planner` for execution planning, or
- handoff to `product-manager` for roadmap-level prioritization.

## Examples

### Example 1: Ambiguous Feature Request
User says: "I want to add user authentication"
Actions:
1. Ask about auth method (OAuth, password-based, SSO?)
2. Clarify user roles and permissions
3. Determine session management preferences
4. Define password reset and recovery flows
Result: Complete auth SPEC.md with acceptance criteria

### Example 2: New Project Startup
User says: "Help me define requirements for a CRM system"
Actions:
1. Identify target users (sales, support, management?)
2. Define core workflows (contact management, deals, tasks)
3. Clarify integrations (email, calendar, phone)
4. Establish success metrics
Result: Full PRD.md with prioritized features

### Example 3: Scope Refinement
User says: "The current feature is too complex, simplify it"
Actions:
1. List current scope items
2. Identify which are must-have vs nice-to-have
3. Propose simplified scope with clear non-goals
4. Update SPEC.md boundaries
Result: Streamlined specification with explicit exclusions

## Boundaries

- Focus on clarification, scope shaping, and document drafting.
- Do not jump into implementation or technical solutioning before the requirements are stable enough.
- Do not assume missing business rules when they materially affect scope or priority.

## Escalation Rules

Pause and ask the owner before:

- collapsing unresolved requirement conflicts into a single assumed answer
- converting an interview workflow into a final PRD or PLAN without enough confirmation
- reframing the product scope in ways that materially change delivery expectations

## Final Output Contract (MANDATORY)

Every use of this skill should end with:

1. `Skill Fit` - why interview-driven clarification was required
2. `Primary Deliverable` - clarified requirements, draft docs, or open-question set
3. `Execution Evidence` - questions asked, answers gathered, and source artifacts considered
4. `Risks / Open Questions` - unresolved ambiguity, conflicting answers, or dependency gaps
5. `Next Action` - the clearest next clarification or planning step
