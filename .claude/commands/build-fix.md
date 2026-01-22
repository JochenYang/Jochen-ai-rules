---
description: Analyze and fix build errors. Run build, parse errors, and implement fixes.
---

# Build Fix Command

Analyze and fix build/compilation errors.

## Usage

```
/build-fix
/build-fix TypeScript type errors in auth module
/build-fix Fix the failing build in CI
```

## What This Does

1. **Run build command** - Execute the project's build script
2. **Parse errors** - Extract error messages and file locations
3. **Analyze root cause** - Understand why the build is failing
4. **Implement fixes** - Fix the identified issues
5. **Verify fix** - Run build again to confirm success

## Common Build Errors

| Error Type | Solution |
|------------|----------|
| TypeScript type errors | Add types or fix type mismatches |
| Import errors | Fix import paths or install dependencies |
| Missing dependencies | Run npm install / pnpm install |
| Linting errors | Fix linting issues or update eslint config |
| Circular dependencies | Refactor to break cycles |
| Missing exports | Add or fix exports |

## Workflow

```
1. Run: npm run build (or pnpm build)
2. Parse output for errors
3. Group errors by type/cause
4. Fix systematically (start with root causes)
5. Verify build succeeds
```

## Best Practices

- Fix root causes, not symptoms
- Fix multiple similar errors together
- Add tests to prevent regressions
- Commit fixes in logical batches
