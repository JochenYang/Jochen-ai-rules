# Requirement Gathering Workflow

This guide provides detailed patterns for using the AskUserQuestion tool to gather complete skill requirements through multi-turn conversations.

## Quick Example: Complete Interaction Flow

Here's a real example of how to go from vague to concrete:

```markdown
Q1: "What main functionality should the image-editor skill provide?"
A1: "Image editing"

Q2: "Can you be more specific? For example: cropping, rotating, filters, red-eye removal, or something else?"
A2: "Mainly rotating and cropping"

Q3: "Great! Can you give a concrete example? Like 'I have a photo.jpg that's sideways, rotate it 90 degrees clockwise'?"
A3: "Yes, exactly that. Also 'crop this image to remove the top 100 pixels'"

Q4: "Perfect! Should this skill also handle batch operations (multiple images at once) or just single images?"
A4: "Just single images for now"

✅ READY: Clear functionality (rotate + crop), concrete examples, scope defined
```

## Core Principle

**Never assume - always clarify.** Skills are most effective when built on concrete, validated requirements. Use AskUserQuestion to transform vague ideas into actionable specifications.

## Question Framework

### Phase 1: Core Understanding (Questions 1-3)

**Goal**: Understand what the skill does and when it triggers

```markdown
Q1: "What is the main purpose of this skill? What problem does it solve?"
Q2: "Can you give 2-3 concrete examples of how you'd use this skill?"
Q3: "What phrases or requests should trigger this skill?"
```

### Phase 2: Scope Definition (Questions 4-6)

**Goal**: Define boundaries and identify edge cases

```markdown
Q4: "What should this skill NOT handle? Any related tasks to exclude?"
Q5: "Should this skill support [common variation X]? What about [edge case Y]?"
Q6: "Are there any specific constraints? (file formats, size limits, performance requirements)"
```

### Phase 3: Resource Identification (Questions 7-9)

**Goal**: Identify scripts, references, and assets needed

```markdown
Q7: "Do you have existing documentation, templates, or code to include?"
Q8: "Are there specific tools, libraries, or APIs this skill should use?"
Q9: "What output format or quality standards should this skill follow?"
```

## Question Patterns by Skill Type

### For Workflow Skills (multi-step processes)

```markdown
Q: "Can you walk me through the workflow step-by-step?"
Q: "At step [X], what decisions need to be made? What are the options?"
Q: "What happens if [error condition Y] occurs during step [X]?"
Q: "What's the expected input and output for each step?"
```

### For Tool Integration Skills (APIs, file formats)

```markdown
Q: "Which specific API endpoints or file operations will be used most?"
Q: "Do you have API documentation or schema definitions to include?"
Q: "What authentication or configuration is needed?"
Q: "What are common error scenarios and how should they be handled?"
```

### For Domain Knowledge Skills (company-specific, specialized)

```markdown
Q: "What domain-specific terminology or concepts should be documented?"
Q: "Are there existing policies, guidelines, or standards to reference?"
Q: "Who are the typical users and what's their expertise level?"
Q: "What are the most common questions or tasks in this domain?"
```

## Multi-Turn Conversation Strategies

### Strategy 1: Funnel (Broad → Specific)

Start with open questions, then narrow down:

```markdown
Turn 1: "What should this skill do?" → "Data analysis"
Turn 2: "What type of data?" → "Sales data from BigQuery"
Turn 3: "What specific analyses?" → "Revenue trends, top products, regional performance"
Turn 4: "What output format?" → "Markdown reports with charts"
```

### Strategy 2: Example-Driven

Use examples to validate understanding:

```markdown
Turn 1: "Can you give an example?" → [User provides vague example]
Turn 2: "Let me make that more concrete: [specific example]. Is this what you mean?" → "Yes, exactly!"
Turn 3: "Here's another scenario: [edge case]. Should the skill handle this?" → "No, out of scope"
```

### Strategy 3: Iterative Refinement

Build on previous answers:

```markdown
Turn 1: "What functionality?" → "PDF editing"
Turn 2: "You mentioned editing - do you mean: text extraction, form filling, annotation, or something else?" → "Form filling"
Turn 3: "For form filling, should the skill: auto-detect fields, use a template, or require manual mapping?" → "Auto-detect"
Turn 4: "Got it! Should it handle: checkboxes, dropdowns, signatures, or just text fields?" → "All of them"
```

## When to Stop Asking

Stop when you can confidently answer these questions:

1. ✅ **What**: What does the skill do? (1-2 sentence description)
2. ✅ **When**: When should it trigger? (specific phrases or contexts)
3. ✅ **How**: What's the workflow? (step-by-step process)
4. ✅ **Resources**: What scripts/references/assets are needed? (concrete list)
5. ✅ **Boundaries**: What's in scope vs out of scope? (clear boundaries)

## Anti-Patterns to Avoid

❌ **Asking too many questions at once**
```markdown
Bad: "What functionality? What triggers? What resources? What constraints? What output?"
Good: "What's the main functionality this skill should provide?"
```

❌ **Accepting vague answers**
```markdown
User: "I want a data analysis skill"
Bad: "Got it, I'll create a data analysis skill"
Good: "What type of data will you analyze? Can you give a specific example?"
```

❌ **Assuming without validating**
```markdown
Bad: "I assume you want SQL support, right?"
Good: "What data source will this skill work with? SQL databases, CSV files, APIs, or something else?"
```

❌ **Stopping too early**
```markdown
Bad: After 2 questions → "I have enough information"
Good: After 5-8 questions → "Let me summarize what I understand: [detailed summary]. Does this match your vision?"
```

## Example: Complete Requirement Gathering Session

**Skill**: PDF Form Filler

```markdown
Q1: "What's the main purpose of this skill?"
A1: "Fill out PDF forms automatically"

Q2: "Can you give a concrete example? Like 'I have a tax form and a JSON file with my info, fill it out'?"
A2: "Yes! Exactly that. I have multiple forms and want to fill them with data from JSON"

Q3: "Should the skill auto-detect form fields or use a predefined mapping?"
A3: "Auto-detect would be ideal"

Q4: "What types of fields should it handle? Text, checkboxes, dropdowns, signatures?"
A4: "Text and checkboxes for now. Dropdowns would be nice but not critical"

Q5: "Should it validate the data before filling (like checking date formats)?"
A5: "Yes, that would be helpful"

Q6: "Do you have example PDFs and JSON files I can use as references?"
A6: "Yes, I'll provide them"

Q7: "What should happen if a field in the JSON doesn't match any form field?"
A7: "Log a warning but continue filling other fields"

Q8: "Should the output be a new PDF or overwrite the original?"
A8: "New PDF with '_filled' suffix"

✅ READY TO PROCEED: Clear understanding of functionality, scope, and resources needed
```

## Summary

Use AskUserQuestion to:
- Transform vague ideas into concrete specifications
- Validate assumptions with examples
- Identify edge cases and boundaries
- Discover required resources
- Build confidence before implementation

Continue asking until you can write a detailed skill plan without guessing.
