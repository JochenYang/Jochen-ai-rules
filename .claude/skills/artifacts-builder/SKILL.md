---
name: artifacts-builder
description: Rapid prototyping tool for React interactive demos and single-file HTML artifacts. Uses shadcn/ui component library with 40+ components. Perfect for product demos, design validation, and shareable browser previews.
license: MIT
compatibility: Requires Node.js 18+, npm/yarn. Uses React 18, Vite, Tailwind CSS, and Parcel for bundling.
metadata:
  author: "jochen-ai"
  version: "1.0.0"
  category: "prototyping"
  tags: ["react", "prototype", "demo", "shadcn", "artifacts"]
allowed-tools: Read Write Bash
---

# Frontend Prototype Builder

Rapidly build shareable interactive prototypes for demos and product validation.

## Core Capabilities

- React + TypeScript interactive prototypes
- 40+ shadcn/ui components ready to use
- Single-file HTML bundling for sharing
- Direct browser preview

## Tech Stack

- **Framework**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS + shadcn/ui
- **Bundling**: Parcel + html-inline

## Executable Tools

The following scripts can be run directly without reading source code:

- `scripts/init-artifact.sh` - Initialize project structure
- `scripts/bundle-artifact.sh` - Bundle into single-file HTML

## Design Guidelines

**No "AI Style" Design**:

- No gradient backgrounds
- Avoid excessive center alignment
- Avoid pure white large rounded corners
- Avoid default Inter font
- Use solid colors and clear color hierarchy

## Boundaries

Focus on interactive prototype building, not production code. For complete applications, use developer skill.

## Detailed References

- `workflows/artifact-building.md` - Complete building workflow
- `guides/quick-start.md` - Quick start guide
