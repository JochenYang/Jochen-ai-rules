# Variation Guidance

**IMPORTANT**: Each Three.js app should feel unique and context-appropriate.

## Vary by Scenario

| Scenario | Visual Style | Animation | Colors |
|----------|--------------|-----------|--------|
| **Portfolio/showcase** | Elegant, smooth | Subtle, refined | Muted, sophisticated |
| **Game/interactive** | Bold, dynamic | Snappy, responsive | Bright, contrasting |
| **Data visualization** | Clean, precise | Clear transitions | Systematic, readable |
| **Background effect** | Atmospheric | Slow, ambient | Dark, gradient |
| **Product viewer** | Realistic | Smooth orbit | PBR materials |

## Vary Visual Elements

### Geometry Choice
Not everything needs to be a cube. Explore:
- Spheres for organic, planetary themes
- Tori for rings, orbital paths
- Icosahedra for low-poly aesthetic
- Custom BufferGeometry for unique shapes

### Material Style
Mix and match:
- Flat shaded for low-poly look
- Glossy for polished surfaces
- Metallic for industrial/tech
- Wireframe for architectural feel

### Color Palettes
Consider:
- Complementary (opposite on color wheel)
- Analogous (adjacent on color wheel)
- Monochromatic (single hue variations)
- Triadic (three equidistant hues)

### Animation Style
Vary the motion character:
- Rotation: continuous spin vs. bounce vs. wobble
- Oscillation: smooth sine wave vs. elastic spring
- Wave motion: cascading vs. random
- Mouse tracking: subtle tilt vs. dramatic follow

---

## Avoid Converging On

These patterns are overused:

- Default green cube as first example every time
- Same camera angle (front-facing, z=5)
- Identical lighting setup (always directional light at 1,1,1)
- Purple-to-blue gradient backgrounds
- "Click to interact" prompts without clear affordance

Make each app feel purpose-built for its context.
