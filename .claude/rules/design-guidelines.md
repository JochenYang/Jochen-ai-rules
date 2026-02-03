# Design Guidelines

**RULE TYPE**: Global mandatory design standards that ALL UI/UX work must follow.

These are non-negotiable requirements for visual design and user experience.

---

## Visual Style

- Simple, flat, readable designs
- **NO** large gradient backgrounds
- **NO** complex shine/gradient effects
- Prioritize existing project theme colors and UI component libraries

## Color System

### Primary + Neutral Palette
- Build unified color scheme with ≤5 primary colors
- Ensure text-to-background contrast ratio ≥ 4.5:1 (WCAG AA)
- Dark mode: Use soft grays (avoid pure black #000)

### Color Usage
```css
/* GOOD */
.primary-color { color: #3B82F6; }
.background { background: #1E293B; }
.text-primary { color: #F8FAFC; }

/* BAD */
.background { background: #000000; }  /* Too harsh */
.gradient { background: linear-gradient(135deg, #ff00cc, #333399); }  /* Too flashy */
```

## Design Principles

### Mobile-First Responsive Design
```css
/* Mobile first */
.card { padding: 16px; }

/* Then expand for larger screens */
@media (min-width: 768px) {
  .card { padding: 24px; }
}
```

### Consistency
- Unified spacing (4px, 8px, 12px, 16px, 24px, 32px...)
- Consistent border radius (4px, 8px, 12px...)
- Consistent shadow depths

### Accessibility (WCAG 2.1 AA)
- Color contrast ≥ 4.5:1 for normal text
- Color contrast ≥ 3:1 for large text
- Keyboard accessible
- Focus indicators visible
- Semantic HTML

### Visual Hierarchy
- Use size, color, and spacing to distinguish importance
- Primary actions: Bold, prominent
- Secondary actions: Subtle, less prominent
- Disabled states: Grayed out

## Component Guidelines

### Button Styles
```css
.btn-primary {
  background: var(--primary-color);
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
}

.btn-secondary {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 12px 24px;
  border-radius: 8px;
}
```

### Card Layout
```css
.card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
```

## Spacing Scale
```
0px   - 0
4px   - 0.25rem
8px   - 0.5rem
12px  - 0.75rem
16px  - 1rem    (base)
20px  - 1.25rem
24px  - 1.5rem
32px  - 2rem
40px  - 2.5rem
48px  - 3rem
64px  - 4rem
```

## Dark Mode
```css
:root {
  --bg-primary: #FFFFFF;
  --bg-secondary: #F1F5F9;
  --text-primary: #0F172A;
}

[data-theme="dark"] {
  --bg-primary: #1E293B;
  --bg-secondary: #334155;
  --text-primary: #F8FAFC;
}
```
