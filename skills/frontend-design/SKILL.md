---
name: frontend-design
description: Implement distinctive, production-grade frontend UI code with strong visual direction, motion systems, local media asset generation, conversion-aware copy, and polished frontend execution. Use when building landing pages, marketing sites, product pages, dashboards, motion-heavy interfaces, or frontend experiences that need real assets and compelling copy.
---

# Frontend Design

Build distinctive, production-grade frontend interfaces with clear visual
direction, strong motion, real local assets, and conversion-aware content.
Prefer implementation over abstract strategy, but keep the result cohesive,
performant, and ready to ship.

## Boundary With Other Skills

- Use `frontend-design` for implementation-first frontend work.
- Use `ui-ux-pro-max` only when the user explicitly wants a separate UX audit,
  design-system review, or style-direction critique before implementation.
- Use `developer` when the task expands into backend or broader full-stack
  architecture.
- Keep media generation tied to the frontend deliverable. Do not drift into
  unrelated art, video, or audio production unless the user explicitly asks.

## When NOT to Use

- Pure backend or API development -> use `developer`
- Database design or schema work -> use `database-engineer`
- Product planning or requirements analysis -> use `product-manager` or
  `requirements-interview`
- Architecture design or system planning -> use `dev-planner`
- Security auditing or vulnerability review -> use `quality-assurance`

## When To Use

Use this skill when the user asks to:

- build a landing page, marketing site, dashboard, product page, or
  interactive app shell
- create polished React, Vue, HTML, CSS, or Tailwind frontend code
- add motion systems, scroll storytelling, or premium interaction details
- generate local image, video, or audio assets for the interface
- write conversion-aware UI copy, headings, and CTAs
- upgrade an existing frontend that looks generic, unfinished, or visually weak
- build visually distinctive frontend work that should not feel generic

## Working Model

Before coding, align on:

- **Purpose**: what the interface does and who it serves
- **Tone**: the visual direction to commit to
- **Constraints**: framework, design system, performance, accessibility
- **Differentiation**: the one memorable visual or interaction idea

Before building, write three anchors:

- **Visual thesis**: one sentence describing mood, material, and energy
- **Content plan**: hero, support, detail, final CTA
- **Interaction thesis**: two or three motion ideas that change the feel of
  the page

Each section should have one job, one dominant visual idea, and one primary
takeaway or action.

### Design Controls

Use these three internal dials to keep output intentional instead of generic:

- **DESIGN_VARIANCE**: layout boldness and asymmetry
  - `1-3`: restrained, symmetrical, predictable
  - `4-7`: offset, structured, moderately experimental
  - `8-10`: aggressive asymmetry, broken grids, strong spatial contrast
- **MOTION_INTENSITY**: how animated the interface feels
  - `1-3`: hover, focus, and pressed states only
  - `4-7`: entrance reveals, stagger, restrained choreography
  - `8-10`: scroll-linked sequencing, magnetic motion, cinematic behavior
- **VISUAL_DENSITY**: how much content fits in the viewport
  - `1-3`: airy, premium, gallery-like
  - `4-7`: balanced daily-use product UI
  - `8-10`: dense dashboards, telemetry, operational surfaces

Default baseline:

- `DESIGN_VARIANCE = 6`
- `MOTION_INTENSITY = 4`
- `VISUAL_DENSITY = 4`

Always adapt the dials to the user request, existing product language, and
screen type.

## Direction And Anchoring

If the user request does not clearly specify a direction, do not guess the
style too early.

- If missing information would materially change the implementation, you MUST
  ask exactly one focused clarification question before proceeding.
- Treat these as clarification triggers: missing reference anchor, unclear
  interface type, unclear motion intensity, unclear device priority, or unknown
  requirement to preserve an existing brand or design system.
- Use `AskUserQuestion` when the visual direction, reference style, or
  interaction ambition is still unclear. If the host runtime exposes the tool
  as `askuserquestion`, treat it as the same tool. If no such tool is
  available, ask the same question in plain text.
- Prefer one focused question at a time.
- Prefer multiple-choice framing when possible.
- Skip clarification only when the repo already has a strong established design
  system, the user explicitly says to choose the direction, or the missing
  detail would not meaningfully change the implementation.
- If you choose not to ask, state the assumption you made before implementing.

When clarifying visual direction, prioritize this order:

1. **Reference anchor** - a brand or product from `design-md/` or another
   explicit reference
