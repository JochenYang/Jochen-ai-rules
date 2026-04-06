---
name: frontend-design
description: Implement distinctive, production-grade frontend UI code with strong visual direction, motion systems, local media asset generation, conversion-aware copy, and polished frontend execution. Use when building landing pages, marketing sites, product pages, dashboards, motion-heavy interfaces, or frontend experiences that need real assets and compelling copy.
---

# Frontend Design

Build distinctive, production-grade frontend interfaces with clear visual direction,
strong motion, real local assets, and conversion-aware content. Prefer
implementation over abstract strategy, but keep the final output cohesive,
performant, and ready to ship.

## Boundary With Other Skills

- Use `frontend-design` for implementation-first frontend work.
- Use `ui-ux-pro-max` only when the user explicitly wants a separate UX audit,
  design-system review, or style-direction critique before implementation.
- Use `developer` when the task expands into backend or broader full-stack
  architecture.
- Keep media generation tied to the frontend deliverable. Do not drift into
  unrelated art, video, or audio production unless the user explicitly asks.

## Boundaries

- Focus on implementation-first frontend delivery with strong visual direction.
- Do not absorb backend or broad product-planning work unless another skill explicitly takes over.
- Keep generated media, motion, and copy tied to the frontend deliverable.

## When NOT to Use

- Pure backend or API development → use `developer`
- Database design or schema work → use `database-engineer`
- Product planning or requirements analysis → use `product-manager` or `requirements-interview`
- Architecture design or system planning → use `dev-planner`
- Security auditing or vulnerability review → use `quality-assurance`

## When To Use

Use this skill when the user asks to:

- build a landing page, marketing site, dashboard, product page, or interactive
  app shell
- create polished React, Vue, HTML, CSS, or Tailwind frontend code
- add motion systems, scroll storytelling, or premium interaction details
- generate local image, video, or audio assets for the interface
- write conversion-aware UI copy, headings, and CTAs
- build visually distinctive frontend work that should not feel generic

## Working Style

Before coding, align on:

- **Purpose**: what the interface does and who it serves
- **Tone**: the specific visual direction to commit to
- **Constraints**: framework, design system, performance, accessibility
- **Differentiation**: the one memorable visual or interaction idea

Commit to a clear aesthetic direction before writing code. Bold maximalism and
refined minimalism both work when execution is intentional.

Before building, also write three anchors:

- **Visual thesis**: one sentence describing mood, material, and energy
- **Content plan**: hero, support, detail, final CTA
- **Interaction thesis**: two or three motion ideas that change the feel of the
  page

Each section should have one job, one dominant visual idea, and one primary
takeaway or action.

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
3. Choose a strong visual direction and motion intensity.

### 2. Plan Layout, Motion, And Assets Together

1. Break the UI into sections and reusable components.
2. Decide which sections need motion, which need static polish, and which need
   supporting media.
3. Prefer the smallest set of tools that can deliver the intended effect.

### 3. Verify Dependencies

- Check `package.json` before using a library.
- Do not mix Tailwind v3 and v4 syntax.
- For React or Next.js, isolate interactive behavior into client boundaries when
  needed.

### 4. Generate Local Assets When Needed

Only generate media when it directly supports the frontend outcome.

Rules:

- Never ship placeholder image or video URLs.
- Show prompts to the user before generation when prompts materially affect the
  result.
- Save assets locally in the target project.
- Prefer web-ready formats and compress before delivery.

### 5. Write Real Copy

- Do not use lorem ipsum or filler text.
- Write copy that matches the product, audience, and tone.
- Use AIDA, PAS, or FAB when helpful.

### 6. Implement The UI

- Build responsive, accessible, production-ready code.
- Integrate local assets, real copy, and intentional motion.
- Favor polish in spacing, states, and interaction details.

### 7. Run Quality Gates

- Validate responsive behavior.
- Validate reduced-motion handling.
- Validate loading, empty, and error states when applicable.
- Validate that media is local and dependencies are real.

## Design Rules

### Typography

- Prefer distinctive display and body pairings over default stacks.
- Avoid Inter, Arial, Roboto, and other generic defaults unless the existing
  product already uses them.
- Match font personality to the product tone instead of reaching for the same
  pairings every time.

### Color And Surfaces

- Commit to one coherent palette and use CSS variables for consistency.
- Avoid predictable purple-on-white gradients and washed-out startup palettes.
- Build atmosphere with layered backgrounds, textures, gradients, borders, or
  shadow systems that fit the concept.

### Layout

