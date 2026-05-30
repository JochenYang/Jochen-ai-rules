---
name: frontend-design
description: Implement distinctive, production-grade frontend UI code with strong visual direction, motion systems, local media asset generation, conversion-aware copy, and polished frontend execution. Use when building landing pages, marketing sites, product pages, dashboards, motion-heavy interfaces, or frontend experiences that need real assets and compelling copy.
---

# Frontend Design

Build distinctive, production-grade frontend interfaces that feel intentional,
polished, and ready to ship. This skill exists to prevent generic AI UI: weak
typography, timid color, repetitive layouts, placeholder copy, and ornamental
motion.

## Use This Skill When

- the output is implemented frontend code, not just critique
- the task is a landing page, product page, marketing site, dashboard, app
  shell, docs surface, or interactive prototype
- the UI needs strong visual direction, premium polish, motion, assets, or
  conversion-aware copy
- an existing frontend needs targeted redesign without a full rewrite

## Do Not Use This Skill When

- the task is backend, API, database, or infrastructure work
- the user wants UX critique before implementation -> use `ui-ux-pro-max`
- the user wants broader full-stack delivery -> use `developer`

## Non-Negotiables

- Do not ship generic AI aesthetics.
- Do not guess critical design direction when it would materially change the
  implementation.
- Do not design from scratch when local code, screenshots, or a design system
  already exist and can be mined first.
- Do not use placeholder copy, placeholder media URLs, or half-finished code.
- Do not break an existing design system unless the user explicitly asks.
- Do not add heavy motion or media without clear payoff.
- If a required asset is missing, prefer an explicit local placeholder or
  simple custom illustration over irrelevant stock UI or fake product chrome.

## Execution Model

Before implementation, lock these four inputs:

- **Purpose**: what the interface does and who it serves
- **Anchor**: brand, product, or mood reference
- **Constraints**: framework, design system, accessibility, performance,
  device priority
- **Difference-maker**: the one memorable visual or interaction idea

Then write three anchors:

- **Visual thesis**: one sentence for mood, material, and energy
- **Content plan**: hero, support, detail, final CTA
- **Interaction thesis**: two or three motion ideas that change the feel of
  the page

Each section gets one job, one dominant idea, and one primary takeaway or
action.

## Design Controls

Use these internal dials to avoid generic output:

- **DESIGN_VARIANCE**
  - `1-3`: restrained, symmetrical, predictable
  - `4-7`: offset, structured, moderately experimental
  - `8-10`: asymmetric, broken-grid, high-contrast composition
- **MOTION_INTENSITY**
  - `1-3`: hover, focus, pressed states only
  - `4-7`: reveals, stagger, restrained choreography
  - `8-10`: scroll-linked sequencing, magnetic motion, cinematic behavior
- **VISUAL_DENSITY**
  - `1-3`: airy, luxurious, gallery-like
  - `4-7`: balanced product UI
  - `8-10`: dense operational or telemetry surfaces

Default baseline:

- `DESIGN_VARIANCE = 6`
- `MOTION_INTENSITY = 4`
- `VISUAL_DENSITY = 4`

Adapt the dials to the product type, user request, and existing brand language.

## Clarification Rule

If missing information would materially change the implementation, ask exactly
one focused clarification question before proceeding.

Clarification triggers:

- no clear reference anchor
- no clear interface type
- unclear motion intensity
- unclear device priority
- unclear requirement to preserve an existing brand or design system
- no usable design context for a net-new design task

Use `AskUserQuestion` if available. If not, ask the same question in plain
text. Prefer multiple-choice framing. Ask one thing at a time.

When no brand or style is specified, proactively recommend 2-3 anchors from
`design-md/` based on page type and product tone. Example question patterns:

- "Which direction should we anchor to: a specific brand in `design-md/`, a
  URL reference, or a mood description?"
- "Is there an existing brand or design system I must preserve?"
- "What is the best starting context: existing repo UI, screenshots, a design
  system, or should I choose an anchor and proceed?"

