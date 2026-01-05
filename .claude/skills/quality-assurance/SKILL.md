---
name: quality-assurance
description: Comprehensive code quality assurance covering code review, testing strategies, and security auditing. Identifies bugs, vulnerabilities, performance issues, and maintainability problems. Implements unit/integration/E2E testing and provides actionable recommendations following OWASP and industry best practices.
license: MIT
compatibility: Works with any codebase and testing framework. Can integrate with linters, security scanners (npm audit, Snyk, OWASP ZAP), and testing tools (Jest, Vitest, Playwright, Cypress, pytest).
metadata:
  author: "jochen-ai"
  version: "1.0.0"
  category: "quality-assurance"
  tags: ["code-review", "testing", "security", "quality", "audit", "e2e", "unit-test"]
allowed-tools: Read Write Bash
---

# Quality Assurance Engineer

Comprehensive quality assurance covering code review, testing, and security auditing. Ensures code quality, test coverage, and security compliance across all development phases.

## Core Capabilities

### Code Review
- **Code Quality**: Identifies code smells, anti-patterns, and maintainability issues
- **Performance**: Detects performance bottlenecks and inefficient algorithms
- **Best Practices**: Ensures adherence to language-specific conventions and patterns
- **Architecture**: Reviews design decisions and suggests improvements
- **Prioritization**: Provides severity levels (Critical/High/Medium/Low) for issues

### Testing Strategy
- **Unit Testing**: Component-level testing with high coverage (>80%)
- **Integration Testing**: API and service integration validation
- **E2E Testing**: User flow automation with Playwright/Cypress
- **Test Design**: TDD workflows, mock strategies, fixture management
- **Coverage Analysis**: Identifies untested code paths and edge cases

### Security Auditing
- **OWASP Top 10**: Authentication, authorization, injection, XSS, CSRF
- **Input Validation**: SQL injection, command injection, path traversal prevention
- **Data Protection**: Encryption, secure storage, sensitive data handling
- **Dependency Security**: Vulnerability scanning (npm audit, Snyk)
- **Configuration**: Security headers, CORS, CSP, rate limiting

## Tech Stack

### Testing Frameworks
| Language   | Unit Testing        | E2E Testing          | Mocking          |
|------------|---------------------|----------------------|------------------|
| JavaScript | Jest, Vitest, Mocha | Playwright, Cypress  | Sinon, Jest      |
| TypeScript | Jest, Vitest        | Playwright, Cypress  | Jest, ts-mockito |
| Python     | pytest, unittest    | Selenium, Playwright | unittest.mock    |
| Java       | JUnit, TestNG       | Selenium             | Mockito          |
| Go         | testing, testify    | Selenium             | gomock           |

### Security Tools
- **SAST**: ESLint security plugins, Bandit (Python), SonarQube
- **DAST**: OWASP ZAP, Burp Suite
- **Dependency Scanning**: npm audit, Snyk, Dependabot
- **Secret Detection**: GitGuardian, TruffleHog

## Code Review Checklist

### Critical Issues (Must Fix)
- [ ] Security vulnerabilities (SQL injection, XSS, authentication bypass)
- [ ] Memory leaks or resource leaks
- [ ] Race conditions or deadlocks
- [ ] Data loss or corruption risks
- [ ] Unhandled exceptions that crash the application

### High Priority
- [ ] Performance bottlenecks (N+1 queries, inefficient algorithms)
- [ ] Missing input validation
- [ ] Improper error handling
- [ ] Missing tests for critical paths
- [ ] Hardcoded credentials or sensitive data

### Medium Priority
- [ ] Code duplication (DRY violations)
- [ ] Complex functions (>50 lines, >3 nesting levels)
- [ ] Missing documentation for complex logic
- [ ] Inconsistent naming conventions
- [ ] Magic numbers or strings

### Low Priority
- [ ] Code style inconsistencies
- [ ] Minor refactoring opportunities
- [ ] Optional optimizations
- [ ] Documentation improvements

## Testing Best Practices

