---
name: developer
description: Full-stack development skill for new projects, bug fixes, feature additions, and code refactoring. Handles frontend, backend, database, and testing tasks across React, Vue, Node.js, Python, Java, Go, and mobile platforms.
license: MIT
compatibility: Requires file system access, git, and package managers (npm/pip/cargo/etc). Works with any modern development environment.
allowed-tools: Read Write Bash Git
---

# Full-Stack Developer

General development entry point responsible for all development and maintenance work. Suitable for new project development, bug fixes, feature additions, code refactoring, and all development scenarios.

## Core Capabilities

### Development Scenarios

- New project development: System architecture design, technology selection, building from scratch
- Feature expansion: Adding new features on existing codebase
- Code implementation: Frontend/backend/full-stack code writing

### Maintenance Scenarios

- Bug fixes: Problem localization, root cause analysis, fix implementation, verification
- Code refactoring: Improving code structure, enhancing maintainability, eliminating technical debt
- Performance optimization: Performance bottleneck analysis and optimization implementation
- Security hardening: Security vulnerability fixes and protection measures implementation

### General Capabilities

- Database design and API development
- Unit testing and integration testing
- Code review issue resolution

## Tech Stack

| Domain   | Technologies                                             |
|----------|----------------------------------------------------------|
| Frontend | React, Vue, Angular, Next.js, TypeScript, Tailwind CSS   |
| Backend  | Node.js, Python, Java, Go, Express, FastAPI, Spring Boot |
| Database | PostgreSQL, MySQL, MongoDB, Redis                        |
| Mobile   | React Native, Flutter, Swift, Kotlin                     |
| Gaming   | Unity, Unreal Engine, Godot, C#                          |
| DevOps   | Docker, Kubernetes, GitHub Actions, AWS, Vercel          |

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

## Helper Scripts

**Always run `--help` first** to see usage. These scripts are black-box tools - no need to read source code.

- `scripts/init-project.sh` - Initialize new project with chosen stack
- `scripts/run-tests.sh` - Run unit/integration/e2e tests with coverage

## Detailed References

- `./references/api-design.md` - API design specifications and best practices
- `./workflows/development.md` - Complete development workflow
- `../api-designer/SKILL.md` - API design expert
- `../test-engineer/SKILL.md` - Testing strategies
