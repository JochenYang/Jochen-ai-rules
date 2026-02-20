# Testing Strategy

Comprehensive testing approach ensuring code quality and reliability.

## Test Pyramid

```
        /\
       /  \      E2E Tests (Few, Slow, High Confidence)
      /    \
     /      \    Integration Tests (Medium, Medium Confidence)
    /________\
   /          \  Unit Tests (Many, Fast, Low Confidence)
  /____________\
```

## Unit Testing

### Principles
- **Isolation**: Each test runs independently
- **Single Concern**: Test one behavior per test
- **Fast**: Complete in milliseconds
- **Deterministic**: Same result every run
- **Self-Contained**: No external dependencies

### Naming Convention
```javascript
describe('UserService', () => {
  it('should create user with valid email', () => {})
  it('should throw error for invalid email', () => {})
  it('should return user by id', () => {})
})
```

### Structure (AAA Pattern)
```javascript
it('should calculate total correctly', () => {
  // Arrange
  const items = [{ price: 10 }, { price: 20 }];
  const tax = 0.1;

  // Act
  const total = calculateTotal(items, tax);

  // Assert
  expect(total).toBe(33);
});
```

### What to Test
- Public API contracts
- Edge cases (empty, null, undefined)
- Error conditions
- Boundary conditions
- Expected vs. actual behavior

### What NOT to Test
- Implementation details (private methods)
- Third-party code
- Trivial getters/setters
- Code that changes frequently without behavior change

## Integration Testing

### Scope
- Database interactions
- API endpoint behavior
- Service interactions
- External service mocks

### Setup Pattern
```javascript
beforeAll(async () => {
  await setupTestDatabase();
  await seedTestData();
});

afterAll(async () => {
  await cleanupTestDatabase();
});
```

### Database Testing
- Use test database instance
- Clean state before each test
- Test transactions and rollbacks
- Verify index effectiveness

### API Testing
```javascript
describe('POST /api/users', () => {
  it('should create user and return 201', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ email: 'test@example.com' });

    expect(response.status).toBe(201);
    expect(response.body.email).toBe('test@example.com');
  });
});
```

## End-to-End Testing

### User Flow Coverage
- Critical user journeys
- Authentication flows
- Payment/checkout processes
- Complex multi-step operations

### Best Practices
```javascript
test('user can complete checkout', async ({ page }) => {
  // Use test IDs for reliability
  await page.goto('/products');
  await page.click('[data-testid="add-to-cart"]');
  await page.click('[data-testid="checkout"]');

  // Verify final state
  await expect(page.locator('[data-testid="order-success"]'))
    .toBeVisible();
});
```

### Avoid
- Testing internal state
- Over-specifying selectors
- Hard-coded waits (use waiting strategies)
- Testing trivial flows

## Test Coverage Standards

| Coverage Type | Minimum | Recommended |
|--------------|---------|-------------|
| Line Coverage | 80% | 90% |
| Branch Coverage | 70% | 85% |
| Function Coverage | 80% | 90% |
| Critical Path | 100% | 100% |

## Mock Strategies

### Unit Test Mocks
- Mock external services
- Mock time-dependent behavior
- Mock file system
- Mock network calls

### Integration Test Mocks
- Mock external APIs
- Mock message queues
- Mock authentication services

### E2E Test Mocks
- Minimal mocking
- Test against real integrations when possible
- Use test accounts for external services

## Test Data Management

### Factories
```javascript
const createUser = (overrides = {}) => ({
  email: faker.internet.email(),
  name: faker.person.fullName(),
  ...overrides
});
```

### Fixtures
```javascript
beforeEach(async () => {
  await fixture.load('users.json');
});
```

### Strategies
- **Fresh Database**: Each test run starts clean
- **Transaction Rollback**: Wrap tests in transaction
- **Data Cleanup**: Explicit teardown after each test

## Performance Testing

### Load Testing
- Simulate expected user load
- Measure response times
- Identify bottlenecks

### Stress Testing
- Push beyond normal capacity
- Identify breaking points
- Test recovery behavior

### Endurance Testing
- Extended duration tests
- Memory leak detection
- Resource consumption patterns

## Test Execution

```bash
# Run all tests
./scripts/run-tests.sh --coverage

# Run specific type
./scripts/run-tests.sh --unit
./scripts/run-tests.sh --integration
./scripts/run-tests.sh --e2e

# Run with coverage threshold
./scripts/run-tests.sh --coverage --fail-under 80
```

## Continuous Integration

### Pre-Merge Checks
- All unit tests pass
- Integration tests pass
- Coverage threshold met
- No new security vulnerabilities

### Quality Gates
- Coverage decrease: Block
- New critical bugs: Block
- Test flakiness: Investigate
