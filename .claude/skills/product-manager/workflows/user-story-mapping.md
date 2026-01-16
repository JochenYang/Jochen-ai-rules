# User Story Mapping Workshop Guide

Facilitation guide for running user story mapping sessions.

## Pre-Workshop Preparation

### Invitation
Invite cross-functional team members:
- Product Manager (facilitator)
- Designer(s)
- Developer(s)
- QA Engineer
- Customer Success (optional)
- Subject matter expert

### Materials
- Whiteboard or digital collaboration tool (Miro, FigJam)
- Sticky notes (virtual or physical)
- Timer
- User research data

## Workshop Structure

### Phase 1: User Activities (30 min)

**Objective**: Identify high-level user activities

**Process**:
1. Ask: "What do users do with our product?"
2. Write activities on sticky notes
3. Group similar activities
4. Arrange horizontally by user workflow

**Example Output**:
```
┌─────────────────────────────────────────────────────────┐
│  Activities                                            │
├──────────┬──────────┬──────────┬──────────┬──────────┤
│ Discover │ Evaluate │ Purchase │ Use      │ Support  │
│ Products │ Products │          │ Products │          │
└──────────┴──────────┴──────────┴──────────┴──────────┘
```

### Phase 2: User Tasks (45 min)

**Objective**: Break activities into specific tasks

**Process**:
1. For each activity, ask: "What specific tasks does the user do?"
2. Write tasks on sticky notes below activities
3. Group similar tasks
4. Order by frequency or importance

**Example Output**:
```
Discover Products
├── Browse categories
├── Search products
├── Filter results
├── View product details
└── Read reviews
```

### Phase 3: Stories (60 min)

**Objective**: Create detailed user stories

**Process**:
1. For each task, ask: "What specific story can we implement?"
2. Write stories on smallest sticky notes
3. Group stories into releases (slices)

**Format**:
```
As a [user type]
I want to [action]
So that [benefit]
```

**Example**:
```
As a shopper
I want to filter products by price range
So that I can find items within my budget
```

### Phase 4: Prioritization (30 min)

**Objective**: Order stories for implementation

**Process**:
1. Use affinity estimation or planning poker
2. Mark MVP stories (must have for v1)
3. Mark nice-to-have stories
4. Create release roadmap

### Phase 5: Review & Summary (15 min)

**Objective**: Document and share outcomes

**Process**:
1. Take photo/screenshot
2. Document key decisions
3. Assign follow-up items
4. Schedule next steps

## Facilitation Tips

### Managing Discussion
- Keep the energy high, set time limits
- Encourage equal participation
- CaptureParking Lot items for later
- Make decisions visible

### Handling Disagreements
- Acknowledge all viewpoints
- Use data to resolve conflicts
- Default to "try it and learn"
- Document dissent

### Common Pitfalls
- Going too deep too early
- Including too many people
- Not enforcing time limits
- Forgetting non-happy paths

## Output

### Story Map Artifact
```
                    Releases
                    v1      v2      v3
Activities    ┌─────────────────────────────┐
Discover      │■ ■ ■      │  ■ ■    │  ■   │
Evaluate      │■ ■        │  ■ ■    │  ■   │
Purchase      │■ ■ ■ ■    │  ■      │      │
Use           │■          │  ■ ■ ■  │  ■ ■ │
Support       │           │  ■      │  ■   │
              └─────────────────────────────┘

■ = User story (sized by effort)
```

### Action Items
| Item | Owner | Due Date |
|------|-------|----------|
| [Action] | [Name] | [Date] |

## Post-Workshop

### Follow-up Tasks
- Refine story details
- Estimate effort
- Create backlog tickets
- Schedule sprint planning
