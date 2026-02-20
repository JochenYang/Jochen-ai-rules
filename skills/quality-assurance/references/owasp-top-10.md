# OWASP Top 10 Vulnerabilities Guide

Comprehensive reference for OWASP Top 10 2021 security risks.

## A01:2021 - Broken Access Control

### Description
Access control enforces policy such that users cannot act outside of their intended permissions.

### Common Vulnerabilities
- Bypass access control checks by modifying URL, API, or HTML page
- View or modify data belonging to other users
- Access API with missing access controls
- Elevation of privilege

### Prevention
```javascript
// Good: Verify ownership
async function getUserDocument(userId, documentId) {
  const document = await Document.findById(documentId);
  if (document.ownerId !== userId) {
    throw new AuthorizationError('Access denied');
  }
  return document;
}

// Good: Use middleware for route protection
app.get('/api/admin/users',
  requireAuth,
  requireRole('admin'),
  (req, res) => { /* ... */ }
);
```

### Testing
```bash
# Test for IDOR
curl -u user:pass https://api.example.com/users/12345
# Modify user ID to 12346 - should fail
```

## A02:2021 - Cryptographic Failures

### Description
Previously known as Sensitive Data Exposure. Focuses on failures related to cryptography.

### Common Vulnerabilities
- Transmitting data in clear text
- Using deprecated algorithms
- Using weak keys
- Missing security headers

### Prevention
```javascript
// Good: Use secure protocols
const https = require('https');
const server = https.createServer({
  key: fs.readFileSync('private.key'),
  cert: fs.readFileSync('certificate.crt')
});

// Good: Hash passwords with bcrypt
const bcrypt = require('bcrypt');
const hash = await bcrypt.hash(password, 12);

// Good: Set secure headers
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"]
  }
}));
```

## A03:2021 - Injection

### Description
User input is interpreted as code by an interpreter.

### Types
- SQL Injection
- NoSQL Injection
- OS Command Injection
- LDAP Injection
- XPath Injection

### SQL Injection Prevention
```javascript
// Bad: String concatenation
const query = "SELECT * FROM users WHERE id = " + userId;

// Good: Parameterized queries
const query = 'SELECT * FROM users WHERE id = ?';
const results = db.execute(query, [userId]);

// Good: ORM usage
const user = User.findOne({ where: { id: userId } });
```

### XSS Prevention
```javascript
// Bad: InnerHTML without sanitization
element.innerHTML = userInput;

// Good: Output encoding
element.textContent = userInput;

// Good: React handles encoding automatically
<div>{userInput}</div>

// Good: Use DOMPurify for HTML
import DOMPurify from 'dompurify';
const clean = DOMPurify.sanitize(userInput);
```

## A04:2021 - Insecure Design

### Description
Security requirements and design patterns missing or ineffective.

### Common Issues
- Missing rate limiting
- Missing file size limits
- Predictable recovery codes
- No resource quotas

### Prevention
```javascript
// Good: Rate limiting
const rateLimit = require('express-rate-limit');
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use(limiter);

// Good: File size limits
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ limit: '10mb' }));
```

## A05:2021 - Security Misconfiguration

### Description
Incorrectly configured security settings, default configurations, or verbose error messages.

### Common Issues
- Unnecessary features enabled
- Default credentials not changed
- Verbose error messages
- Missing security headers

### Prevention
```javascript
// Good: Security headers
const securityHeaders = {
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'Content-Security-Policy': "default-src 'self'"
};

// Good: Disable verbose errors in production
if (process.env.NODE_ENV === 'production') {
  app.use((err, req, res, next) => {
    res.status(500).json({ error: 'Internal server error' });
  });
}
```

## A06:2021 - Vulnerable and Outdated Components

### Description
Using components with known vulnerabilities or not keeping them updated.

### Prevention
```bash
# Regular dependency audits
npm audit
# or
pip-audit

# Use Dependabot for auto-updates
# In .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule: "weekly"
```

## A07:2021 - Identification and Authentication Failures

### Description
Compromised credentials, keys, or session tokens.

### Prevention
```javascript
// Good: Strong password policy
const passwordValidator = require('password-validator');
const schema = new passwordValidator()
  .is().min(12)
  .is().max(100)
  .has().uppercase()
  .has().lowercase()
  .has().digits(2)
  .has().symbols(2)
  .has().not().spaces();

// Good: Secure session configuration
app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true,
    httpOnly: true,
    sameSite: 'strict',
    maxAge: 24 * 60 * 60 * 1000 // 24 hours
  }
}));
```

## A08:2021 - Software and Data Integrity Failures

### Description
Software updates, critical data, and CI/CD pipeline without integrity verification.

### Prevention
```javascript
// Good: Verify integrity of updates
const crypto = require('crypto');
const fs = require('fs');

function verifySignature(file, signature, publicKey) {
  const verifier = crypto.createVerify('SHA256');
  verifier.update(fs.readFileSync(file));
  return verifier.verify(publicKey, signature);
}
```

## A09:2021 - Security Logging and Monitoring Failures

### Description
Insufficient logging, monitoring, and response to incidents.

### Prevention
```javascript
// Good: Structured logging
const logger = require('./logger');

app.use((req, res, next) => {
  logger.info({
    method: req.method,
    path: req.path,
    ip: req.ip,
    userId: req.user?.id
  });
  next();
});

// Good: Log authentication attempts
app.post('/login', async (req, res) => {
  const { email, password } = req.body;
  const success = await authenticate(email, password);

  if (!success) {
    logger.warn({
      event: 'login_failed',
      email,
      ip: req.ip,
      timestamp: new Date().toISOString()
    });
  }
});
```

## A10:2021 - Server-Side Request Forgery (SSRF)

### Description
Fetching internal resources without validation.

### Prevention
```javascript
// Good: Validate and sanitize URLs
const URL = require('url').URL;

function validateUrl(inputUrl) {
  const parsed = new URL(inputUrl);
  if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
    throw new Error('Only HTTP/HTTPS allowed');
  }
  if (['127.0.0.1', '::1', '169.254.169.254'].includes(parsed.hostname)) {
    throw new Error('Internal addresses not allowed');
  }
  return parsed.href;
}
```

## References

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- OWASP Cheat Sheet Series: https://cheatsheetseries.owasp.org/
- OWASP Testing Guide: https://owasp.org/www-project-web-security-testing-guide/