2. **Mood and tone** - calm, bold, premium, playful, technical, editorial
3. **Interface type** - landing page, dashboard, docs site, app shell, promo
   page
4. **Constraints** - light or dark preference, motion intensity,
   accessibility, device priority

Recommended question patterns:

- "Which direction should we anchor to: a specific brand in `design-md/`, a
  mood adjective, or should I propose 2-3 options?"
- "Do you want this to feel more editorial, product-polished, experimental, or
  operational?"
- "Should motion stay subtle, medium, or high-impact?"
- "Is there an existing brand or design system I must preserve?"

## Core Principles

- Avoid generic AI aesthetics, especially default font stacks, timid palettes,
  and interchangeable layouts.
- Use expressive typography and a deliberate visual hierarchy.
- Prefer asymmetry, rhythm, overlap, layering, or controlled density over flat
  boilerplate composition.
- Match implementation complexity to the intended visual direction.
- Preserve the existing design language when working inside an established
  product or design system.
- Ship real working code, not mockup-only markup.

## Workflow

### 1. Align The Request

1. Identify page type, audience, and technical constraints.
2. Confirm framework and styling stack from the repo before importing
   dependencies.
3. If any key design input is ambiguous enough to change implementation
   meaningfully, ask exactly one focused clarification question before
   designing. Do not invent a direction just to get moving.
4. If the user specifies a brand or style, immediately load
   `design-md/<brand>/DESIGN.md` and treat it as authoritative.
5. If the user does not specify a brand or style, gather a reference anchor or
   mood, then map it to the closest `design-md/` folder when possible.
6. If no `design-md/` reference fits, summarize the confirmed style as a short
   visual thesis before implementation.
7. When offering options, recommend 2-3 concrete directions max.

### 2. Plan Layout, Motion, And Assets Together

1. Break the UI into sections and reusable components.
2. Decide which sections need motion, which need static polish, and which need
   supporting media.
3. Set the three design controls before implementation.
4. Prefer the smallest set of tools that can deliver the intended effect.

### 3. Verify Dependencies And Runtime Constraints

- Check `package.json` before using any new library.
- Do not mix Tailwind v3 and v4 syntax.
- For React or Next.js, isolate interactive behavior into client boundaries
  when needed.
- In RSC environments, keep global state and animation-heavy code inside client
  components only.
- Prefer `@phosphor-icons/react` or `@radix-ui/react-icons` when the project
  already supports them. Otherwise preserve the existing icon system.

### 4. Route To References

Do not load every reference file by default. Read only what the task needs.

- **Layout, hero composition, section rhythm, or visual hierarchy**: read
  `references/composition-playbook.md`
- **Motion, reveal choreography, stagger, or animation sequencing**: read
  `references/motion-recipes.md`
- **Existing page or app redesign work**: read `references/redesign-audit.md`
- **Image, video, audio, or voice generation**: read
  `references/asset-prompt-guide.md` first, then the relevant minimax guide
- **Tooling trouble or local environment issues**: read
  `references/troubleshooting.md` and `references/env-setup.md`

Asset-specific routing:

- images -> `references/minimax-image-guide.md`
- video -> `references/minimax-video-guide.md`
- TTS / spoken voice -> `references/minimax-tts-guide.md` and
  `references/minimax-voice-catalog.md`
- music -> `references/minimax-music-guide.md`
- CLI flags or invocation details -> `references/minimax-cli-reference.md`

### 5. Implement The UI

- Build responsive, accessible, production-ready code.
- Integrate local assets, real copy, and intentional motion.
- Favor polish in spacing, hierarchy, states, and interaction details.
- When redesigning an existing surface, upgrade in place instead of rewriting
  from scratch unless the user explicitly asks for a rebuild.

### 6. Run Quality Gates

- Run the checks in `Quality Gates` before delivery.

## Design Rules

### Typography

- Prefer distinctive display and body pairings over default stacks.
- Avoid Inter, Arial, Roboto, and other generic defaults unless the existing
  product already uses them.
- Match font personality to the product tone instead of reaching for the same
  pairings every time.
- For dashboards and operational surfaces, avoid serif typography unless the
  established product language already uses it.
- For dense data views, use monospace or tabular numerals for numbers.

### Color And Surfaces

- Commit to one coherent palette and use CSS variables for consistency.
- Prefer one accent color by default.
- Avoid predictable purple-on-white gradients and washed-out startup palettes.
- Avoid pure `#000000`; use tinted dark neutrals or off-black instead.
- Build atmosphere with layered backgrounds, textures, gradients, borders, or
  shadow systems that fit the concept.
