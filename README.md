# Test Codebase with Docs

  A trial project for AI-powered documentation updates.

  Every push to `main` triggers a GitHub Actions workflow that:
  1. Reads the git diff
  2. Calls GitHub Models (gpt-4o-mini) to update `/docs`
  3. Syncs `/docs` to the GitHub Wiki

  ## Structure

  - `src/` — application source code
  - `docs/` — documentation source (auto-updated by AI)
  - `.github/workflows/` — CI/CD pipelines

  ## Local setup

  ```bash
  git clone https://github.com/Lux-Via/Test-codebase-with-docs.git
  export GITHUB_TOKEN=your_pat_here   # or add to ~/.zprofile