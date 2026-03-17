---
argument-hint: <task-description>
description: Restate requirements, assess risks, and create step-by-step implementation plan. WAIT for user CONFIRM before touching any code.
---

# Plan Command

This command invokes the **dev-planner** agent (`.claude/agents/dev-planner.md`) to create a comprehensive implementation plan before writing any code.

1. **Restate Requirements** - Clarify what needs to be built
2. **Identify Risks** - Surface potential issues and blockers
3. **Create Step Plan** - Break down implementation into phases
4. **Wait for Confirmation** - MUST receive user approval before proceeding

## When to Use

Use `/plan` when:
- Starting a new feature
- Making significant architectural changes
- Working on complex refactoring
- Multiple files/components will be affected
- Requirements are unclear or ambiguous

## How It Works

The dev-planner agent will:

1. **Analyze the request** and restate requirements in clear terms
2. **Ask clarifying questions** if requirements are vague (using multi-turn brainstorming)
3. **Break down into phases** with specific, actionable steps
4. **Identify dependencies** between components
5. **Assess risks** and potential blockers
6. **Estimate complexity** (High/Medium/Low)
7. **Present the plan** and WAIT for your explicit confirmation

## Clarification Questions (When Needed)

If the user's request lacks detail, the agent will **proactively ask** questions like:

- What problem does this solve for users?
- What's the expected input/output?
- Are there any performance requirements? (e.g., response time, concurrent users)
- How should errors be handled?
- What existing systems does this integrate with?
- What are the acceptance criteria?

**The agent will continue asking until it has enough context to create a concrete plan.**

## Example Usage

```
User: /plan I need to add real-time notifications when markets resolve

Agent (dev-planner):
# Implementation Plan: Real-Time Market Resolution Notifications

## Requirements Restatement
- Send notifications to users when markets they're watching resolve
- Support multiple notification channels (in-app, email, webhook)
- Ensure notifications are delivered reliably
- Include market outcome and user's position result

## Implementation Phases

### Phase 1: Database Schema
1. **Add notifications table** (File: prisma/schema.prisma)
   - Action: Create table with id, user_id, market_id, type, status, created_at
   - Why: Store notification history and delivery status
   - Dependencies: None
   - Risk: Low

2. **Add user preferences table** (File: prisma/schema.prisma)
   - Action: Create user_notification_preferences with channel settings
   - Why: Allow users to control notification channels
   - Dependencies: None
   - Risk: Low

### Phase 2: Notification Service
1. **Create notification service** (File: lib/notifications.ts)
   - Action: Implement notification queue using BullMQ/Redis
   - Why: Reliable async delivery with retry logic
   - Dependencies: Redis setup
   - Risk: Medium (requires Redis infrastructure)

2. **Add notification templates** (File: lib/notifications/templates.ts)
   - Action: Create email/in-app templates
   - Why: Consistent messaging across channels
   - Dependencies: Step 2.1
   - Risk: Low

### Phase 3: Integration Points
1. **Hook into market resolution** (File: lib/markets/resolve.ts)
   - Action: Query users with positions, enqueue notifications
   - Why: Trigger notifications when market resolves
   - Dependencies: Phase 2 complete
   - Risk: Medium (performance with 1000+ users)

### Phase 4: Frontend Components
1. **Create NotificationBell component** (File: components/NotificationBell.tsx)
   - Action: Header notification icon with unread count
   - Why: User-visible notification access
   - Dependencies: None
   - Risk: Low

2. **Add real-time updates** (File: hooks/useNotifications.ts)
   - Action: Implement Supabase subscriptions
   - Why: Instant notification delivery
   - Dependencies: Step 4.1
   - Risk: Low

## Dependencies
- Redis (for queue)
- Email service (SendGrid/Resend)
- Supabase real-time subscriptions

## Risks & Mitigations
- **HIGH: Email deliverability** 
  - Mitigation: Configure SPF/DKIM, use reputable service
- **MEDIUM: Performance with 1000+ users per market**
  - Mitigation: Batch processing, rate limiting
- **MEDIUM: Notification spam**
  - Mitigation: User preferences, digest mode
- **LOW: Real-time subscription overhead**
  - Mitigation: Connection pooling, fallback to polling

## Testing Strategy
- Unit tests: notification service, template rendering
- Integration tests: end-to-end notification flow
- E2E tests: user receives notification in UI

## Success Criteria
- [ ] Users receive notifications within 5 seconds of market resolution
- [ ] Email deliverability >95%
- [ ] Users can configure notification preferences
- [ ] No duplicate notifications sent
- [ ] System handles 10,000 notifications/hour

## Estimated Complexity: MEDIUM
- Backend: 4-6 hours
- Frontend: 3-4 hours
- Testing: 2-3 hours
- Total: 9-13 hours

**WAITING FOR CONFIRMATION**: Proceed with this plan? (yes/no/modify)
```

## Important Notes

**CRITICAL**: The dev-planner agent will **NOT** write any code until you explicitly confirm the plan with "yes" or "proceed" or similar affirmative response.

If you want changes, respond with:
- "modify: [your changes]"
- "different approach: [alternative]"
- "skip phase 2 and do phase 3 first"

## Integration with Other Commands

After planning:
- Use `/tdd` to implement with test-driven development
- Use `/build-fix` if build errors occur
- Use `/review` (invokes `code-reviewer` agent) to review completed implementation

## Related Agents

This command invokes the `dev-planner` agent located at:
`.claude/agents/dev-planner.md`