- Tint shadows to the surrounding palette when possible instead of relying on
  generic black shadow presets.

### Layout

- Prefer asymmetry, modular rhythm, or intentional negative space.
- If `DESIGN_VARIANCE > 4`, avoid centered hero compositions by default.
- Avoid interchangeable centered-hero plus three-card-grid layouts unless the
  surrounding product already uses that pattern.
- Use grid, overlap, stacking, or sectional contrast to create hierarchy.
- Treat the first viewport like a poster, not a document.
- Default to cardless layouts for marketing and brand-led work. Use sections,
  columns, dividers, lists, and media blocks before reaching for card grids.
- Let each section carry one dominant idea instead of stacking many small UI
  devices into the same region.
- Use `min-h-[100dvh]` instead of `h-screen` for full-height hero sections.
- On mobile, high-variance layouts must collapse aggressively to a single
  column with no horizontal scroll.

### Landing Page Composition

- Default sequence: hero, support, detail, final CTA.
- Make the brand or product name the loudest text on branded pages.
- Use one dominant visual anchor in the first viewport.
- Prefer full-bleed or visually dominant heroes when the brief is brand-led.
- Avoid hero cards, stat strips, logo clouds, and floating dashboard props by
  default.
- Keep the hero text column narrow enough to scan quickly and place it on a
  calm tonal area of the visual.
- If a sticky header consumes viewport height, budget for it in the hero.

### App And Dashboard Restraint

- Default to calm hierarchy, strong spacing, few colors, and minimal chrome.
- Organize product UI around workspace, navigation, secondary context, and one
  clear accent for action or state.
- Prefer utility copy over marketing copy for dashboards, admin tools, and
  operational surfaces.
- If `VISUAL_DENSITY > 7`, prefer dividers, spacing, and alignment over
  generic cards.
- Avoid dashboard-card mosaics unless the card itself is the interaction model.

### Imagery And Copy

- Make imagery do narrative work; decorative texture alone is not enough.
- Prefer real-looking, in-situ imagery over fake dashboards or abstract filler.
- Ensure imagery has a stable tonal area for text and tap targets.
- Keep headlines concise, let them carry the meaning, and trim repetition
  aggressively.
- Do not use lorem ipsum, placeholder brands, generic people names, or empty
  hype language.
- Avoid emojis in UI copy, alt text, and interface chrome unless the existing
  product deliberately uses them.

### Components

- Customize shadcn-style primitives or base components so they belong to the
  chosen direction.
- Add meaningful loading, empty, error, hover, focus, and pressed states.
- Prefer visible labels above inputs for forms.
- Aim for minimum `44px` touch targets on interactive controls.
- Do not stop at the happy path.

## Motion Rules

### Tool Selection

- Use CSS for simple hover, focus, and lightweight entrance effects.
- Use Framer Motion for UI transitions and layout choreography.
- Use GSAP only when scroll sequencing or precise timeline control is needed.
- Use Three.js or React Three Fiber only when 3D materially improves the
  experience.

### Guardrails

- Do not mix GSAP and Framer Motion in the same component tree.
- Animate GPU-friendly properties such as `transform`, `opacity`, `filter`,
  and carefully chosen `clip-path`.
- Respect `prefers-reduced-motion`.
- Never drive magnetic hover or continuous micro-motion with React `useState`;
  use motion values or library-native animation state instead.
- Keep perpetual or CPU-heavy animation in small leaf components.
- For `staggerChildren`, keep the parent motion wrapper and animated children
  in the same client component tree.
- Use `IntersectionObserver`, `whileInView`, or scroll libraries instead of raw
  `window.addEventListener("scroll")` for reveal logic.
- Apply noise or grain overlays only to fixed, pointer-events-none layers, not
  scrolling containers.
- Clean up timers, scroll triggers, and effects in `useEffect`.
- Disable expensive parallax or 3D effects on coarse pointers or weak devices.
- For visually led work, ship two or three intentional motions: one entrance
  sequence, one scroll-linked or depth effect, and one hover or reveal that
  sharpens affordance.
- Remove motion that is ornamental only; motion should improve hierarchy,
  atmosphere, or affordance in a quick recording.

For motion work, follow `Route To References` before reading support files.

## Asset Generation

Use local generation only when the frontend needs real supporting media.

Available scripts:

