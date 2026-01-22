# Coding Standards

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
  discountPercent: number
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

### Key Code
```typescript
// Deliberately using mutation here for performance with large arrays
// Spread operator would create copy overhead on each iteration
items.push(newItem);
```

### When NOT to Comment
```typescript
// BAD: Stating the obvious
// Increment counter by 1
count++

// Set name to user's name
name = user.name

// GOOD: Explain WHY, not WHAT
// Reset buffer to prevent memory leak from accumulated data
buffer = [];
```

## Immutability (CRITICAL)

ALWAYS create new objects, NEVER mutate:

```typescript
// WRONG: Mutation
function updateUser(user, name) {
  user.name = name  // MUTATION!
  return user
}

// CORRECT: Immutability
function updateUser(user, name) {
  return {
    ...user,
    name
  }
}

// WRONG: Array mutation
items.push(newItem)

// CORRECT: Create new array
const updatedItems = [...items, newItem]
```

## Error Handling

ALWAYS handle errors comprehensively:

```typescript
// GOOD
async function fetchData(url: string) {
  try {
    const response = await fetch(url)

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    return await response.json()
  } catch (error) {
    console.error('Fetch failed:', error)
    throw new Error('Failed to fetch data')
  }
}
```

## Type Safety

NEVER use `any`:

```typescript
// BAD
function getData(id: any): any {
  return database.query(id)
}

// GOOD
interface User {
  id: string
  name: string
  email: string
}

function getUser(id: string): Promise<User | null> {
  return database.users.find(id)
}
```
