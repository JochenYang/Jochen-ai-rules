# Web Development Best Practices

Essential guidelines for modern web application development.

## Project Structure

```
src/
├── components/     # Reusable UI components
├── pages/          # Route-level components
├── hooks/          # Custom React hooks
├── services/       # API clients and services
├── utils/          # Helper functions
├── types/          # TypeScript type definitions
├── constants/      # Application constants
├── assets/         # Static assets
└── styles/         # Global styles
```

## Component Design

### Composition Pattern
```tsx
// Good: Composable components
function Card({ children, className }) {
  return <div className={`card ${className}`}>{children}</div>;
}

function CardHeader({ children }) {
  return <div className="card-header">{children}</div>;
}

function CardContent({ children }) {
  return <div className="card-content">{children}</div>;
}

// Usage
<Card>
  <CardHeader>Title</CardHeader>
  <CardContent>Content</CardContent>
</Card>
```

### Custom Hooks
```tsx
// Good: Extract logic into hooks
function useAsync<T>(
  asyncFn: () => Promise<T>,
  immediate = true
) {
  const [state, setState] = useState<T | null>(null);
  const [loading, setLoading] = useState(immediate);
  const [error, setError] = useState<Error | null>(null);

  const execute = async () => {
    setLoading(true);
    try {
      const result = await asyncFn();
      setState(result);
      return result;
    } catch (e) {
      setError(e);
      throw e;
    } finally {
      setLoading(false);
    }
  };

  return { state, loading, error, execute };
}
```

## State Management

### Local State
```tsx
// Use useState for local component state
function SearchInput() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const handleSearch = useCallback(async () => {
    const data = await search(query);
    setResults(data);
  }, [query]);

  return <input value={query} onChange={e => setQuery(e.target.value)} />;
}
```

### Global State
```tsx
// Use context for global state
const ThemeContext = createContext<ThemeContextType>(defaultTheme);

function ThemeProvider({ children }) {
  const [theme, setTheme] = useState<Theme>('light');

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}
```

## API Integration

### Service Layer
```typescript
// api/client.ts
const BASE_URL = process.env.API_URL;

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new ApiError(response);
  }

  return response.json();
}

// api/users.ts
export const UserService = {
  getAll: () => request<User[]>('/users'),
  getById: (id: string) => request<User>(`/users/${id}`),
  create: (data: CreateUserDto) =>
    request<User>('/users', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: string, data: UpdateUserDto) =>
    request<User>(`/users/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: string) =>
    request<void>(`/users/${id}`, { method: 'DELETE' }),
};
```

## Error Handling

### Boundary Pattern
```tsx
function ErrorBoundary({ children }: { children: ReactNode }) {
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    window.addEventListener('error', e => setError(e.error));
  }, []);

  if (error) {
    return <FallbackComponent error={error} />;
  }

  return children;
}
```

### Async Error Handling
```tsx
async function handleSubmit() {
  try {
    await submitForm(data);
    showSuccess('Form submitted');
  } catch (error) {
    if (error instanceof ValidationError) {
      showFieldErrors(error.fields);
    } else {
      showError('Submission failed');
    }
  }
}
```

## Accessibility

### ARIA Labels
```tsx
<button
  aria-label="Close dialog"
  onClick={onClose}
>
  <XIcon aria-hidden="true" />
</button>

<input
  aria-invalid={hasError}
  aria-describedby="email-helper"
  id="email"
/>
<span id="email-helper" className="helper-text">
  Enter your email address
</span>
```

### Keyboard Navigation
```tsx
// Focus management
function Dialog({ isOpen, onClose }) {
  const focusRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (isOpen) {
      focusRef.current?.focus();
    }
  }, [isOpen]);

  return (
    <dialog open={isOpen} ref={focusRef}>
      <button onClick={onClose} autoFocus>Close</button>
      {children}
    </dialog>
  );
}
```

## Testing

### Component Tests
```tsx
import { render, screen, fireEvent } from '@testing-library/react';

describe('Button', () => {
  it('renders with label', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button')).toHaveTextContent('Click me');
  });

  it('calls onClick when clicked', () => {
    const onClick = jest.fn();
    render(<Button onClick={onClick}>Click me</Button>);
    fireEvent.click(screen.getByRole('button'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});
```
