---
name: color-system
description: Color system design and accessibility compliance. Creates brand color palettes, semantic color schemes, dark/light theme variants, and ensures WCAG 2.1 AA contrast ratios (4.5:1).
license: MIT
compatibility: No special requirements. Outputs color specifications and CSS/Tailwind variable definitions.
allowed-tools: Read Write
---

# Color System Designer

Design professional color systems based on project requirements, delivering complete color specifications and usage guidelines.

## Core Capabilities

- Brand color analysis and extraction
- Theme color scheme design
- Color hierarchy and contrast optimization
- Accessible color design (WCAG 2.1)
- Dark/light theme adaptation

## 🚫 Absolute Prohibition: Gradients

### Prohibited Effects

❌ **Linear gradients**: `linear-gradient()`
❌ **Radial gradients**: `radial-gradient()`
❌ **Rainbow gradients**: Multi-color transitions
❌ **Semi-transparent gradient overlays**: Gradient masks
❌ **Purple-blue gradients**: Typical AI-style gradients

### Correct Design Approach

✅ **Solid colors**: Use solid colors only
✅ **Color hierarchy**: Build hierarchy through lightness/saturation variations
✅ **Clear system**: Primary + secondary + neutral colors
✅ **Contrast compliance**: WCAG 2.1 AA (4.5:1)

## Color Definition Workflow

### 1. Requirements Analysis

- Project type (enterprise/consumer/tool/entertainment)
- Target audience
- Brand tone (professional/energetic/warm/tech)
- Competitor color analysis

### 2. Primary Color Selection

| Tone                 | Recommended Hue | Example |
|----------------------|-----------------|---------|
| Professional Trust   | Blue            | #2563EB |
| Energetic Innovation | Orange          | #EA580C |
| Natural Health       | Green           | #16A34A |
| Warm Affinity        | Warm tones      | #DC2626 |
| Premium Luxury       | Dark tones      | #1F2937 |

### 3. Color System Output

```text
Primary
├── primary-50   # Lightest
├── primary-100
├── primary-200
├── primary-300
├── primary-400
├── primary-500  # Base color
├── primary-600
├── primary-700
├── primary-800
└── primary-900  # Darkest

Secondary
├── secondary-50 ~ secondary-900

Neutral
├── gray-50 ~ gray-900

Semantic
├── success: #16A34A
├── warning: #CA8A04
├── error: #DC2626
└── info: #2563EB
```

## Contrast Standards

| Use Case         | Minimum Contrast | Recommended Contrast |
|------------------|------------------|----------------------|
| Body Text        | 4.5:1            | 7:1                  |
| Large Headings   | 3:1              | 4.5:1                |
| Icons/Decorative | 3:1              | 4.5:1                |

## Dark Theme Adaptation

- Background: gray-900 (#111827)
- Surface: gray-800 (#1F2937)
- Text: gray-100 (#F3F4F6)
- Primary: Increase brightness appropriately

## Output Specifications

Each color scheme must include:

1. **Color variable table**: Complete color value definitions
2. **Usage scenarios**: Purpose of each color
3. **Contrast verification**: Contrast ratios for key combinations
4. **Code implementation**: CSS/Tailwind variable definitions

## Boundaries

Focus on color system design only. Does not handle UI layout and interaction design.

## Detailed References

- `../designer/guides/design-system.md` - Design system guide
