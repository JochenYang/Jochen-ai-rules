---
name: phaser-build
description: Build 2D HTML5 games for the web using Phaser with WebGL/Canvas rendering. Use when creating Phaser game scaffolds, scenes, core loops, or deployment guidance for web-based releases.
---

# Phaser Builder

Focused skill for building Phaser-based 2D web games and guidance aligned with Phaser's web-first design.

## What Phaser Is

- HTML5 game framework for **2D** games in web browsers
- Uses **WebGL** and **Canvas** rendering across desktop and mobile web
- Supports **JavaScript** and **TypeScript** development
- Works with many frontend frameworks and can be bundled for web delivery
- Complete API reference available for Phaser 3.87.0

## Best Fit Scenarios

- 2D games targeting browsers on desktop and mobile
- Lightweight web playable builds (including embed-friendly environments)
- Rapid prototyping and production-grade 2D releases on the web

## Not a Fit When

- You need full **3D** rendering or 3D physics built-in
- You must publish on modern consoles like PS5, Xbox, or Switch
- You require a **no-code** editor-only workflow

## Core Capabilities

- Game scaffolding and scene lifecycle setup
- Input handling, physics, sprites, and 2D animations
- Performance-aware rendering and asset loading strategies
- Web-oriented packaging and deployment guidance

## API Surface Map

### Core Runtime
- **Phaser.Game**: Bootstraps renderer, global systems, and main loop
- **Phaser.Scene**: Primary unit of gameplay logic and lifecycle
- **Scene Plugins**: Loader, Input, Cameras, Tween Manager, Time, Physics

### Assets & Loading
- **Loader Plugin**: Preload images, spritesheets, audio, tilemaps, atlases
- **Cache Manager**: Shared asset caching across scenes

### Display & Cameras
- **Game Objects**: Sprites, Images, Text, Graphics, Containers
- **Cameras**: Scene-level camera manager for view control and effects

### Input & Interaction
- **Input Plugin**: Keyboard, pointer, gamepad input per scene
- **Event Emitter**: Scene events for lifecycle and custom hooks

### Physics
- **Arcade Physics**: Lightweight built-in physics per scene
- **Matter Physics**: Optional physics system when configured

### Animation & Time
- **Animation Manager**: Global animation definitions shared across scenes
- **Tween Manager**: Scene-level tweens for property animation
- **Time / Clock**: Timers, delayed calls, and time scaling

### Audio
- **Sound Manager**: Global audio system for music and sfx

## Scene Lifecycle

- **init**: Prepare state and read scene config
- **preload**: Load assets using the Loader Plugin
- **create**: Build objects, input, and systems
- **update**: Frame loop for gameplay logic

## Global vs Scene Systems

- Global: Renderer, Animation Manager, Cache, Registry, Sound, Scene Manager
- Scene-local: Input, Tweens, Cameras, Loader, Physics

## Development Guidance

- Prefer web-first design and browser performance constraints
- Use JavaScript or TypeScript only
- Keep architecture modular: scenes, systems, and reusable game objects
- Use Scene plugins instead of reaching into Game-level systems

## Boundaries

Focus on Phaser 2D web games. Do not recommend Phaser for 3D-first or console-native releases.
