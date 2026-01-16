# Security Audit Methodology

Systematic security assessment following OWASP guidelines and industry best practices.

## Audit Scope

### In Scope
- Application source code
- Configuration files
- Dependency libraries
- API endpoints
- Authentication/authorization flows
- Data handling and storage
- Third-party integrations

### Out of Scope
- Infrastructure (handled by DevOps)
- Physical security
- Social engineering
- Zero-day vulnerabilities in dependencies

## Audit Phases

### Phase 1: Reconnaissance
1. **Application Mapping**
   - Identify all entry points
   - Map attack surface
   - Document technology stack
   - List third-party dependencies

2. **Configuration Review**
   - Security headers
   - CORS policies
   - Rate limiting
   - Error handling

### Phase 2: Authentication Review
1. **Password Storage**
   - Verify bcrypt/argon2 usage
   - Check salt implementation
   - Validate password policy

2. **Session Management**
   - Token expiration
   - Secure cookie flags
   - Session fixation protection
   - Concurrent session handling

3. **Multi-Factor Authentication**
   - Implementation verification
   - Backup code handling
   - Recovery flow security

### Phase 3: Authorization Review
1. **Access Control**
   - Role-based access control (RBAC)
   - Permission inheritance
   - Horizontal privilege escalation
   - Vertical privilege escalation

2. **API Security**
   - Endpoint authorization
   - IDOR protection
   - Direct object reference

### Phase 4: Input Validation Review
1. **Injection Attacks**
   - SQL injection
   - Command injection
   - LDAP injection
   - NoSQL injection

2. **Cross-Site Scripting (XSS)**
   - Stored XSS
   - Reflected XSS
   - DOM-based XSS

3. **File Upload Security**
   - Type validation
   - Size limits
   - Content verification
   - Storage location

### Phase 5: Data Protection Review
1. **Sensitive Data**
   - PII identification
   - Encryption at rest
   - Encryption in transit
   - Data retention

2. **Logging & Monitoring**
   - Sensitive data in logs
   - Audit trail completeness
   - Alert configuration

### Phase 6: Dependency Audit
1. **Vulnerability Scanning**
   - npm audit / pip-audit
   - Snyk / Dependabot
   - CVE database check

2. **License Compliance**
   - License compatibility
   - Attribution requirements

## OWASP Top 10 Checklist

### A01:2021 - Broken Access Control
- [ ] Authorization enforced server-side
- [ ] No predictable resource IDs
- [ ] Role checks on every request
- [ ] CORS properly configured
- [ ] No path traversal vulnerabilities

### A02:2021 - Cryptographic Failures
- [ ] Strong encryption algorithms (AES-256, RSA-2048+)
- [ ] No deprecated ciphers
- [ ] HTTPS enforced
- [ ] Secure key management
- [ ] No hardcoded secrets

### A03:2021 - Injection
- [ ] Parameterized queries
- [ ] Input sanitization
- [ ] Output encoding
- [ ] Safe file handling
- [ ] No eval() with user input

### A04:2021 - Insecure Design
- [ ] Rate limiting implemented
- [ ] File size limits
- [ ] Resource quotas
- [ ] Business logic validation

### A05:2021 - Security Misconfiguration
- [ ] Security headers set
- [ ] Debug mode disabled
- [ ] Default credentials changed
- [ ] Unnecessary services disabled
- [ ] Error messages sanitized

### A06:2021 - Vulnerable Components
- [ ] Dependencies updated
- [ ] No known CVEs
- [ ] Unused dependencies removed
- [ ] Component versions documented

### A07:2021 - Identification and Authentication
- [ ] Strong password policy
- [ ] Secure session management
- [ ] MFA available
- [ ] Account lockout implemented
- [ ] Password reset secure

### A08:2021 - Software and Data Integrity
- [ ] Code signing verified
- ] Integrity checks on updates
- [ ] Secure deserialization
- [ ] CI/CD pipeline secured

### A09:2021 - Security Logging and Monitoring
- [ ] Authentication logging
- [ ] Error logging
- [ ] Audit trail
- [ ] Alerting configured

### A10:2021 - Server-Side Request Forgery (SSRF)
- [ ] URL validation
- [ ] DNS rebinding protection
- [ ] Internal network access blocked
- [ ] Allowlist for external requests

## Audit Report Format

### Executive Summary
- Scope and methodology
- Risk rating summary
- Key findings overview
- Recommendations summary

### Detailed Findings
- Vulnerability description
- Impact assessment
- Likelihood rating
- Severity rating
- Evidence (screenshots, logs)
- Remediation steps
- References

### Appendices
- Test cases
- Tools used
- Raw data
- Glossary

## Remediation Tracking

| Finding | Severity | Status | Owner | Due Date |
|---------|----------|--------|-------|----------|
| SQL Injection in Search | Critical | In Progress | @developer | 2024-01-20 |
| Missing Rate Limiting | High | Pending | @developer | 2024-01-25 |

## Tools

```bash
# Dependency scan
./scripts/security-scan.sh --dependencies

# Secrets detection
./scripts/security-scan.sh --secrets

# Static analysis
./scripts/security-scan.sh --sast

# Full audit
./scripts/security-scan.sh --full
```
