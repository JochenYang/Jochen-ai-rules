---
name: frontend
description: Frontend development and optimization for React, Vue, Angular applications. Handles component architecture, state management, responsive design, Core Web Vitals optimization, and accessibility compliance.
license: MIT
compatibility: Requires Node.js, npm/yarn, and modern browsers for testing. Works with Vite, Webpack, or other build tools.
allowed-tools: Read Write Bash
---

# Frontend Development Expert

Deep frontend development and maintenance, focusing on complex scenarios and performance optimization. Suitable for frontend new project development, bug fixes, performance bottleneck optimization, complex component architecture, and all frontend scenarios.

## Core Capabilities

### Development & Maintenance

- React/Vue/Angular component development and maintenance
- Frontend bug localization and fixes
- UI feature expansion and optimization
- State management (Redux/Zustand/Pinia/Vuex)

### Styling & Layout

- CSS/Tailwind/Styled-components styling
- Responsive layout and mobile adaptation
- Accessibility design (WCAG compliance)

### Performance & Optimization

- Frontend performance optimization and Core Web Vitals tuning
- Code splitting and lazy loading
- Complex interaction scenario optimization

## Tech Stack

| Category  | Technologies                                 |
|-----------|----------------------------------------------|
| Framework | React, Vue 3, Angular, Svelte                |
| Build     | Vite, Webpack, Turbopack                     |
| Styling   | Tailwind CSS, CSS Modules, Styled-components |
| State     | Redux Toolkit, Zustand, Pinia, Jotai         |
| Testing   | Jest, Vitest, Testing Library, Playwright    |

## Design Guidelines

### No Gradients Policy

❌ **Absolutely Forbidden**:

- Linear gradients (linear-gradient)
- Radial gradients (radial-gradient)
- Rainbow gradient effects
- Semi-transparent gradient overlays

✅ **Correct Approach**:

- Use solid colors
- Build hierarchy through hue/saturation variations
- Clear color system: Primary + Secondary + Neutral colors

### Responsive Breakpoints

```css
/* Mobile-first */
sm: 640px   /* Small phones */
md: 768px   /* Tablets */
lg: 1024px  /* Laptops */
xl: 1280px  /* Desktops */
2xl: 1536px /* Large screens */
```

## Performance Optimization

- Code splitting and lazy loading
- Image optimization (WebP/AVIF, lazy loading)
- Critical CSS inlining
- Tree shaking to remove unused code

## Core Web Vitals Targets

- **LCP** < 2.5s
- **FID** < 100ms
- **CLS** < 0.1

## Boundaries

Focus on frontend UI and interaction implementation, not backend API and database design.

## Helper Scripts

**Always run `--help` first** to see usage. These scripts are black-box tools - no need to read source code.

- `scripts/optimize-bundle.sh` - Bundle size analysis and optimization

## Detailed References

- `./references/performance-optimization.md` - Core Web Vitals and performance optimization guide
- `../designer/guides/design-system.md` - Design system guide
