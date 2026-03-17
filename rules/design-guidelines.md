---
name: design-guidelines
description: Mandatory UI/UX design standards.
---

# Design Guidelines

**RULE TYPE**: Mandatory UI/UX design standards.

## Visual Baseline

- Keep interface simple, readable, and consistent.
- Reuse existing theme tokens and component library first.
- Avoid overly flashy gradients and heavy visual effects.

## Accessibility (WCAG 2.1 AA)

- Contrast >= 4.5:1 for normal text
- Contrast >= 3:1 for large text
- Keyboard navigable interactions
- Visible focus states
- Semantic HTML structure

## Responsive Rules

1. Build mobile-first.
2. Scale spacing and layout progressively for larger screens.
3. Keep interaction targets accessible on touch devices.

## Consistency Rules

- Unified spacing scale (4/8/12/16/24/32...)
- Unified radius scale (4/8/12...)
- Consistent elevation and shadow depth
- Clear visual hierarchy for primary vs secondary actions

## Color & Theme Rules

- Limit primary color count (recommended <= 3)
- In dark mode, avoid pure black `#000`
- Use design tokens for colors, spacing, and typography
