# AGENTS

Use this file as the fast entry point for AI agents working in this repository.

## Repo Summary

`docker-library` is a library of 300+ Docker Compose application packages under `apps/`.
Each app is independent and should be runnable with `docker compose up`.

## Start Here

Read in this order:
1. `docs/vision.md`
2. `docs/architecture.md`
3. `docs/code_owner.md`
4. `docs/ai-sdlc/README.md`
5. `docs/upstream-spec.md`
6. `.github/copilot-instructions.md`

## Core Rules

- Treat each `apps/<app>` directory as one deployable unit.
- Keep changes minimal and app-local unless the task is explicitly cross-cutting.
- Prefer official images or trusted upstream images.
- If `docker-compose.yml` references `./src/...`, the file must exist.
- Follow env conventions, especially `W9_URL`, `W9_URL_REPLACE`, `W9_LOGIN_USER`, and `W9_LOGIN_PASSWORD`.
- Validate by deployment when the task changes runnable behavior.

## i18n

- Translatable env keys are `W9_*_SET` and `W9_LOGIN*`.
- When a task adds or changes such keys, ensure `i18n/translation.json` gets the key.
- New keys may stay `["", ""]`; translations are filled by humans, not AI.
- Do not edit downstream repos; the `i18n.yml` workflow syncs them by PR.

## Delivery Model

- Issue is the work unit.
- AI does research, implementation, and routine validation.
- Owner only decides demand and final E2E result.
- Use the quality gates in `docs/ai-sdlc/05-quality-gates.md`.

## Main Paths

- Apps: `apps/`
- App metadata: `metadata/maintenance.yaml`, `metadata/archive.yaml`
- Shared skills: `skills/`
- Template: `template/`
- Scripts: `build/`
- Process docs: `docs/ai-sdlc/`
- CI: `.github/workflows/`

## Testing

- Run `make test`; suites live in `cli/tests`, `tests/build`, `tests/skills`
- Test contract: `docs/test.md`
- Manual walkthrough: `docs/runbook.md`

## When Updating Apps

- Check upstream version and release notes first.
- Classify the candidate using `docs/ai-sdlc/02-maintenance-policy.md`.
- Update only what is required for the target version.
- Produce a short test report using `docs/ai-sdlc/06-test-report-format.md`.
