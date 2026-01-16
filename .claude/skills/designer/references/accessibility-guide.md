# Accessibility Guide

Best practices for creating accessible interfaces.

## WCAG 2.1 AA Compliance

### Core Principles

| Principle | Description | Requirements |
|-----------|-------------|--------------|
| Perceivable | Information presented in ways users can perceive | 1.1-1.4 |
| Operable | UI components and navigation operable | 2.1-2.5 |
| Understandable | Information and operation understandable | 3.1-3.3 |
| Robust | Content robust enough for assistive technologies | 4.1 |

## Color Contrast

### Minimum Ratios
| Level | Normal Text | Large Text | UI Components |
|-------|-------------|------------|---------------|
| AA | 4.5:1 | 3:1 | 3:1 |
| AAA | 7:1 | 4.5:1 | 4.5:1 |

```css
/* Good contrast examples */
.text-primary {
  color: #1a1a1a;       /* Contrast 15.9:1 against white */
  background: #ffffff;
}

.text-muted {
  color: #666666;       /* Contrast 5.9:1 against white */
  background: #ffffff;
}

/* Large text (18pt+ or 14pt bold+) */
.headline {
  color: #2d3748;       /* Contrast 8.8:1 against white */
  font-size: 24px;
}
```

### Color Blindness
```css
/* Don't rely on color alone */
.status-badge {
  /* Bad: Only changes color */
  background: green;
}

/* Good: Icon + color */
.status-badge {
  background: green;
  icon: url('/check-icon.svg');
}

/* Good: Pattern + color */
.status-badge {
  background: green;
  pattern: url('/hatch-pattern.svg');
}
```

## Keyboard Navigation

### Focus Management
```css
/* Visible focus indicators */
:focus-visible {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}

/* Skip link styles */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: #000;
  color: #fff;
  padding: 8px;
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}
```

### Tab Order
```jsx
// Logical tab order
<div>
  <a href="#main">Skip to main content</a>
  <nav>...</nav>
  <main id="main">
    <button>First focusable</button>
    <button>Second focusable</button>
  </main>
  <footer>...</footer>
</div>
```

## Screen Reader Support

### ARIA Attributes
```jsx
// Landmark roles
<header role="banner">...</header>
<nav role="navigation">...</nav>
<main role="main">...</main>
<footer role="contentinfo">...</footer>
<aside role="complementary">...</aside>

// Interactive elements
<button aria-label="Close dialog" onClick={close}>
  <XIcon aria-hidden="true" />
</button>

// Live regions
<div role="status" aria-live="polite">
  {message}
</div>

<div role="alert" aria-live="assertive">
  {errorMessage}
</div>

// Descriptions
<input
  aria-describedby="password-requirements"
  id="password"
/>
<span id="password-requirements">
  Must be at least 8 characters
</span>
```

### Form Labels
```jsx
// Explicit label
<label htmlFor="email">Email address</label>
<input id="email" type="email" />

// Implicit label
<label>
  Email address
  <input type="email" />
</label>

// Aria-label as fallback
<input type="email" aria-label="Email address" />

// Required fields
<label htmlFor="email">
  Email address
  <span aria-hidden="true">*</span>
</label>
<input id="email" required aria-required="true" />
```

## Accessible Components

### Modal Dialog
```jsx
function Modal({ isOpen, onClose, title, children }) {
  const modalRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      modalRef.current?.focus();
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
  }, [isOpen]);

  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      className="modal-overlay"
      onClick={onClose}
    >
      <div
        ref={modalRef}
        className="modal-content"
        tabIndex={-1}
        onClick={e => e.stopPropagation()}
      >
        <h2 id="modal-title">{title}</h2>
        {children}
        <button
          aria-label="Close modal"
          onClick={onClose}
        >
          <XIcon aria-hidden="true" />
        </button>
      </div>
    </div>
  );
}
```

### Data Table
```jsx
<table>
  <caption>User list with {users.length} entries</caption>
  <thead>
    <tr>
      <th scope="col">Name</th>
      <th scope="col">Email</th>
      <th scope="col">Role</th>
    </tr>
  </thead>
  <tbody>
    {users.map(user => (
      <tr key={user.id}>
        <td>{user.name}</td>
        <td>{user.email}</td>
        <td>{user.role}</td>
      </tr>
    ))}
  </tbody>
</table>
```

## Testing Checklist

### Automated Testing
```javascript
// axe-core
import { axe } from 'jest-axe';

it('should have no accessibility violations', async () => {
  const { container } = render(<Component />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});

// Lighthouse
const audit = await new AxeDevtools().audit(page);
```

### Manual Testing
- [ ] Navigate with keyboard only
- [ ] Test with screen reader (NVDA, VoiceOver)
- [ ] Verify color contrast ratios
- [ ] Check focus visibility
- [ ] Test reduced motion preference
- [ ] Verify text scaling (200%)

### Tools
| Tool | Purpose |
|------|---------|
| axe DevTools | Browser extension |
| WAVE | Web accessibility evaluator |
| Lighthouse | Automated auditing |
| Pa11y | CI accessibility testing |
