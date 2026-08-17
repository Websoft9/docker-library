# Contributing

This repository uses an AI-first delivery model.

Start here:
1. `AGENTS.md`
2. `docs/vision.md`
3. `docs/architecture.md`
4. `docs/ai-sdlc/README.md`
5. `docs/code_owner.md`

Core rules:
- issue is the work unit
- one app or one coherent task per issue
- owner decides demand and final E2E result
- AI does research, implementation, automated validation, and reporting

Contribution flows:
- app update: `docs/ai-sdlc/03-update-pipeline.md`
- new app: `docs/ai-sdlc/04-new-app-pipeline.md`
- quality gates: `docs/ai-sdlc/05-quality-gates.md`
- test report: `docs/ai-sdlc/06-test-report-format.md`

Branch rule:
- contributors submit PRs to `dev`
- `main` is release-ready only

PR rule:
- link the issue
- keep the PR focused
- include the latest AI test report
- owner performs final E2E before release
