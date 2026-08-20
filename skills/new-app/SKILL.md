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
- trademark (required)
- official references (required): at least one of `docs.github`, `docs.image`, `docs.install`

## Steps

1. If the task input contains a `new-app-request` yaml block (issue), validate it first with `make --no-print-directory libs ARGS="new-app --validate-issue <file|-> --json"`. On failure, stop and report the errors; do not research until the request is valid.
2. Load the libs CLI venv first: run `make install` if `.venv/` does not exist, then run `make --no-print-directory libs ARGS="list --include-archived --json"` (one-shot equivalent of `make cli` + `libs list`). Get the most complete app list (active + archived + internal). If `<app>` is in the list, stop immediately and report its key attributes (status, scope, cadence, update_policy). Then route: active/frozen → `app-update` skill; archived → `restore-app` skill (`libs restore`); or ask the user to provide a different app name / terminate. Do not create, modify, or overwrite anything.
3. Read the issue requirements and official upstream docs.
4. Read repository rules from `docs/code_owner.md` and the machine template under `metadata/templates/new-app/`.
5. After research determines the real image and version, scaffold the package skeleton with `make --no-print-directory libs ARGS="new-app --from-issue <file|-> --version <x.x> --repo <image> --json"` (or direct flags when there is no issue block). The command refuses duplicates and runs the quality gates automatically.
6. Fill `.env`, `docker-compose.yml`, `variables.json`, `README.md`, and `src/` beyond the skeleton, following the todo list returned by the scaffold command.
7. Register any new translatable env key in `i18n/translation.json`.
8. Run automated validation for structure, policy, deploy, and reachability.
9. Produce a short test report.
10. Recommend a maintenance cadence and update policy for the new app.

## Output

- created files
- upstream references
- automated validation result
- risks
- recommended cadence and update policy
- owner E2E focus

## Rules

- Existence is decided by `libs list --include-archived`, never by checking `apps/<app>/` alone; an archived or internal app also counts as existing.
- If `<app>` exists, stop at step 2, report its status/scope, and ask the user; never fall through to creation.
- The request block schema is `metadata/new-app.schema.json`; validate through `libs new-app --validate-issue`, never by hand.
- The CLI scaffold reads `metadata/templates/new-app/`; `template/` stays as a human reference and must not be treated as the machine template source.
- Prefer official images or trusted upstream images.
- Keep the app aligned to repository conventions.
- Do not change unrelated apps.
- Produce the report in the same language the user used unless the user asks otherwise.
