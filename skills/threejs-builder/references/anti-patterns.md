# Anti-Patterns to Avoid

## Basic Setup Mistakes

### Not importing OrbitControls from correct path
**Why bad**: Controls won't load, `THREE.OrbitControls` is undefined in modern Three.js

**Better**: Use `import { OrbitControls } from 'three/addons/controls/OrbitControls.js'` or unpkg examples/jsm path

### Forgetting to add object to scene
**Why bad**: Object won't render, silent failure

**Better**: Always call `scene.add(object)` after creating meshes/lights

### Using old `requestAnimationFrame` pattern instead of `setAnimationLoop`
**Why bad**: More verbose, doesn't handle XR/WebXR automatically

**Better**: `renderer.setAnimationLoop((time) => { ... })`

---

## Performance Issues

### Creating new geometries in animation loop
**Why bad**: Massive memory allocation, frame rate collapse

**Better**: Create geometry once, reuse it. Transform only position/rotation/scale

### Using too many segments on primitives
**Why bad**: Unnecessary vertices, GPU overhead

**Better**: Default segments are usually fine. `SphereGeometry(1, 32, 16)` not `SphereGeometry(1, 128, 64)`

### Not setting pixelRatio cap
**Why bad**: 4K/5K displays run at full resolution, poor performance

**Better**: `Math.min(window.devicePixelRatio, 2)`

---

## Code Organization

### Everything in one giant function
**Why bad**: Hard to modify, hard to debug

**Better**: Separate setup into functions: `createScene()`, `createLights()`, `createMeshes()`

### Hardcoding all values
**Why bad**: Difficult to tweak and experiment

**Better**: Define constants at top: `const CONFIG = { color: 0x00ff88, speed: 0.001 }`