Skip clarification only when:

- the repo already has a strong design system
- the user explicitly says to choose the direction
- the missing detail would not meaningfully change the implementation

If you proceed without asking, state the assumption first.

## Workflow

### 1. Align

1. Identify page type, audience, and technical constraints.
2. Confirm framework and styling stack before importing dependencies.
3. If direction is ambiguous enough to change the build, ask one question.
4. Inspect the most relevant existing UI context first: local components,
   screenshots, route shells, design-system docs, or brand references.
5. If the user names a brand or style, immediately load
   `design-md/<brand>/DESIGN.md` and treat it as authoritative.
6. If no brand is named, recommend 2-3 anchors from `design-md/` based on page
   type and product tone, then load the chosen anchor.
7. If no anchor fits, summarize the intended style as a visual thesis before
   building.
8. When offering options, recommend 2-3 concrete directions max.

### 2. Plan

1. Break the UI into sections and reusable components.
2. Decide which sections need motion, which need static polish, and which need
   supporting media.
3. Set the three design controls.
4. Prefer the smallest toolset that can still deliver the effect.
5. Decide whether the task is best handled as direct implementation, a focused
   design study, or a clickable prototype.

### 3. Read References

Load only what the task needs:

- layout, hero composition, hierarchy, section rhythm ->
  `references/composition-playbook.md`
- motion, reveal choreography, stagger, scroll behavior ->
  `references/motion-recipes.md`
- redesigning an existing page or app -> `references/redesign-audit.md`
- media generation -> `references/asset-prompt-guide.md` first, then the
  currently supported toolchain docs; prefer the installed toolchain (e.g. `mmx-cli`)
- tooling trouble -> `references/troubleshooting.md`,
  `references/env-setup.md`

### 3.5. Acquire Context Before Freehanding

- Prefer code and design context over screenshots alone when both exist.
- When editing an existing product, inspect the visual vocabulary before making
  changes: hierarchy, spacing, color roles, radius, borders, shadows, motion,
  copy tone, and density.
- When the repo lacks enough context, explicitly anchor to one of:
  `design-md/`, a provided reference, or a written visual thesis.
- Treat full freehand invention as the last resort, not the default.

### 4. Build

- write responsive, accessible, production-ready UI
- integrate real copy, local assets, and intentional motion
- preserve the existing system when working inside a product
- redesign in place unless the user explicitly asks for a rebuild
- when the task is exploratory, keep variants easy to compare inside the same
  implementation path unless separation is clearly cleaner
- check `package.json` before introducing any new dependency
- do not mix Tailwind v3 and v4 syntax
- keep interactive or animation-heavy behavior inside the correct client
  boundary when using React or Next.js

### 5. Verify

- run quality gates before delivery

## DESIGN.md Consumption

Treat `design-md/` as the authoritative style library.

Each `DESIGN.md` may contain two layers:

1. YAML front matter for machine-readable tokens
2. Markdown body for rationale and application guidance

Each `DESIGN.md` typically covers these areas:

1. Visual Theme and Atmosphere
2. Color Palette and Roles (hex values with semantic names)
3. Typography Rules (families, sizes, weights, line-heights)
4. Component Stylings (buttons, cards, inputs with exact specs)
5. Layout Principles (spacing scale, grid, container)
6. Depth and Elevation (shadow system)
7. Do's and Don'ts (explicit design constraints)
8. Responsive Behavior (breakpoints and collapsing)
9. Agent Prompt Guide (reusable component prompts)

Extract and apply all relevant sections systematically, not just color and
typography.

When YAML exists:

- read tokens first for exact colors, typography, spacing, radius, and
  component defaults
- treat tokens as normative values
- use prose for tone, hierarchy, composition philosophy, and edge cases
- if prose and tokens conflict, follow tokens for exact values and prose for
  intent, then note the ambiguity

When the user does not specify a brand or style:

