# Common Testing Patterns and Anti-Patterns

Best practices and common pitfalls in automated testing.

## Testing Patterns

### Pattern 1: Builder Pattern for Test Data
```javascript
// Builder for complex test objects
class UserBuilder {
  constructor() {
    this.user = {
      email: 'test@example.com',
      name: 'Test User',
      role: 'user',
      preferences: {}
    };
  }

  withEmail(email) {
    this.user.email = email;
    return this;
  }

  withName(name) {
    this.user.name = name;
    return this;
  }

  asAdmin() {
    this.user.role = 'admin';
    return this;
  }

  withPreferences(prefs) {
    this.user.preferences = prefs;
    return this;
  }

  build() {
    return this.user;
  }
}

// Usage
const adminUser = new UserBuilder()
  .withEmail('admin@example.com')
  .asAdmin()
  .build();
```

### Pattern 2: Shared Test Setup
```javascript
// test-support/setup.js
let testDatabase;
let testRedis;

beforeAll(async () => {
  testDatabase = await setupTestDatabase();
  testRedis = await setupTestRedis();
});

afterAll(async () => {
  await testDatabase.cleanup();
  await testRedis.cleanup();
});

// test/user.service.test.js
describe('UserService', () => {
  beforeEach(async () => {
    await testDatabase.clear();
  });

  it('should create user', async () => {
    const user = await UserService.create({
      email: 'test@example.com'
    });
    expect(user.id).toBeDefined();
  });
});
```

### Pattern 3: Parameterized Tests
```javascript
// Reduce duplication with parameterized tests
const testCases = [
  { input: 'test@example.com', valid: true },
  { input: 'invalid-email', valid: false },
  { input: '@example.com', valid: false },
  { input: 'test@', valid: false }
];

testCases.forEach(({ input, valid }) => {
  it(`should validate ${input} as ${valid}`, () => {
    const result = validateEmail(input);
    expect(result).toBe(valid);
  });
});
```

### Pattern 4: Snapshot Testing
```javascript
// Component snapshot testing
import renderer from 'react-test-renderer';

it('renders correctly', () => {
  const tree = renderer
    .create(<Button variant="primary">Click me</Button>)
    .toJSON();
  expect(tree).toMatchSnapshot();
});
```

### Pattern 5: Mocking External Services
```javascript
// Mock HTTP responses
jest.mock('axios');
import axios from 'axios';

it('fetches user data', async () => {
  axios.get.mockResolvedValue({
    data: { id: 1, name: 'Test User' }
  });

  const user = await UserService.fetchUser(1);
  expect(user.name).toBe('Test User');
});
```

### Pattern 6: Contract Testing
```javascript
// Provider
describe('User API', () => {
  it('should return user schema', () => {
    const user = generateUser();
    expect(user).toMatchSchema(userSchema);
  });
});

// Consumer
it('can consume user data', () => {
  const user = api.getUser(1);
  expect(user.id).toBeNumber();
  expect(user.email).toMatchEmail();
});
```

## Testing Anti-Patterns

### Anti-Pattern 1: Testing Implementation Details
```javascript
// Bad: Testing internal state
it('should increment counter internally', () => {
  const counter = new Counter();
  counter.increment();
  expect(counter._count).toBe(1); // Fragile!
});

// Good: Testing behavior
it('should return incremented value', () => {
  const counter = new Counter();
  expect(counter.getValue()).toBe(0);
  expect(counter.getValue()).toBe(1);
});
```

### Anti-Pattern 2: Over-Mocking
```javascript
// Bad: Mocking everything
it('should save user', async () => {
  const mockDb = { save: jest.fn().mockResolvedValue({ id: 1 }) };
  const mockLogger = { info: jest.fn() };
  const mockCache = { set: jest.fn() };

  const service = new UserService(mockDb, mockLogger, mockCache);
  await service.save({ name: 'Test' });

  expect(mockDb.save).toHaveBeenCalled();
});
```

**Solution**: Test at integration level for complex flows, mock only external boundaries.

### Anti-Pattern 3: Flaky Tests
```javascript
// Bad: Time-dependent
it('should timeout after 5 seconds', async () => {
  const start = Date.now();
  await waitForTimeout(5000);
  expect(Date.now() - start).toBeGreaterThanOrEqual(5000);
});

// Better: Use fake timers
it('should timeout after 5 seconds', async () => {
  jest.useFakeTimers();
  const callback = jest.fn();

  setTimeout(callback, 5000);
  jest.advanceTimersByTime(5000);
  expect(callback).toHaveBeenCalled();
});
```

### Anti-Pattern 4: Interdependent Tests
```javascript
// Bad: Tests depend on execution order
let counter = 0;

it('first test sets counter', () => {
  counter = 5;
});

it('second test uses counter', () => {
  expect(counter).toBe(5); // Fragile!
});

// Good: Each test is independent
it('should handle increment', () => {
  const counter = new Counter();
  counter.increment();
  expect(counter.getValue()).toBe(1);
});
```

### Anti-Pattern 5: Assertion Roulette
```javascript
// Bad: Multiple unrelated assertions
it('should create user', async () => {
  const user = await createUser();

  expect(user.id).toBeDefined();
  expect(user.createdAt).toBeInstanceOf(Date);
  expect(user.email).toBe('test@example.com');
  expect(user.name).toBe('Test');
  expect(user.role).toBe('user');
  expect(user.password).not.toBe('plaintext'); // Separate test?
});

// Good: One expectation per test, or group related assertions
it('should create user with correct email', async () => {
  const user = await createUser({ email: 'test@example.com' });
  expect(user.email).toBe('test@example.com');
});
```

### Anti-Pattern 6: Brittle Selectors
```javascript
// Bad: Fragile selectors
await page.click('body > div > div:nth-child(2) > button');
await page.click('.btn.btn-primary.my-5');

// Good: Test IDs
await page.click('[data-testid="submit-button"]');
await page.click('[data-testid="add-to-cart"]');
```

## Test Organization

### File Structure
```
tests/
├── unit/
│   ├── user/
│   │   ├── user.model.test.js
│   │   └── user.service.test.js
│   └── setup.js
├── integration/
│   ├── api/
│   │   └── user.api.test.js
│   └── database/
│       └── user.repository.test.js
├── e2e/
│   ├── specs/
│   │   ├── login.spec.js
│   │   └── checkout.spec.js
│   └── pages/
│       ├── LoginPage.js
│       └── CheckoutPage.js
├── fixtures/
│   ├── users.json
│   └── products.json
└── support/
    ├── setup.js
    └── hooks.js
```

### Naming Conventions
- `*.test.js` - Unit tests
- `*.integration.test.js` - Integration tests
- `*.spec.js` - E2E tests (Playwright/Cypress)
- `*.fixture.js` - Test data factories
- `*.helper.js` - Test utilities

## Performance Optimization

### Parallel Execution
```javascript
// jest.config.js
module.exports = {
  maxWorkers: '50%',
  testPathIgnorePatterns: ['/node_modules/', '/e2e/']
};
```

### Test Isolation
```javascript
// Use --runInBand for CI stability
// jest --runInBand
```

### Selective Testing
```bash
# Run only changed tests
jest --changedSince=main

# Run specific test file
jest user.service.test.js

# Run tests matching pattern
jest --testNamePattern="should create"
```
