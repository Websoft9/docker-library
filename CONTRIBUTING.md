# Contributing

This repository uses an AI-first delivery model: owners decide demand and the final E2E result; AI handles research, implementation, validation, and reporting.

## Start here

- `AGENTS.md`
- `docs/vision.md`
- `docs/architecture.md`
- `docs/ai-sdlc/README.md`
- `skills/README.md`

## Workflow

1. Open an issue for one app or one coherent task.
2. The AI workflow starts automatically and uses the matching skill.
3. Review the AI pull request to `dev`; it links the issue and includes the latest test report.
4. The owner performs final E2E; `main` stays release-ready.

## Issue automation

Opening an issue starts the AI workflow for owners, members, collaborators, and contributors. A maintainer can create the `ai` label once in repository settings and add it to run the workflow on any other issue; adding other labels does not start a new run.

Configure the repository variable `OPENCODE_MODEL` and the matching provider secret (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, or `DEEPSEEK_API_KEY`). Set `OPENCODE_GITHUB_TOKEN` if AI pull requests must trigger CI.

Keep changes minimal and app-local, validate runnable behavior by deployment, and never commit secrets.
