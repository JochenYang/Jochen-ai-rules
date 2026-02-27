# Coding Standards

**RULE TYPE**: Global mandatory standards that ALL agents and code must follow.

These are non-negotiable requirements. Skills provide optional best practices; Rules are mandatory.

---

## Code Comments (MANDATORY)

All code must include English comments:

### Functions/Methods

```typescript
/**
 * Calculates the total price including tax and discounts
 * @param basePrice - The original price before any modifications
 * @param taxRate - Tax percentage as a decimal (e.g., 0.08 for 8%)
 * @param discountPercent - Discount percentage as a decimal
 * @returns The final calculated price
 */
function calculateTotalPrice(
  basePrice: number,
  taxRate: number,
  discountPercent: number,
): number {
  // Calculate discount amount first
  const discountAmount = basePrice * discountPercent;

  // Apply discount to base price
  const discountedPrice = basePrice - discountAmount;

  // Apply tax to the discounted price
  const taxAmount = discountedPrice * taxRate;

  return discountedPrice + taxAmount;
}
```

### Complex Logic

```typescript
// Use exponential backoff to avoid overwhelming the API during outages
// Maximum delay capped at 30 seconds to prevent excessive waiting
const delay = Math.min(1000 * Math.pow(2, retryCount), 30000);

// Binary search for efficient key lookup in sorted array
// Time complexity: O(log n) vs O(n) for linear search
```

### Key Decisions

```typescript
// Deliberately mutating a LOCAL copy here for performance with large arrays.
// Rule: NEVER mutate inputs/shared state. Local mutation on a fresh copy is allowed
// in hot paths when documented.
const updatedItems = [...items];
updatedItems.push(newItem);
```

### When NOT to Comment

```typescript
// BAD: Stating the obvious
// Increment counter by 1
count++;

// Set name to user's name
name = user.name;

// GOOD: Explain WHY, not WHAT
// Reset buffer to prevent memory leak from accumulated data
buffer = [];
```

---

## Immutability (CRITICAL)

Default rule: treat inputs as immutable. NEVER mutate function arguments or shared state.

Exception: local mutation is allowed ONLY when you are mutating a fresh local copy (not shared),
the mutation does not escape the function scope, and the reason is documented.

```typescript
// WRONG: Mutation
function updateUser(user, name) {
  user.name = name; // MUTATION!
  return user;
}

// CORRECT: Immutability
function updateUser(user, name) {
  return {
    ...user,
    name,
  };
}

// WRONG: Array mutation
items.push(newItem);

// CORRECT: Create new array
const updatedItems = [...items, newItem];

// ALSO OK (exception): mutate a fresh local copy
const updatedItems2 = [...items];
updatedItems2.push(newItem);
```

---

## Error Handling (MANDATORY)

ALWAYS handle errors comprehensively:

```typescript
// GOOD
async function fetchData(url: string) {
  try {
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Fetch failed:", error);
    throw new Error("Failed to fetch data");
  }
}
```

---

## Type Safety (MANDATORY)

NEVER use `any`:

```typescript
// BAD
function getData(id: any): any {
  return database.query(id);
}

// GOOD
interface User {
  id: string;
  name: string;
  email: string;
}

function getUser(id: string): Promise<User | null> {
  return database.users.find(id);
}
```

---

## Input Validation (MANDATORY)

ALWAYS validate user input:

```typescript
import { z } from "zod";

const schema = z.object({
  email: z.string().email(),
  age: z.number().int().min(0).max(150),
});

const validated = schema.parse(input);
```

---

## Core Engineering Principles

- **Simplicity First**: Every line of modification should have a clear and minimal necessity, avoiding over-engineering.
- **Minimal Impact**: Changes should be precisely targeted, modifying only what is necessary to minimize side effects on the existing system.
- **Demand Elegance**: For non-trivial changes, pause and ask: "Is there a more elegant way?" If a fix feels hacky, stop. Knowing everything you know now, implement the elegant solution.

---

## Autonomous Bug Fixing (CRITICAL)

When given a bug report or error:

- **Zero Hand-holding**: Locate the root cause using logs, failing tests, or stack traces and fix it directly.
- **Proof**: Provide evidence that the fix works (test results or log snippets).
- **Self-Correction**: Go fix failing CI tests and logs without being told how.

---

## File Organization

MANY SMALL FILES > FEW LARGE FILES:

- High cohesion, low coupling
- 200-400 lines typical, 800 max
- Extract utilities from large components
- Organize by feature/domain, not by type

---

## Code Quality Checklist

Before marking work complete:

- [ ] Code is readable and well-named
- [ ] Functions are small (<50 lines)
- [ ] Files are focused (<800 lines)
- [ ] No deep nesting (>4 levels)
- [ ] Proper error handling
- [ ] No console.log statements
- [ ] No hardcoded values
- [ ] No mutation of inputs/shared state (immutability enforced)
- [ ] All code has English comments
- [ ] Type safety enforced (no `any`)
- [ ] Input validation implemented

---

## Relationship to Skills

- **Rules** (this file): Mandatory standards that must be followed
- **Skills** (`.claude/skills/`): Optional best practices and patterns for reference

All agents must enforce these rules. Skills provide additional guidance but are not mandatory.
