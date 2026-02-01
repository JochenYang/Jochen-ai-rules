# Backend Architecture Patterns

Standard backend architecture patterns and best practices.

## 1. Domain-Driven Design (DDD) Basics

### Entities & Value Objects

- **Entities**: Objects with a unique identity (e.g., User ID).
- **Value Objects**: Defined by their attributes, no identity (e.g., Address, Money). Always immutable.

### Aggregates

A cluster of associated objects treated as a unit for data changes. Accessed via an **Aggregate Root**.

---

## 2. Repository Pattern

**Goal**: Separate business logic from data access details.

```typescript
// Interface
interface IUserRepository {
  getById(id: string): Promise<User | null>;
  save(user: User): Promise<void>;
  delete(id: string): Promise<void>;
}

// Implementation (Prisma example)
class PrismaUserRepository implements IUserRepository {
  async getById(id: string) {
    return prisma.user.findUnique({ where: { id } });
  }
}
```

---

## 3. Service Layer

**Goal**: Encapsulate business logic and coordinate between resources or external services.

```typescript
class RegistrationService {
  constructor(
    private userRepo: IUserRepository,
    private emailService: IEmailService,
  ) {}

  async register(data: RegisterDTO) {
    const user = User.create(data);
    await this.userRepo.save(user);
    await this.emailService.sendWelcome(user.email);
    return user;
  }
}
```

---

## 4. CQRS (Command Query Responsibility Segregation)

**Goal**: Separate update operations (Commands) from read operations (Queries).

### Command (Write)

```typescript
interface Command {
  execute(): Promise<void>;
}

class CreateUserCommand implements Command {
  constructor(private data: any) {}
  async execute() {
    /* Handle write logic */
  }
}
```

### Query (Read)

```typescript
class UserQueries {
  async getProfile(id: string) {
    /* Read directly from DB/Cache, bypass domain model */
  }
}
```

---

## 5. Event-Driven Architecture (EDA)

**Goal**: Achieve loose coupling between components.

```typescript
// Domain Event
class UserRegisteredEvent {
  constructor(public readonly userId: string) {}
}

// Handler
class SendWelcomeEmailHandler {
  handle(event: UserRegisteredEvent) {
    // Handle email sending asynchronously
  }
}
```

---

## 6. Middleware Patterns

### Common Middlewares

- **Auth**: Authorization and authentication.
- **Validation**: Input validation (e.g., Zod, Joi).
- **Logging**: Request/Response logging.
- **Error Handling**: Unified exception handling.
- **Rate Limiting**: Prevent abuse.

---

## 7. API Gateway & Microservices Patterns

- **BFF (Backend for Frontend)**: Tailored APIs for different clients.
- **Circuit Breaker**: Prevent cascading failures.
- **Sidecar**: Handle logging, metrics, security, etc.