### Unit Testing
```javascript
// Good: Test one thing, clear naming, arrange-act-assert
describe('UserService', () => {
  it('should create user with valid email', async () => {
    // Arrange
    const userData = { email: 'test@example.com', name: 'Test' };
    
    // Act
    const user = await userService.create(userData);
    
    // Assert
    expect(user.email).toBe(userData.email);
    expect(user.id).toBeDefined();
  });
  
  it('should throw error for invalid email', async () => {
    // Arrange
    const userData = { email: 'invalid', name: 'Test' };
    
    // Act & Assert
    await expect(userService.create(userData))
      .rejects.toThrow('Invalid email format');
  });
});
```

### E2E Testing
```javascript
// Good: Test user flows, use page objects, handle async properly
test('user can complete checkout flow', async ({ page }) => {
  // Navigate and login
  await page.goto('/products');
  await page.click('[data-testid="add-to-cart"]');
  
  // Verify cart
  await expect(page.locator('[data-testid="cart-count"]')).toHaveText('1');
  
  // Complete checkout
  await page.click('[data-testid="checkout"]');
  await page.fill('[name="email"]', 'test@example.com');
  await page.click('[data-testid="submit-order"]');
  
  // Verify success
  await expect(page.locator('[data-testid="order-confirmation"]'))
    .toBeVisible();
});
```

## Security Audit Checklist

### Authentication & Authorization
- [ ] Passwords hashed with bcrypt/argon2 (not MD5/SHA1)
- [ ] JWT tokens properly validated and expired
- [ ] Session management secure (httpOnly, secure, sameSite cookies)
- [ ] Multi-factor authentication for sensitive operations
- [ ] Role-based access control (RBAC) properly implemented

### Input Validation
- [ ] All user inputs validated and sanitized
- [ ] SQL queries use parameterized statements
- [ ] File uploads validated (type, size, content)
- [ ] API rate limiting implemented
- [ ] CORS configured properly

### Data Protection
- [ ] Sensitive data encrypted at rest and in transit
- [ ] No credentials in code or logs
- [ ] PII handled according to regulations (GDPR, CCPA)
- [ ] Secure random number generation for tokens
- [ ] Database backups encrypted

### Configuration
- [ ] Security headers set (CSP, X-Frame-Options, HSTS)
- [ ] Error messages don't leak sensitive information
- [ ] Debug mode disabled in production
- [ ] Dependencies up to date with security patches
- [ ] Secrets managed via environment variables or vault

## Execution Workflow

### Phase 1: Code Review
1. Analyze code structure and architecture
2. Identify security vulnerabilities and performance issues
3. Check adherence to best practices and conventions
4. Provide prioritized recommendations with severity levels

### Phase 2: Test Strategy
1. Assess current test coverage and identify gaps
2. Design test cases for critical paths and edge cases
3. Implement unit, integration, and E2E tests
4. Verify test coverage meets quality standards (>80%)

### Phase 3: Security Audit
1. Review authentication and authorization mechanisms
2. Check input validation and sanitization
3. Scan dependencies for known vulnerabilities
4. Verify secure configuration and data protection
5. Provide actionable remediation steps

## Quality Standards

- Test coverage > 80% for critical paths
- Zero critical security vulnerabilities
- Code review findings addressed before merge
- All tests passing in CI/CD pipeline
- Performance benchmarks met

## Boundaries

Focus on code quality, testing, and security. Not responsible for product requirements, UI/UX design, or infrastructure architecture.

## Helper Scripts

**Always run `--help` first** to see usage.

- `scripts/run-tests.sh` - Run all tests with coverage report
- `scripts/security-scan.sh` - Run security vulnerability scan
- `scripts/lint-code.sh` - Run linters and static analysis
- `scripts/coverage-report.sh` - Generate detailed coverage report

## Detailed References

- `./workflows/code-review.md` - Code review process and checklist
- `./workflows/testing-strategy.md` - Test design and implementation guide
- `./workflows/security-audit.md` - Security audit methodology
- `./references/owasp-top-10.md` - OWASP Top 10 vulnerabilities guide
- `./references/testing-patterns.md` - Common testing patterns and anti-patterns

## Official Resources

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Testing Best Practices: https://testingjavascript.com/
- Security Guidelines: https://cheatsheetseries.owasp.org/
