# Test Codebase with Docs

Welcome to the project documentation.

This wiki is automatically maintained by an AI-powered GitHub Actions workflow.
Every push to `main` triggers a diff analysis and updates these pages.

## Pages

| Page | Description |
|---|---|
| [Overview](overview) | Project modules and purpose |
| [API Reference](api-reference) | All classes, methods, and parameters |
| [Changelog](changelog) | History of changes |

## How it works

```
git push to main
      ↓
GitHub Actions reads git diff
      ↓
Calls gpt-4o-mini via GitHub Models
      ↓
Updates /docs/*.md in the repo
      ↓
Syncs /docs/*.md to this Wiki
```
