---
name: frontend-design
description: Implement distinctive, production-grade frontend UI code. Use when user asks to "build a button", "create a navbar", "make a landing page", "implement a card component", "design a form", "create a modal", or says "write React/Vue/HTML/CSS code" for components, pages, or apps with clear direction. If design direction is unclear, use ui-ux-pro-max first.
---

This skill guides creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to aesthetic details and creative choices.

## Boundary With Other Skills

- Use `frontend-design` for **implementation-first UI tasks** (write production code).
- Use `ui-ux-pro-max` for **design-system selection, style reasoning, and UX audits**.
- If user asks both strategy and implementation: run `ui-ux-pro-max` first, then implement with `frontend-design`.

The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

## Design Thinking

Before coding, understand the context and commit to a BOLD aesthetic direction:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc. There are so many flavors to choose from. Use these for inspiration but design one that is true to the aesthetic direction.
- **Constraints**: Technical requirements (framework, performance, accessibility).
- **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?

**CRITICAL**: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work - the key is intentionality, not intensity.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:
- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

## Frontend Aesthetics Guidelines

Focus on:
- **Typography**: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics; unexpected, characterful font choices. Pair a distinctive display font with a refined body font.
- **Color & Theme**: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes.
- **Motion**: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. Use scroll-triggering and hover states that surprise.
- **Spatial Composition**: Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Grid-breaking elements. Generous negative space OR controlled density.
- **Backgrounds & Visual Details**: Create atmosphere and depth rather than defaulting to solid colors. Add contextual effects and textures that match the overall aesthetic. Apply creative forms like gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, and grain overlays.

NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients on white backgrounds), predictable layouts and component patterns, and cookie-cutter design that lacks context-specific character.

Interpret creatively and make unexpected choices that feel genuinely designed for the context. No design should be the same. Vary between light and dark themes, different fonts, different aesthetics. NEVER converge on common choices (Space Grotesk, for example) across generations.

**IMPORTANT**: Match implementation complexity to the aesthetic vision. Maximalist designs need elaborate code with extensive animations and effects. Minimalist or refined designs need restraint, precision, and careful attention to spacing, typography, and subtle details. Elegance comes from executing the vision well.

Remember: Claude is capable of extraordinary creative work. Don't hold back, show what can truly be created when thinking outside the box and committing fully to a distinctive vision.

## Examples

### Example 1: Button Component
User says: "Create a submit button with hover animation"
Actions:
1. Choose bold aesthetic direction (e.g., brutalist with sharp edges)
2. Select distinctive font pairing
3. Implement CSS with meaningful hover/focus states
4. Add micro-interaction animation
Result: Production-ready button code

### Example 2: Landing Page
User says: "Build a SaaS landing page for a dev tool"
Actions:
1. Define aesthetic (e.g., terminal-inspired brutalist)
2. Create hero, features, pricing sections
3. Use CSS animations for entrance effects
4. Ensure responsive design
Result: Complete HTML/CSS landing page

### Example 3: Card Component
User says: "Design a product card with hover effects"
Actions:
1. Pick visual direction (e.g., soft/pastel luxury)
2. Implement card layout with CSS Grid/Flexbox
3. Add depth with shadows, gradients, or transforms
4. Create hover state animations
Result: Reusable card component

## Troubleshooting

### Issue: Output looks generic/AI-generated
Cause: Defaulting to safe choices (Inter font, purple gradients, centered layouts)
Solution: Commit to a specific aesthetic direction before coding. Reference the Design Thinking section.

### Issue: Design doesn't match the intended tone
Cause: Skipping the context analysis step
Solution: Before coding, explicitly state: "This interface is [brutalist/minimalist/luxury/etc] because [reason]."

### Issue: Layout breaks on mobile
Cause: Hardcoded dimensions or desktop-only breakpoints
Solution: Use relative units (rem/vh/vw), implement mobile-first media queries, test responsive behavior.
