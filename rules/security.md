---
name: security
description: Mandatory security baseline for all code changes.
---

# Security Guidelines

**RULE TYPE**: Mandatory security baseline for all code changes.

## Core Security Checks

- [ ] No hardcoded secrets (keys, tokens, passwords)
- [ ] External input validation is enforced
- [ ] SQL uses parameterized queries
- [ ] XSS risk is mitigated (escape/sanitize output)
- [ ] Auth and permission checks are in place
- [ ] Sensitive details are not exposed in errors/logs
- [ ] Rate limiting or abuse controls exist on exposed endpoints

## Secret Management

- Read secrets from environment variables or secret manager only.
- Fail fast when required secrets are missing.
- Never print secrets in logs, snapshots, or test fixtures.

## Incident Response Protocol

1. Stop feature delivery for confirmed high-risk issues.
2. Patch critical vulnerabilities first.
3. Rotate leaked credentials immediately.
4. Search codebase for similar patterns and patch globally.
5. Trigger `security-reviewer` when scope includes auth/payment/PII/secrets.

## High-Risk Escalation (Mandatory)

Immediately escalate and require explicit owner decision when:

1. credential leakage is confirmed or strongly suspected
2. production data exposure risk exists
3. auth/permission boundaries can be bypassed
4. legal/compliance-sensitive data handling is uncertain

## Verification Output Contract

For security-relevant changes, delivery must explicitly list:

1. `Verified` - checks completed with evidence
2. `Not Verified` - checks not executed and why
3. `Next Mitigation` - the highest-priority follow-up action
