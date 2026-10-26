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
3. Review the AI pull request to `main`; it links the issue and includes the latest test report. Use a Conventional Commits title such as `fix: ...`, `feat: ...`, or `ci: ...`.
4. The owner performs final E2E; release is a semver tag on `main`.

`main` is protected by the `main-protection` ruleset: PR-only, squash merges, linear history, and no force pushes or branch deletion.

## Issue automation

An issue starts the AI workflow only when it is opened and already has the `ai` label; both conditions are required. Adding `ai` later does not start Copilot. The assignment workflow uses `MAINTENANCE_STATE_TOKEN`; it must be a user PAT with `repo` scope that can assign Copilot.

For maintenance scan review, review the table and comment `/approve-updates app1, app2` with the exact apps to process. The workflow creates linked child issues deterministically and assigns Copilot to each approved child, so Copilot starts working immediately.

Keep changes minimal and app-local, validate runnable behavior by deployment, and never commit secrets.