1. ask for direction if needed
2. recommend 2-3 anchors max
3. load the chosen `DESIGN.md`
4. extract the core token set if YAML exists
5. build against that anchor instead of freehanding the aesthetic

## Exploration Modes And Variations

Choose the working mode by the actual problem:

- purely visual direction work -> produce tightly scoped visual comparisons
  rather than a bloated full app shell
- interaction, flow, or concept exploration -> prefer a realistic clickable
  prototype or end-to-end implemented slice
- direct product implementation -> ship the chosen direction cleanly instead of
  over-optimizing for breadth

When the user wants options:

- vary 2-4 meaningful dimensions max: layout, typography, color treatment,
  motion language, or interaction model
- start with one direction that stays close to the existing product language,
  then expand into bolder alternatives
- make variants comparable; avoid creating unrelated designs with no shared
  evaluation frame
- if a single code path can support comparison cleanly, prefer toggles, props,
  or structured variants over fragmented duplicate files
- if a design needs multiple files, name them clearly and preserve the prior
  revision when making a major directional change

## Design Rules

### Typography

- Use distinctive display and body pairings.
- Avoid Inter, Arial, Roboto, and generic defaults unless the existing product
  already uses them.
- Match font personality to product tone.
- For dashboards and operational UI, avoid serif unless already established.
- Use monospace or tabular numerals for dense numbers and technical labels.

### Color And Surface

- Commit to one coherent palette with one accent color. See `craft/color.md` for palette structure, contrast min, and dark theme rules.
- Avoid pure `#000000`, purple-on-white AI gradients, and generic black shadows.
- Use CSS variables for token-driven consistency.

### Layout

- Prefer asymmetry, modular rhythm, or intentional negative space.
- If `DESIGN_VARIANCE > 4`, avoid centered hero compositions by default.
- Avoid the interchangeable centered hero plus three-card grid pattern.
- Treat the first viewport like a poster, not a document.
- Use sections, columns, dividers, lists, and media before defaulting to card
  grids.
- Use `min-h-[100dvh]` instead of `h-screen` for full-height hero sections.
- Collapse high-variance layouts aggressively to one column on mobile.

### Landing Pages

- Default flow: hero, support, detail, final CTA.
- Make the brand or product unmistakable in the first screen.
- Give the first viewport one dominant visual anchor.
- Avoid hero cards, logo clouds, stat strips, and floating fake dashboards by
  default.
- Keep the hero text column narrow and placed on a calm tonal area.

### Dashboards And Product UI

- Default to calm hierarchy, strong spacing, few colors, and minimal chrome.
- Organize around workspace, navigation, context, and one clear action accent.
- Prefer utility copy over marketing copy.
- If `VISUAL_DENSITY > 7`, prefer dividers, spacing, and alignment over
  generic cards.

### Copy And Imagery

- Write real copy. No lorem ipsum, fake brand names, generic people names, or
  empty hype language.
- Keep headlines concise and meaning-heavy.
- Make imagery do narrative work; decorative texture alone is not enough.
- Prefer real-looking, in-situ imagery over fake dashboards or abstract filler.
- Avoid emojis in UI copy, alt text, and interface chrome unless already part
  of the product language.
- If real assets are unavailable, use deliberate placeholders that make the
  intended structure obvious instead of low-credibility filler.

### Components

- Customize primitives so they belong to the chosen direction.
- Add loading, empty, error, hover, focus, and pressed states.
- Prefer visible labels above inputs.
- Aim for at least `44px` touch targets.

## Motion Rules

### Tool Choice

- CSS for simple hover, focus, and lightweight entrances
- Framer Motion for UI choreography and layout transitions
- GSAP for precise scroll sequencing only
- Three.js / React Three Fiber only when 3D materially improves the experience

### Guardrails

- Do not mix GSAP and Framer Motion in the same component tree.
- Animate `transform`, `opacity`, `filter`, and carefully chosen `clip-path`,
  not layout properties.
