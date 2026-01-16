# GraphQL API Design Guide

Best practices for designing GraphQL APIs.

## Schema Design

### Type System
```graphql
# Scalar types
scalar DateTime
scalar UUID
scalar Email

# Object types
type User {
  id: ID!
  email: Email!
  name: String!
  role: UserRole!
  createdAt: DateTime!
  updatedAt: DateTime!
  orders: [Order!]!
  profile: Profile
}

# Enums
enum UserRole {
  USER
  ADMIN
}

# Input types
input CreateUserInput {
  email: Email!
  name: String!
  password: String!
  role: UserRole
}

# Union types
union SearchResult = User | Product | Article

# Interface
interface Node {
  id: ID!
}

type User implements Node {
  id: ID!
  email: Email!
  name: String!
}
```

### Query Design
```graphql
# Simple query
query GetUser($id: ID!) {
  user(id: $id) {
    id
    name
    email
  }
}

# Nested queries (avoid over-fetching)
query GetUserWithOrders($id: ID!) {
  user(id: $id) {
    id
    name
    orders(first: 10) {
      edges {
        node {
          id
          total
          items {
            name
            quantity
          }
        }
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
}
```

### Mutation Design
```graphql
# Single mutation
mutation CreateUser($input: CreateUserInput!) {
  createUser(input: $input) {
    user {
      id
      email
    }
    errors {
      field
      message
    }
  }
}

# Batch mutations
mutation UpdateUsers($input: [UpdateUserInput!]!) {
  updateUsers(input: $input) {
    results {
      user {
        id
        name
      }
      success
      error
    }
  }
}
```

## Performance Optimization

### Pagination
```graphql
# Relay-style cursor pagination
type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type UserEdge {
  node: User!
  cursor: String!
}

# Query
query GetUsers($first: Int, $after: String) {
  users(first: $first, after: $after) {
    edges {
      node {
        id
        name
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

### Dataloader Pattern
```javascript
// Prevent N+1 queries
const userLoader = new DataLoader(async (userIds) => {
  const users = await User.findByIds(userIds);
  return userIds.map(id => users.find(u => u.id === id));
});

const resolvers = {
  Query: {
    user: (_, { id }) => userLoader.load(id),
  },
  User: {
    orders: (user) => Order.findByUserId(user.id),
  }
};
```

### Query Complexity Limits
```javascript
const costAnalysisPlugin = {
  overallCostLimit: 1000,
  perQueryCostLimit: 100,
  multipliers: {
    listSizeArg: 'limit',
  }
};
```

## Best Practices

### Naming Conventions
- Use camelCase for fields
- Use PascalCase for types
- Use SCREAMING_SNAKE_CASE for enums
- Use descriptive, non-ambiguous names

### Nullability
- Make non-nullable only when truly required
- Use nullable fields for optional data
- Consider field deprecation strategy

### Deprecation
```graphql
type User {
  oldField: String @deprecated(reason: "Use 'newField' instead")
}
```

## Tools

```bash
# Generate GraphQL schema
npm run graphql:generate

# Validate schema
npm run graphql:validate

# Generate TypeScript types
npm run graphql:codegen
```
