# Composition Playbook

Use this reference when the task depends on art direction, hierarchy,
restraint, imagery, and motion more than raw component count. This is
especially useful for landing pages, brand sites, editorial experiences,
high-polish product demos, and visually led prototypes.

## Core Stance

- Start with composition, not components.
- Treat the first viewport like a poster, not a document.
- Default to one big visual idea, sparse copy, and disciplined spacing.
- Use sections, media blocks, columns, dividers, and lists before introducing
  cards.
- Keep the system tight: two typefaces max and one accent color by default.

## Working Model

Before building, write:

- visual thesis: one sentence describing mood, material, and energy
- content plan: hero, support, detail, final CTA
- interaction thesis: two or three motion ideas that change the feel of the
  page

Each section gets one job, one dominant visual idea, and one primary takeaway
or action.

## Landing Pages

Default sequence:

1. Hero: brand or product, promise, CTA, and one dominant visual
2. Support: one concrete feature, offer, or proof point
3. Detail: atmosphere, workflow, product depth, or story
4. Final CTA: convert, start, visit, or contact

Hero rules:

- One composition only.
- Use a full-bleed image or dominant visual plane when the page is brand-led.
- On full-bleed heroes, do not inherit a shared page gutter or framed shell;
  constrain the inner text and action column only.
- Brand first, headline second, body third, CTA fourth.
- Avoid hero cards, logo clouds, stat strips, pill soup, and floating fake
  dashboards by default.
- Keep headlines short enough to understand in one glance.
- Keep the text column narrow and place it on a calm tonal area.
- Ensure contrast and tap targets remain strong over imagery.

Litmus:

- If the first viewport still works after removing the image, the image is too
  weak.
- If the brand disappears after hiding the nav, the hierarchy is too weak.

Viewport budgeting:

- Sticky or fixed headers count against the first screen.
- If using `100vh` or `100svh`, subtract persistent chrome or overlay the
  header rather than stacking it in normal flow.

## Apps And Product UI

Default to restraint:

- calm surface hierarchy
- strong typography and spacing
- few colors
- dense but readable information
- minimal chrome
- cards only when the card is the interaction

Organize around:

- primary workspace
- navigation
- secondary context or inspector
- one clear accent for action or state

Avoid:

- dashboard-card mosaics
- thick borders around every region
- decorative gradients behind routine product UI
- multiple competing accent colors
- ornamental icons that do not improve scanning

If a panel can become plain layout without losing meaning, remove the card.

## Imagery

Imagery must do narrative work.

- Use at least one strong, real-looking image for brands, venues, editorial
  pages, and lifestyle products.
- Prefer in-situ photography over abstract gradients or fake 3D filler.
- Crop or choose images with a stable tonal area for text.
- Avoid imagery with signage, logos, or typographic clutter competing with the
  interface.
- Do not generate images with built-in UI frames, splits, cards, or panels.
- If multiple moments are needed, use multiple images instead of one collage.

The first viewport needs a real visual anchor. Decorative texture is not
enough.

## Copy

- Write in product language, not design commentary.
- Let the headline carry the meaning.
- Supporting copy should usually be one short sentence.
- Cut repetition between sections.
- Do not leak prompt language or design commentary into the UI.
- Give every section one responsibility: explain, prove, deepen, or convert.

If deleting 30 percent of the copy improves the page, keep deleting.

## Utility Copy For Product UI

For dashboards, admin tools, or operational workspaces:

- prioritize orientation, status, and action over promise or mood
- start with the working surface itself, not a marketing hero
- use headings that describe the area or action directly
- keep supporting text focused on scope, freshness, behavior, or decision value

Good examples:

- `Selected KPIs`
- `Plan status`
- `Search metrics`
- `Top segments`
- `Last sync`

Avoid homepage-style slogans and campaign language on product surfaces unless
explicitly requested.

Litmus:

- If an operator scans only headings, labels, and numbers, can they understand
  the page immediately?

## Motion

Use motion to create presence and hierarchy, not noise.

For visually led work, aim for two or three intentional motions:

- one entrance sequence in the hero
- one scroll-linked, sticky, or depth effect
- one hover, reveal, or layout transition that sharpens affordance

Prefer motion that is:

- noticeable in a quick recording
- smooth on mobile
- fast and restrained
- consistent across the page
- removed when ornamental only

## Failure Modes To Reject

- generic SaaS card grid as the first impression
- beautiful image with weak brand presence
- strong headline with no clear action
- busy imagery behind text
- sections repeating the same mood statement
- carousel with no narrative purpose
- app UI made of stacked cards instead of layout

## Final Litmus Checks

- Is the brand or product unmistakable in the first screen?
- Is there one strong visual anchor?
- Can the page be understood by scanning headlines only?
- Does each section have one job?
- Are cards actually necessary?
- Does motion improve hierarchy or atmosphere?
- Would the design still feel premium if all decorative shadows were removed?
