# Redesign Audit

Use this reference when the task is to improve an existing website, landing
page, dashboard, or app shell without rewriting it from scratch.

## Working Sequence

1. **Scan** - identify framework, styling system, and current UI patterns
2. **Diagnose** - list the generic patterns, weak hierarchy, and missing states
3. **Fix** - upgrade the existing implementation in place

Default posture:

- work with the existing stack
- keep functionality stable
- prefer focused improvements over large rewrites
- validate after each change

## Audit Checklist

### Typography

- browser defaults or Inter used everywhere without intent
- display text lacks size, weight, tracking, or line-height discipline
- body text runs too wide for comfortable reading
- only 400 and 700 weights are used
- data-heavy surfaces use proportional numerals
- labels, caps, and metadata lack tracking adjustments
- sentence wrapping creates obvious orphans

### Color And Surfaces

- pure black backgrounds where a tinted dark would feel better
- more than one accent color competing for attention
- warm and cool grays mixed in the same surface system
- purple or blue AI gradients used by default
- generic black drop shadows instead of palette-aware depth
- flat sections with no texture, imagery, or tonal hierarchy
- random dark section dropped into an otherwise light page

### Layout

- everything centered and symmetrical
- generic three-column feature cards
- `100vh` used where `100dvh` is safer
- flexbox percentage math where grid should be used
- no container or max-width constraint
- every region boxed into equal-height cards
- no overlap, layering, or sectional contrast where the brief needs depth
- inconsistent button baselines or pricing-table alignment
- mobile collapse creates horizontal scroll or touch-target conflicts

### Interaction And States

- no hover, pressed, or focus states
- transitions are instant or inconsistent
- loading uses generic spinners instead of shape-matched skeletons
- empty and error states are missing
- dead links still point to `#`
- no visible active navigation state
- motion animates layout properties instead of transforms and opacity

### Content

- lorem ipsum, placeholder brands, generic people names, or fake round numbers
- homepage slogans showing up inside product UI
- repeated copy with no section-level responsibility
- error messages sound vague, loud, or overly cute
- dates, avatars, and examples look duplicated or obviously fake

### Components

- default shadcn or generic border-plus-shadow card styling
- every CTA pair is filled plus ghost with no hierarchy
- FAQ always rendered as a boxed accordion
- testimonials and pricing use generic three-tower layouts
- every action opens a modal even when inline disclosure would work better

### Code And Semantics

- div soup where semantic tags should exist
- inline styles fighting the project styling system
- hardcoded widths that break responsive behavior
- missing alt text, meta tags, or favicon
- arbitrary z-index values
- commented-out dead code or import hallucinations

## High-Impact Upgrade Moves

Apply the smallest useful set:

- swap fonts first
- clean the palette next
- add hover, active, focus, loading, empty, and error states
- fix grid, spacing, and container constraints
- replace generic card rows with more intentional composition
- add subtle imagery, grain, or tonal depth where sections feel flat
- tighten copy so each section has one job

## Fix Priority

1. Font and typography hierarchy
2. Palette cleanup and surface consistency
3. Hover, pressed, focus, loading, empty, and error states
4. Layout containment, spacing, and mobile collapse
5. Generic component replacement
6. Final polish on motion, copy, and depth

## Guardrails

- do not migrate frameworks or styling libraries unless explicitly requested
- do not break existing functionality
- verify dependencies before importing new packages
- keep the final diff reviewable and scoped
