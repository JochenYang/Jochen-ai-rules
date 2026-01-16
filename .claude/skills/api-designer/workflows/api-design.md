# API Design Workflow

Systematic approach to designing robust and maintainable APIs.

## Design Phases

### Phase 1: Requirements Analysis
1. **Identify Resources**
   - Define core entities
   - Determine resource relationships
   - Map business processes to API operations

2. **Define Operations**
   - CRUD operations per resource
   - Business-specific actions
   - Batch operations

### Phase 2: Endpoint Design

#### RESTful Conventions
```
GET    /users              # List users
GET    /users/{id}         # Get user
POST   /users              # Create user
PUT    /users/{id}         # Update user (full)
PATCH  /users/{id}         # Update user (partial)
DELETE /users/{id}         # Delete user

GET    /users/{id}/orders  # Nested resource
POST   /users/{id}/orders  # Create order for user
```

#### Naming Guidelines
- Use nouns for resources (not verbs)
- Use lowercase with hyphens
- Use plural names for collections
- Max 2 levels of nesting

### Phase 3: Data Modeling

#### Request/Response Schemas
```typescript
// User creation request
interface CreateUserRequest {
  email: string;
  name: string;
  password: string;
  role?: 'user' | 'admin';
}

// User response (without sensitive data)
interface UserResponse {
  id: string;
  email: string;
  name: string;
  role: 'user' | 'admin';
  createdAt: string;
  updatedAt: string;
}
```

#### Error Response Standard
```typescript
interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
    path: string;
    timestamp: string;
  };
}

// Example
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": ["Must be a valid email address"]
    },
    "path": "/users",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Phase 4: Versioning Strategy

#### URL Versioning
```
/v1/users
/v2/users
```

#### Header Versioning (Optional)
```
Accept: application/vnd.api+json;version=1
```

### Phase 5: Documentation

#### OpenAPI Specification
```yaml
openapi: 3.0.3
info:
  title: User API
  version: 1.0.0
  description: API for managing users

servers:
  - url: https://api.example.com/v1

paths:
  /users:
    get:
      summary: List users
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: Paginated user list
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  pagination:
                    $ref: '#/components/schemas/Pagination'

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
        email:
          type: string
          format: email
        name:
          type: string
```

### Phase 6: Security Design

#### Authentication
- Bearer token authentication
- OAuth 2.0 for third-party access
- API keys for service-to-service

#### Authorization
- Role-based access control (RBAC)
- Attribute-based access control (ABAC)
- Scope-based permissions

#### Rate Limiting
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Tools

```bash
# Generate OpenAPI documentation
./scripts/openapi-gen.sh --input src --output docs/openapi.yaml

# Validate API design
./scripts/validate-api.sh --spec docs/openapi.yaml
```