- Respect `prefers-reduced-motion`.
- Do not use React `useState` for magnetic hover or continuous motion.
- Keep perpetual or CPU-heavy animation in small leaf components.
- Keep `staggerChildren` parents and animated children in the same client tree.
- Use `IntersectionObserver`, `whileInView`, or scroll libraries instead of raw
  `window.addEventListener("scroll")`.
- Apply grain or noise overlays only to fixed, pointer-events-none layers.
- Clean up timers, scroll triggers, and effects.
- Remove ornamental motion with no hierarchy, affordance, or atmosphere value.

## Assets

Only generate media when it directly improves the frontend outcome.

Preferred execution path:

- use the currently installed, workspace-approved media generation toolchain
  first; `mmx-cli` is the preferred MiniMax path when available
- use the installed toolchain (e.g. `mmx-cli`); avoid script-based
  workflows that require separate environment setup

Asset rules:

- never ship placeholder media URLs
- save generated assets locally
- prefer WebP for images, compressed MP4 for video, normalized audio where
  relevant
- show prompts to the user before generation when the visual direction is
  sensitive
- keep commands reproducible and non-interactive when running generation in an
  agent workflow

## Output Integrity

- No placeholder comments such as `TODO`, `...`, or "same pattern".
- No skeleton output when full implementation is required.
- If the task asks for a full file or full component set, deliver the whole
  thing.
- If output must pause, stop at a clean breakpoint instead of compressing the
  rest into summaries.

## Prototype And Artifact Rules

Apply these when the deliverable is an HTML prototype, design study, or
standalone frontend artifact:

- choose a descriptive filename that reflects the screen or concept
- avoid giant monolithic files; split large artifacts into smaller components
  or support files when the structure starts hiding intent
- for major revisions, preserve the old version or make the variant boundary
  explicit so comparison is easy
- avoid fake title screens unless the user explicitly wants a presentation-like
  artifact
- keep the design centered on the interface itself, not decorative framing

## Escalation Rules

Pause and ask before:

- changing an established brand or design system in a major way
- adding motion or media that materially increases delivery risk
- shipping without responsive and accessibility validation

## Quality Gates

Before delivery, verify:

- responsive on mobile and desktop
- reduced-motion path handled
- loading, empty, and error states present when applicable
- no placeholder media URLs remain
- generated media saved locally
- heavy libraries justified and isolated
- code matches the intended aesthetic instead of a generic template
- first screen has one unmistakable visual anchor
- brand or product is unmistakable in the first screen
- each section has one job
- cards are used only when they earn their place
- no obvious filler, unfinished implementation, or generic slop remains
- when the UI is runnable, preview the implemented result rather than trusting
  static code inspection alone

### Anti-AI-Slop Checks

Run `craft/anti-ai-slop.md` as the quality gate before shipping. Covers:
indigo accent, trust gradients, emoji icons, wrong display fonts, AI
dashboard tiles, invented metrics, filler copy, and external placeholder CDNs.

## Final Output Contract

Every use of this skill should end with:

1. `Skill Fit`
2. `Primary Deliverable`
3. `Execution Evidence`
4. `Design System Alignment`
5. `Reference Evidence` - selected `design-md` anchor and any references loaded
6. `Risks / Open Questions`
7. `Next Action`

## References

Read only as needed:

- `references/composition-playbook.md`
- `references/motion-recipes.md`
- `references/redesign-audit.md`
- `references/troubleshooting.md`
- `references/asset-prompt-guide.md`
- `references/env-setup.md`

### Craft Rules

Brand-agnostic design craftsmanship. Read as needed during review:

- `craft/anti-ai-slop.md` — anti-AI-tell rules and quality gates
- `craft/color.md` — accent discipline, contrast, dark-theme rules
- `craft/typography-hierarchy.md` — hierarchy vectors, rhythm, controlled
  violations
- `craft/state-coverage.md` — loading, empty, error, edge, and form states
- `craft/accessibility-baseline.md` — WCAG 2.2 AA, ARIA, focus, labels
- `craft/laws-of-ux.md` — cognitive heuristics, decision-making, memory laws
