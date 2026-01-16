# REST API Design Guide

Best practices for designing RESTful APIs.

## Principles

### REST Constraints
- **Client-Server**: Separation of concerns
- **Stateless**: Each request independent
- **Cacheable**: Improve performance
- **Uniform Interface**: Consistent resource access
- **Layered System**: Architecture flexibility

## Resource Design

### URL Structure
```
https://api.example.com/{version}/{resource}/{id}/{sub-resource}
```

### HTTP Methods
| Method | Idempotent | Safe | Usage |
|--------|------------|------|-------|
| GET    | Yes        | Yes  | Retrieve resource |
| POST   | No         | No   | Create resource |
| PUT    | Yes        | No   | Replace resource |
| PATCH  | No         | No   | Partial update |
| DELETE | Yes        | No   | Delete resource |

### Examples
```http
GET    /api/v1/users              # List users
GET    /api/v1/users?page=2       # Paginated list
GET    /api/v1/users/123          # Get specific user
POST   /api/v1/users              # Create user
PUT    /api/v1/users/123          # Replace user
PATCH  /api/v1/users/123          # Update user fields
DELETE /api/v1/users/123          # Delete user
GET    /api/v1/users/123/orders   # User's orders
```

## Response Design

### Success Responses
```json
// Single resource
{
  "data": {
    "id": "123",
    "name": "John Doe"
  }
}

// Collection
{
  "data": [
    { "id": "1", "name": "User 1" },
    { "id": "2", "name": "User 2" }
  ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "totalPages": 5
  },
  "links": {
    "first": "/users?page=1",
    "last": "/users?page=5",
    "next": "/users?page=2",
    "prev": null
  }
}
```

### Error Responses
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "User with id '123' not found",
    "details": {
      "resource": "User",
      "id": "123"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "path": "/api/v1/users/123"
  }
}
```

## Query Parameters

### Filtering
```
GET /users?role=admin&active=true
GET /users?createdAfter=2024-01-01
GET /users?sort=-createdAt,name
```

### Pagination
```
GET /users?page=1&limit=20
```

### Field Selection
```
GET /users?fields=id,name,email
```

## Content Negotiation

### Request Headers
```
Accept: application/json
Accept: application/vnd.api+json
```

### Versioning via Header (Optional)
```
Accept: application/vnd.api+json;version=1
```

## Best Practices

### Do
- Use plural nouns for collections
- Use HTTP status codes correctly
- Include self-referencing links (HATEOAS)
- Version your API from the start
- Use pagination for collections
- Include request IDs for tracing

### Don't
- Use verbs in URLs
- Mix plural and singular
- Return sensitive data
- Use random IDs
- Break backward compatibility without versioning
