# Frontend Architecture Patterns

Modern frontend component patterns and state management practices.

## 1. Component Composition

**Principle**: Build complex UIs by combining simpler components.

```tsx
// Using children for flexible layouts
function Card({
  children,
  title,
}: {
  children: React.ReactNode;
  title: string;
}) {
  return (
    <div className="card">
      <h3>{title}</h3>
      {children}
    </div>
  );
}

// Composition
<Card title="User Profile">
  <Avatar src="..." />
  <UserInfo name="..." />
</Card>;
```

---

## 2. Container/Presenter Pattern

**Goal**: Separate logic (data fetching, state) from UI (presentation).

- **Container**: Handles data, side effects, and logic.
- **Presenter**: Pure component that receives data via props.

```tsx
// Container
function UserListContainer() {
  const { data, loading } = useUsers();
  if (loading) return <Spinner />;
  return <UserList users={data} />;
}

// Presenter
function UserList({ users }) {
  return (
    <ul>
      {users.map((u) => (
        <li key={u.id}>{u.name}</li>
      ))}
    </ul>
  );
}
```

---

## 3. Custom Hooks (Logic Reuse)

**Goal**: Extract cross-component stateful logic into reusable functions.

```typescript
function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState(() => {
    const saved = localStorage.getItem(key);
    return saved ? JSON.parse(saved) : initialValue;
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue] as const;
}
```

---

## 4. Context Layer (Global State)

**Goal**: Avoid prop drilling for global data like themes, localization, or auth.

```tsx
const AuthContext = createContext<Auth | null>(null);

function AuthProvider({ children }) {
  const auth = useProvideAuth();
  return <AuthContext.Provider value={auth}>{children}</AuthContext.Provider>;
}

// Usage
const auth = useContext(AuthContext);
```

---

## 5. Compound Components

**Goal**: Provide a clean and expressive API for complex components (e.g., Select, Tabs).

```tsx
<Select>
  <Select.Trigger />
  <Select.Content>
    <Select.Option value="1">Option 1</Select.Option>
  </Select.Content>
</Select>
```

---

## 6. Render Props & HOCs

- **Render Props**: Share code via a function prop.
- **HOC (Higher-Order Component)**: Wrap components to inject functionality.
  _(Note: Use hooks for these scenarios in modern development whenever possible.)_

---

## 7. Strategic Code Splitting

- **Route Based**: Split chunks by application routes.
- **Component Based**: Split heavy third-party libraries (e.g., Maps, Editors).
- **User Action Based**: Load on hover or click.
