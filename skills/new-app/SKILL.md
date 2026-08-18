---
name: new-app
description: Use when the user wants to add one new application package, create a new app from official deployment docs, or asks for a new app implementation workflow. Trigger phrases: new app, create app package, add app, 新应用, 新增应用.
---

# New App

Create one new repository app package from official upstream deployment references.

This skill follows `docs/ai-sdlc/04-new-app-pipeline.md`, `docs/ai-sdlc/05-quality-gates.md`, and `docs/ai-sdlc/06-test-report-format.md`.

Supporting files in this skill:

- `checklist.md`
- `prompt-fragments.md`
- `report-template.md`

## Inputs

- app name (required)
- official site or docs (required)
- official image or compose reference (required)

## Steps

1. Load the libs CLI venv first: run `make install` if `.venv/` does not exist, then run `make --no-print-directory libs ARGS="list --include-archived --json"` (one-shot equivalent of `make cli` + `libs list`). Get the most complete app list (active + archived + internal). If `<app>` is in the list, stop immediately and report its key attributes (status, scope, cadence, update_policy). Then route: active/frozen → `app-update` skill; archived → `restore-app` skill (`libs restore`); or ask the user to provide a different app name / terminate. Do not create, modify, or overwrite anything.
2. Read the issue requirements and official upstream docs.
3. Read `template/` and repository rules from `docs/code_owner.md`.
4. Create the app under `apps/<app>/`.
5. Fill `.env`, `docker-compose.yml`, `variables.json`, `README.md`, and `src/`.
6. Register any new translatable env key in `i18n/translation.json`.
7. Run automated validation for structure, policy, deploy, and reachability.
8. Produce a short test report.
9. Recommend a maintenance cadence and update policy for the new app.

## Output

- created files
- upstream references
- automated validation result
- risks
- recommended cadence and update policy
- owner E2E focus

## Rules

- Existence is decided by `libs list --include-archived`, never by checking `apps/<app>/` alone; an archived or internal app also counts as existing.
- If `<app>` exists, stop at step 1, report its status/scope, and ask the user; never fall through to creation.
- Prefer official images or trusted upstream images.
- Keep the app aligned to repository conventions.
- Do not change unrelated apps.
- Produce the report in the same language the user used unless the user asks otherwise.
