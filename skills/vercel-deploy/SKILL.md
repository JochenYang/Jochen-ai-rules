---
name: vercel-deploy
description: Deploy projects to Vercel with one command. Use when user wants to deploy to Vercel, publish website, or needs production/preview deployment. Triggers on: "deploy to vercel", "vercel deploy", "发布到vercel", "部署到线上".
---

# Vercel Deploy Skill

Deploy current project to Vercel using Vercel CLI.

## Quick Start

1. Check if Vercel CLI is installed:
```bash
vercel --version
```

If not installed, prompt user to install:
```bash
npm i -g vercel
```

2. Check login status:
```bash
vercel whoami
```

If not logged in:
- Run `vercel login` - opens browser for OAuth login (no token needed)
- Or use VERCEL_TOKEN environment variable for CI/CD

3. Detect deployment mode:
- **Preview deployment** (default): `vercel`
- **Production deployment**: `vercel --prod`

## Deployment Workflow

### Step 1: Pre-deployment Check

1. Check project structure:
   - Look for `package.json`, `vercel.json`, `next.config.*`, `nuxt.config.*`
   - Detect framework automatically

2. Check for uncommitted changes:
   - Warn user about uncommitted changes
   - Suggest committing or using `--force`

### Step 2: Ask Deployment Mode

Prompt user to choose:
- **Preview** (default): For testing, creates preview URL
- **Production**: `vercel --prod`, creates production URL

### Step 3: Execute Deployment

Run the appropriate command:
```bash
# Preview deployment
vercel

# Production deployment
vercel --prod
```

### Step 4: Handle Result

1. **Success**: Display the deployment URL clearly
2. **Failure**: Parse error message, suggest fixes

## Common Issues

### Not logged in
```
Error: Not authenticated
```
Solution: Run `vercel login` - opens browser, click "Continue" to authenticate

### Project not linked
```
Error: No linked project
```
Solution: Run `vercel link` to link to a Vercel project

### Build failed
Check error output, common fixes:
- Check package.json scripts
- Verify build command in vercel.json
- Check environment variables

## Vercel Configuration

If user needs custom config, create `vercel.json`:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "nextjs"
}
```

## Output Format

Present deployment result:

```
✓ Deployed! 🎉

Production URL: https://your-project.vercel.app
Preview URL: https://your-project-xxx.vercel.app

To deploy updates, run: vercel --prod
```
