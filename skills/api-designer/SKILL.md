---
name: api-designer
description: API architecture design and documentation for RESTful, GraphQL, and gRPC services. Creates OpenAPI specifications, defines versioning strategies, and establishes authentication/authorization patterns. Use when user asks to design API, create endpoints, document REST/GraphQL, or plan API architecture.
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

## When NOT to Use

- Writing implementation code → use `developer`
- Database schema design → use `database-engineer`
- Frontend UI development → use `frontend-design`
- Infrastructure or DevOps setup → use `devops-engineer`

## When To Use

Use this skill when the user asks to:

- design a new API or endpoint structure
- document existing APIs with OpenAPI/Swagger
- plan API versioning or migration strategy
- establish authentication/authorization patterns for APIs

## Quick Reference

**Always run `--help` first** to see usage.

- `scripts/openapi-gen.sh` - Generate OpenAPI documentation

## Detailed References

- `./workflows/api-design.md` - API design workflow
- `./guides/rest-api.md` - REST API design guide
- `./guides/graphql.md` - GraphQL API design guide
- `./guides/grpc.md` - gRPC API design guide

## Escalation Rules

Pause and ask the owner before:

- locking in an API style, auth model, or versioning strategy that has broad product impact
- expanding from interface design into implementation details outside this skill's boundary
- making compatibility assumptions that could break existing clients

## Final Output Contract (MANDATORY)

Every use of this skill should end with:

1. `Skill Fit` - why API design work was needed
2. `Primary Deliverable` - interface design, spec, or contract summary
3. `Execution Evidence` - references used, files produced, and validation performed
4. `Risks / Open Questions` - compatibility, auth, or rollout concerns
5. `Next Action` - the concrete documentation, review, or implementation step
