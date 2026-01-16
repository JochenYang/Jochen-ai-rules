# Typography System Guide

Best practices for establishing and using a typography system.

## Type Scale

### Major Third Scale (1.25)
```
Base: 16px

Scale:
xs   = 12px  (0.75rem)
sm   = 14px  (0.875rem)
base = 16px  (1rem)
lg   = 20px  (1.25rem)
xl   = 24px  (1.5rem)
2xl  = 30px  (1.875rem)
3xl  = 38px  (2.375rem)
4xl  = 48px  (3rem)
5xl  = 60px  (3.75rem)
```

### Perfect Fourth Scale (1.333)
```
xs   = 12px  (0.75rem)
sm   = 14px  (0.875rem)
base = 16px  (1rem)
lg   = 21px  (1.333rem)
xl   = 28px  (1.777rem)
2xl  = 38px  (2.369rem)
3xl  = 50px  (3.157rem)
4xl  = 67px  (4.209rem)
```

## Font Families

### Primary Font (Headings)
```css
--font-display: 'Inter', system-ui, -apple-system, sans-serif;
```

### Secondary Font (Body)
```css
--font-body: 'Inter', system-ui, -apple-system, sans-serif;
```

### Monospace Font
```css
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

### Chinese/Japanese/Korean
```css
--font-cjk: 'Noto Sans SC', 'PingFang SC', 'Hiragino Sans GB', sans-serif;
```

## Font Weights

| Name | Weight | Usage |
|------|--------|-------|
| Thin | 100 | Decorative |
| Light | 300 | Large text, emphasis |
| Regular | 400 | Body text |
| Medium | 500 | Subtitles, buttons |
| Semibold | 600 | Section headers |
| Bold | 700 | Headings, emphasis |
| Extrabold | 800 | Display text |
| Black | 900 | Display text |

## Line Heights

| Usage | Line Height | Example |
|-------|-------------|---------|
| Headings | 1.2 - 1.3 | 1.25 |
| Body text | 1.5 - 1.7 | 1.6 |
| Large text | 1.3 - 1.4 | 1.35 |
| Tight | 1.1 - 1.2 | 1.2 |
| Loose | 1.8 - 2.0 | 1.8 |

## Letter Spacing

| Usage | Tracking | Example |
|-------|----------|---------|
| Large text | -0.02em | Headings |
| Body text | 0 | Normal |
| Small caps | 0.1em | Labels, tags |
| Wide | 0.05em | All caps |

## CSS Custom Properties

```css
:root {
  /* Font families */
  --font-display: 'Inter', system-ui, sans-serif;
  --font-body: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  /* Font sizes */
  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.875rem;   /* 14px */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.125rem;   /* 18px */
  --text-xl: 1.25rem;    /* 20px */
  --text-2xl: 1.5rem;    /* 24px */
  --text-3xl: 1.875rem;  /* 30px */
  --text-4xl: 2.25rem;   /* 36px */

  /* Font weights */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  /* Line heights */
  --leading-tight: 1.2;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;

  /* Letter spacing */
  --tracking-tight: -0.02em;
  --tracking-normal: 0;
  --tracking-wide: 0.025em;
}
```

## Type Utility Classes

```css
/* Headings */
.text-display {
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  line-height: var(--leading-tight);
  letter-spacing: var(--tracking-tight);
}

.text-h1 {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  line-height: var(--leading-tight);
}

.text-h2 {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  line-height: var(--leading-tight);
}

.text-h3 {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  line-height: var(--leading-normal);
}

/* Body */
.text-body {
  font-size: var(--text-base);
  font-weight: var(--font-normal);
  line-height: var(--leading-normal);
}

.text-small {
  font-size: var(--text-sm);
  line-height: var(--leading-normal);
}

.text-caption {
  font-size: var(--text-xs);
  line-height: var(--leading-normal);
  color: var(--text-muted);
}
```

## Responsive Typography

```css
/* Fluid typography using clamp() */
.text-fluid {
  font-size: clamp(1rem, 2vw + 0.5rem, 1.5rem);
}

/* Mobile-first responsive */
.text-h1 {
  font-size: var(--text-2xl);
}

@media (min-width: 768px) {
  .text-h1 {
    font-size: var(--text-3xl);
  }
}

@media (min-width: 1024px) {
  .text-h1 {
    font-size: var(--text-4xl);
  }
}
```

## Best Practices

### Do
- Use relative units (rem, em)
- Set base font size on html
- Maintain vertical rhythm
- Use type scale consistently
- Ensure sufficient contrast
- Test readability at all sizes

### Don't
- Use px for font sizes
- Mix too many fonts (max 2-3)
- Use all caps for long text
- Set line-height too tight (<1.4 for body)
- Rely solely on font size for hierarchy
