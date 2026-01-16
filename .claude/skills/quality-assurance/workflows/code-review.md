# Code Review Process

Systematic approach to code review ensuring quality, security, and maintainability.

## Review Phases

### Phase 1: Pre-Review Preparation
1. **Context Understanding**
   - Review PR description and linked issues
   - Understand business requirements and acceptance criteria
   - Identify affected components and dependencies

2. **Environment Setup**
   - Pull the branch locally
   - Install dependencies
   - Run existing tests to establish baseline

### Phase 2: Structural Analysis
1. **Architecture Check**
   - Design pattern consistency
   - Layer separation (presentation, business logic, data access)
   - Dependency direction (high-level modules should not depend on low-level details)

2. **Code Organization**
   - File and folder structure
   - Naming conventions
   - Module boundaries

### Phase 3: Security Review
1. **Authentication & Authorization**
   - Verify identity checks on sensitive endpoints
   - Check role-based access control implementation
   - Validate session management

2. **Input Validation**
   - SQL injection prevention (parameterized queries)
   - XSS prevention (output encoding)
   - Command injection prevention
   - File upload validation

3. **Data Protection**
   - Sensitive data handling
   - Encryption at rest and in transit
   - PII exposure prevention

### Phase 4: Performance Review
1. **Database Queries**
   - N+1 query patterns
   - Missing indexes
   - Inefficient joins
   - Missing pagination

2. **Algorithm Efficiency**
   - Time complexity analysis
   - Space complexity analysis
   - Unnecessary iterations

3. **Resource Management**
   - Connection pool leaks
   - Memory leaks
   - File handle leaks

### Phase 5: Quality Assessment
1. **Code Smells**
   - Long methods (>50 lines)
   - High cyclomatic complexity (>10)
   - Large classes (>300 lines)
   - Feature envy (class accessing another's data excessively)

2. **Test Coverage**
   - Critical path coverage
   - Edge case handling
   - Error condition tests

3. **Documentation**
   - Public API documentation
   - Complex algorithm explanations
   - Known limitations or caveats

## Severity Classification

| Level | Description | Action Required |
|-------|-------------|-----------------|
| Critical | Security vulnerability, data loss, system crash | Block merge, immediate fix |
| High | Functional bug, performance issue, maintainability | Must fix before merge |
| Medium | Code smell, suboptimal implementation | Should fix, discuss if blockers |
| Low | Style preference, minor improvement | Nice to have, optional |

## Review Checklist

### Security
- [ ] No hardcoded credentials
- [ ] Input sanitization on all external inputs
- [ ] SQL queries use parameterized statements
- [ ] Authentication verified on sensitive operations
- [ ] Authorization checks on protected resources
- [ ] Sensitive data logged with masking
- [ ] Error messages don't leak internals
- [ ] Dependencies have no known vulnerabilities

### Performance
- [ ] Database queries optimized (index usage, pagination)
- [ ] No blocking operations in main thread
- [ ] Efficient data structures used
- [ ] Caching implemented for expensive operations
- [ ] Connection pool properly configured
- [ ] Memory usage within acceptable bounds

### Maintainability
- [ ] Clear, descriptive naming
- [ ] Single responsibility per function/class
- [ ] DRY principle followed
- [ ] Comments explain "why", not "what"
- [ ] Code follows project style guide
- [ ] No commented-out code
- [ ] No TODO/FIXME without issue link

### Testing
- [ ] Tests cover critical paths
- [ ] Edge cases tested
- [ ] Error conditions tested
- [ ] No flaky tests
- [ ] Tests are isolated and repeatable

## Feedback Guidelines

### For Reviewers
- Be specific: "This loop causes O(n²) complexity" not "this is bad"
- Suggest alternatives: "Consider using a Map for O(1) lookup"
- Distinguish between style and substance
- Acknowledge good code
- Explain the impact of issues found

### For Authors
- Provide context in PR description
- Self-review before requesting review
- Respond to feedback constructively
- Ask for clarification if needed
- Link related documentation or decisions

## Tools Integration

```bash
# Static analysis
./scripts/lint-code.sh

# Security scan
./scripts/security-scan.sh

# Test coverage
./scripts/coverage-report.sh --fail-under 80
```
