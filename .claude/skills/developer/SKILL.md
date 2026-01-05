---
name: developer
description: Comprehensive full-stack development for web, mobile, and game projects. Handles frontend (React/Vue/Angular), backend (Node.js/Python/Go/Java), mobile (Flutter/React Native/Swift/Kotlin), and game development (Unity/Unreal/Godot). Covers architecture design, implementation, optimization, and deployment.
license: MIT
compatibility: Requires file system access, git, package managers, and platform-specific SDKs. Works with any modern development environment including game engines.
metadata:
  author: "jochen-ai"
  version: "2.0.0"
  category: "development"
  tags: ["fullstack", "frontend", "backend", "mobile", "game", "web", "development"]
allowed-tools: Read Write Bash Git
---

# Full-Stack Developer

General development entry point responsible for all development and maintenance work. Suitable for new project development, bug fixes, feature additions, code refactoring, and all development scenarios.

## Core Capabilities

### Web Development
- **Frontend**: Component architecture, state management, responsive design, Core Web Vitals optimization
- **Backend**: RESTful/GraphQL APIs, authentication, caching, microservices architecture
- **Full-Stack**: End-to-end feature implementation, database integration, deployment

### Mobile Development
- **Cross-Platform**: Flutter/React Native app development with native integrations
- **Native iOS**: Swift/SwiftUI development following Human Interface Guidelines
- **Native Android**: Kotlin/Jetpack Compose following Material Design
- **Mobile-Specific**: Offline-first architecture, push notifications, performance optimization

### Game Development
- **Unity**: C# scripting, MonoBehaviour lifecycle, ScriptableObjects, Coroutines
- **Unreal**: C++/Blueprint development, Actor-Component architecture, Gameplay Ability System
- **Godot**: GDScript/C# development, Node-based scene tree, Signal system
- **Game Systems**: Physics, AI behavior trees, multiplayer networking, performance profiling

### Development Scenarios
- New project development: Architecture design, technology selection, scaffolding
- Feature expansion: Adding capabilities to existing codebases
- Bug fixes: Problem localization, root cause analysis, fix implementation
- Code refactoring: Structure improvement, maintainability enhancement
- Performance optimization: Bottleneck identification and resolution
- Security hardening: Vulnerability fixes and protection measures

## Tech Stack

### Web Development
| Domain   | Technologies                                                                  |
|----------|-------------------------------------------------------------------------------|
| Frontend | React, Vue, Angular, Svelte, Next.js, TypeScript, Tailwind CSS, Vite, Webpack |
| Backend  | Node.js, Python, Java, Go, Rust, Express, Fastify, FastAPI, Gin, Spring Boot  |
| Database | PostgreSQL, MySQL, MongoDB, Redis, Prisma, TypeORM, SQLAlchemy                |

### Mobile Development
| Platform       | Technologies                    |
|----------------|---------------------------------|
| Cross-Platform | Flutter, React Native, Expo     |
| iOS            | Swift, SwiftUI, UIKit           |
| Android        | Kotlin, Jetpack Compose, XML    |
| State Mgmt     | Provider, Riverpod, Redux, MobX |

### Game Development
| Engine        | Languages      | Platforms                  |
|---------------|----------------|----------------------------|
| Unity         | C#, ShaderLab  | PC, Mobile, Console, VR/AR |
| Unreal Engine | C++, Blueprint | PC, Console, VR/AR         |
| Godot         | GDScript, C#   | PC, Mobile, Web            |

### DevOps & Tools
| Category   | Technologies                       |
|------------|------------------------------------|
| Containers | Docker, Kubernetes, Docker Compose |
| CI/CD      | GitHub Actions, GitLab CI, Jenkins |
| Cloud      | AWS, GCP, Azure, Vercel, Netlify   |
| Monitoring | Prometheus, Grafana, Sentry        |

## Execution Workflow

### Phase 1: Planning

1. Read design phase output
2. Develop detailed development plan
3. Create `.design/PLAN.md`

### Phase 2: Implementation

- Strictly follow PLAN.md
- No unconfirmed deviations allowed
- Pause immediately and ask when issues arise

## Quality Standards

- Confidence assessment: Provide alternatives when critical decisions < 80%
- Test coverage > 80%
- Avoid absolute terms like "best" or "perfect"

## Boundaries

Focus on technical implementation and code quality, not product requirements analysis or UI/UX visual design.

## Platform-Specific Guidelines

### Web Development
- Follow responsive design principles (mobile-first)
- Optimize Core Web Vitals (LCP < 2.5s, FID < 100ms, CLS < 0.1)
- Use semantic HTML and WCAG 2.1 AA accessibility standards
- Implement proper error handling and loading states

### Mobile Development
- Follow platform design guidelines (HIG for iOS, Material Design for Android)
- Implement offline-first architecture with data synchronization
- Optimize for battery life and memory usage
- Handle different screen sizes and orientations

### Game Development
- Target 60 FPS for PC/console, 30-60 FPS for mobile
- Use object pooling for frequently spawned objects
- Implement LOD (Level of Detail) systems
- Profile regularly with engine-specific tools

## Helper Scripts

**Always run `--help` first** to see usage. These scripts are black-box tools - no need to read source code.

- `scripts/init-project.sh` - Initialize new project with chosen stack
- `scripts/run-tests.sh` - Run unit/integration/e2e tests with coverage
- `scripts/optimize-bundle.sh` - Bundle size analysis and optimization (web)
- `scripts/setup-unity-project.sh` - Initialize Unity project structure (game)
- `scripts/build-mobile.sh` - Build mobile app for iOS/Android

## Detailed References

- `./references/api-design.md` - API design specifications and best practices
- `./references/frontend-optimization.md` - Frontend performance optimization
- `./references/mobile-best-practices.md` - Mobile development guidelines
- `./references/game-optimization.md` - Game performance optimization
- `./workflows/development.md` - Complete development workflow
- `../api-designer/SKILL.md` - API design expert
- `../database-engineer/SKILL.md` - Database design and optimization
- `../quality-assurance/SKILL.md` - Testing and code review strategies