- Prefer asymmetry, modular rhythm, or intentional negative space.
- Avoid interchangeable centered-hero plus three-card-grid layouts unless the
  surrounding product already uses that pattern.
- Use grid, overlap, stacking, or sectional contrast to create hierarchy.
- Treat the first viewport like a poster, not a document.
- Default to cardless layouts for marketing and brand-led work. Use sections,
  columns, dividers, lists, and media blocks before reaching for card grids.
- Let each section carry one dominant idea instead of stacking many small UI
  devices into the same region.

### Landing Page Composition

- Default sequence: hero, support, detail, final CTA.
- Make the brand or product name the loudest text on branded pages.
- Use one dominant visual anchor in the first viewport.
- Prefer full-bleed or visually dominant heroes when the brief is brand-led.
- Avoid hero cards, stat strips, logo clouds, and floating dashboard props by
  default.
- Keep the hero text column narrow enough to scan quickly and place it on a
  calm area of the visual.
- If a sticky header consumes viewport height, budget for it in the hero.

### App And Dashboard Restraint

- Default to calm hierarchy, strong spacing, few colors, and minimal chrome.
- Organize product UI around workspace, navigation, secondary context, and one
  clear accent for action or state.
- Prefer utility copy over marketing copy for dashboards, admin tools, and
  operational surfaces.
- Avoid dashboard-card mosaics unless the card itself is the interaction model.

### Imagery And Copy

- Make imagery do narrative work; decorative texture alone is not enough.
- Prefer real-looking, in-situ imagery over fake dashboards or abstract filler.
- Ensure imagery has a stable tonal area for text and tap targets.
- Keep headlines concise, let them carry the meaning, and trim repetition
  aggressively.
- For product surfaces, prioritize orientation, status, and action over mood or
  campaign language.

### Components

- Customize shadcn-style primitives or base components so they belong to the
  chosen direction.
- Add meaningful loading, empty, error, hover, focus, and pressed states.
- Do not stop at the happy path.

## Motion Rules

### Tool Selection

- Use CSS for simple hover, focus, and lightweight entrance effects.
- Use Framer Motion for UI transitions and layout choreography.
- Use GSAP only when scroll sequencing or precise timeline control is needed.
- Use Three.js or React Three Fiber only when 3D materially improves the
  experience.

### Guardrails

- Do not mix GSAP and Framer Motion in the same component.
- Animate GPU-friendly properties such as `transform`, `opacity`, `filter`, and
  carefully chosen `clip-path`.
- Respect `prefers-reduced-motion`.
- Lazy-load heavy libraries and isolate perpetual motion in small leaf
  components.
- Disable expensive parallax or 3D effects on coarse pointers or weak devices.
- For visually led work, ship two or three intentional motions: one entrance
  sequence, one scroll-linked or depth effect, and one hover or reveal that
  sharpens affordance.
- Remove motion that is ornamental only; motion should improve hierarchy,
  atmosphere, or affordance in a quick recording.

Read these when needed:

- `references/motion-recipes.md`
- `references/composition-playbook.md`
- `references/troubleshooting.md`

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

Read these when needed:

- `references/asset-prompt-guide.md`
- `references/minimax-cli-reference.md`
- `references/minimax-image-guide.md`
- `references/minimax-video-guide.md`
- `references/minimax-tts-guide.md`
- `references/minimax-music-guide.md`
- `references/minimax-voice-catalog.md`
- `references/env-setup.md`

## Escalation Rules

Pause and ask the owner before:

- changing established brand or design-system direction in a major way
- introducing asset generation or motion choices that materially increase delivery risk
- shipping frontend work without responsive and accessibility validation

## Final Output Contract (MANDATORY)

Every use of this skill should end with:

1. `Skill Fit` - why implementation-first frontend design is the right path
2. `Primary Deliverable` - page, component set, or asset-backed frontend output
3. `Execution Evidence` - files changed, preview/build steps, and validation completed
4. `Risks / Open Questions` - responsiveness, performance, or polish concerns
5. `Next Action` - the next implementation or review step

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

## References

Read only as needed:

- `references/composition-playbook.md`
- `references/motion-recipes.md`
- `references/troubleshooting.md`
- `references/asset-prompt-guide.md`
- `references/minimax-cli-reference.md`
- `references/minimax-image-guide.md`
- `references/minimax-video-guide.md`
- `references/minimax-tts-guide.md`
- `references/minimax-music-guide.md`
- `references/minimax-voice-catalog.md`
- `references/env-setup.md`
