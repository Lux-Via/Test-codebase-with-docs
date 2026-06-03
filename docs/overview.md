# Project Overview

This project is a trial codebase for testing AI-powered documentation updates.
Every push to `main` triggers a GitHub Actions workflow that reads the git diff,
calls an AI model, and updates these docs — then syncs them to the GitHub Wiki.

## Modules

- **calculator** — stateful `Calculator` class with operation history and scientific functions
- **inventory** — in-memory `Inventory` class with stock management, search, and low-stock alerts
- **AI Adoption** — new section added to the documentation, including styles and layout for AI adoption components.