- `scripts/minimax_image.py`
- `scripts/minimax_video.py`
- `scripts/minimax_tts.py`
- `scripts/minimax_music.py`

Asset workflow:

1. Parse the needed asset type, quantity, format, and placement.
2. Craft a concrete prompt with composition, lighting, tone, and usage.
3. Confirm prompts with the user before generation when visual direction is
   sensitive.
4. Save generated files under the target project's asset directory.
5. Prefer WebP for images, compressed MP4 for video, and normalized audio when
   possible.

For asset work, follow `Route To References` before reading support files.

## Copywriting

Write real product copy that supports the interface.

- Use AIDA for landing pages and narrative marketing sections.
- Use PAS for pain-driven hooks and problem framing.
- Use FAB for feature explanation and benefit-oriented detail.
- Use concrete CTA language that tells the user what they get.

Good copy is concise, specific, and visually integrated with the layout. Avoid
generic hype and empty slogans.

## Generative And Visual Frontend

When the request includes generative or art-led presentation:

- use `templates/viewer.html` as the base for interactive visual output
- use `templates/generator_template.js` as the starting pattern
- use `canvas-fonts/` when curated local typography helps the visual result
- prefer deterministic seeded behavior when reproducibility matters

Keep artistic exploration in service of the frontend outcome unless the user
explicitly asks for standalone visual art.

## Output Integrity

- Do not ship placeholder comments such as `TODO`, `...`, "rest of code", or
  "same pattern".
- Do not replace required implementation with a skeleton plus explanation.
- If the task requires a full file or full component set, deliver the whole
  thing.
- When output size becomes a limit, stop at a clean breakpoint and make the
  continuation explicit instead of compressing the rest into summaries.

## Escalation Rules

Pause and ask the owner before:

- changing an established brand or design-system direction in a major way
- introducing asset generation or motion choices that materially increase
  delivery risk
- shipping frontend work without responsive and accessibility validation

## Quality Gates

Before delivering:

- responsive on mobile and desktop
- reduced-motion path is handled
- loading, empty, and error states exist when applicable
- no placeholder media URLs remain
- generated media is saved locally
- heavy libraries are justified and isolated
- code matches the intended aesthetic rather than a generic template
- the first screen has one unmistakable visual anchor
- the brand or product is unmistakable in the first screen
- each section has one job and cards are used only when they earn their place
- no obvious placeholder comments, fake filler, or unfinished implementation
  remain

## Final Output Contract (MANDATORY)

Every use of this skill should end with:

1. `Skill Fit` - why implementation-first frontend design is the right path
2. `Primary Deliverable` - page, component set, or asset-backed frontend output
3. `Execution Evidence` - files changed, preview or build steps, and validation
   completed
4. `Design System Alignment` - when using `design-md/`, confirm which Do's and
   Don'ts were followed and any intentional deviations
5. `Risks / Open Questions` - responsiveness, performance, or polish concerns
6. `Next Action` - the next implementation or review step

## Design System Reference Library

When the user specifies a target style, or selects one after clarification,
use the `design-md/` folder as an authoritative reference.

Each design system follows a 9-section structure:

1. **Visual Theme & Atmosphere** - mood, material, energy
2. **Color Palette & Roles** - hex values with semantic names
3. **Typography Rules** - font families, sizes, weights, line-heights
4. **Component Stylings** - buttons, cards, inputs with exact specs
5. **Layout Principles** - spacing scale, grid, container
6. **Depth & Elevation** - shadow system with values
7. **Do's and Don'ts** - explicit design constraints
8. **Responsive Behavior** - breakpoints and collapsing strategy
9. **Agent Prompt Guide** - reusable component prompts

When the user does not specify a brand or style:

1. Ask for a direction before coding.
2. Recommend 2-3 relevant anchors from `design-md/` based on page type and
   product tone.
3. Load the chosen `DESIGN.md`.
4. Implement against that anchor instead of freehanding the aesthetic.

## References

Read only as needed:

- `references/composition-playbook.md`
- `references/motion-recipes.md`
- `references/redesign-audit.md`
- `references/troubleshooting.md`
- `references/asset-prompt-guide.md`
- `references/minimax-cli-reference.md`
- `references/minimax-image-guide.md`
- `references/minimax-video-guide.md`
- `references/minimax-tts-guide.md`
- `references/minimax-music-guide.md`
- `references/minimax-voice-catalog.md`
- `references/env-setup.md`
