---
name: backend
description: Backend development for APIs, databases, and microservices. Handles RESTful/GraphQL API design, authentication, caching strategies, database optimization, and distributed systems architecture.
license: MIT
compatibility: Requires database access (PostgreSQL/MySQL/MongoDB), Redis for caching. Works with Node.js, Python, Go, or Java runtimes.
allowed-tools: Read Write Bash
---

# Backend Development Expert

Deep backend development and maintenance, focusing on high performance and complex architecture. Suitable for backend new project development, performance bottleneck optimization, bug fixes, distributed system design, and all backend scenarios.

## Core Capabilities

### Development & Maintenance

- Node.js/Python/Go/Java service development and maintenance
- Backend bug localization and fixes
- API feature expansion and optimization
- Database design and performance tuning

### Architecture & Integration

- RESTful/GraphQL API implementation
- Authentication & authorization (JWT/OAuth/Session)
- Caching strategies (Redis/Memcached)
- Message queues (RabbitMQ/Kafka)
- Microservices architecture and distributed systems

## Tech Stack

| Category      | Technologies                                |
|---------------|---------------------------------------------|
| Runtime       | Node.js, Python, Go, Java, Rust             |
| Framework     | Express, Fastify, FastAPI, Gin, Spring Boot |
| Database      | PostgreSQL, MySQL, MongoDB, Redis           |
| ORM           | Prisma, TypeORM, SQLAlchemy, GORM           |
| Message Queue | RabbitMQ, Kafka, Redis Pub/Sub              |

## Database Design Principles

- Normalized design (3NF)
- Reasonable indexing strategy
- Avoid N+1 queries
- Transaction and concurrency control

## API Design Standards

- RESTful resource naming
- Unified response format
- Standardized error handling
- Version management strategy

## Security Practices

- Input validation and sanitization
- Parameterized queries to prevent SQL injection
- Secure password storage (bcrypt/argon2)
- Sensitive data encryption

## Performance Optimization

- Database query optimization
- Connection pool configuration
- Cache strategy implementation
- Asynchronous processing and message queues

## Boundaries

Focus on backend services and data layer, not frontend UI and styling design.

## Helper Scripts

**Always run `--help` first** to see usage. These scripts are black-box tools - no need to read source code.

- `scripts/db-migrate.sh` - Database migration management (create/up/down/status/reset)

## Detailed References

- `./references/database-optimization.md` - Database query optimization and caching strategies
- `../developer/references/api-design.md` - API design guide
- `../security-auditor/workflows/security-audit.md` - Security audit workflow
