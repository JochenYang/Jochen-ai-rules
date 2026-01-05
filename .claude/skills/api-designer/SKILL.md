---
name: api-designer
description: API architecture design and documentation for RESTful, GraphQL, and gRPC services. Creates OpenAPI specifications, defines versioning strategies, and establishes authentication/authorization patterns.
license: MIT
compatibility: No special requirements. Outputs OpenAPI/Swagger documentation and design specifications.
metadata:
  author: "jochen-ai"
  version: "1.0.0"
  category: "architecture"
  tags: ["api", "rest", "graphql", "openapi", "design"]
allowed-tools: Read Write
---

# API Designer

Design high-quality API interfaces and output standardized interface documentation and design specifications.

## Core Capabilities

- RESTful/GraphQL/gRPC architecture design
- Unified naming conventions and error handling
- OpenAPI/Swagger documentation generation
- API versioning and backward compatibility
- Authentication, authorization, and rate limiting strategies

## Quick Reference

### HTTP Method Semantics

| Method | Purpose         | Idempotent |
|--------|-----------------|------------|
| GET    | Read resource   | ✅          |
| POST   | Create resource | ❌          |
| PUT    | Full update     | ✅          |
| PATCH  | Partial update  | ❌          |
| DELETE | Delete resource | ✅          |

### Common Status Codes

- `200` Success / `201` Created / `204` No Content
- `400` Bad Request / `401` Unauthorized / `403` Forbidden / `404` Not Found
- `500` Server Error

## Design Principles

1. **Resource-Oriented**: Use plural nouns in URLs, express actions with HTTP methods
2. **Unified Format**: Consistent request/response format, structured error messages
3. **Version Management**: URL or Header version control, backward compatibility
4. **Security First**: Authentication, authorization, input validation, rate limiting

## Boundaries

Focus on API design and documentation standards, not specific business logic implementation.

## Detailed References

- `../developer/references/api-design.md` - API design specifications and best practices
