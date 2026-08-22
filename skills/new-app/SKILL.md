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
- official references (required): at least one URL for the project repository, image registry, or install docs

If any required input is missing, stop and ask the user for it before researching or scaffolding. Never guess the trademark and never research without at least one official reference URL.

## Steps

1. Load the libs CLI venv first: run `make install` if `.venv/` does not exist, then run `make --no-print-directory libs ARGS="list --include-archived --json"`. Get the most complete app list (active + archived + internal). If `<app>` is in the list, stop immediately and report its key attributes (status, scope, cadence, update_policy). Then route: active/frozen → `app-update` skill; archived → `restore-app` skill (`libs restore`); or ask the user to provide a different app name / terminate. Do not create, modify, or overwrite anything.
2. Read the issue requirements and official upstream docs.
3. Read repository rules from `docs/code_owner.md` and the machine template under `metadata/templates/new-app/`.
4. Research the real image and version from upstream sources.
5. Scaffold the package skeleton with `make --no-print-directory libs ARGS="new-app --name <app> --trademark <brand> --json"` plus `--version <x.x>` and `--repo <image>` when the research has already resolved them (otherwise the CLI writes explicit TODO placeholders). The command refuses duplicates and runs the quality gates automatically.
6. Fill `.env`, `docker-compose.yml`, `variables.json`, `README.md`, and `src/` beyond the skeleton, following the todo list returned by the scaffold command. Decide the env groups from research: enable the password group (uncomment and fill) when the app has a DB or login; enable the web group when it exposes a web page; delete groups the app does not need.
7. Register any new translatable env key in `i18n/translation.json`.
8. Run the `deploy-validation` skill to prove the app deploys.
9. Produce a short test report.
10. Assign a maintenance cadence and update policy: write the app into the matching buckets of `metadata/maintenance.yaml` (apps not listed inherit the monthly/patch-minor defaults), and state the assignment in the report. The owner reviews it at merge.
11. Draft the Contentful marketing fields from the upstream research: copy `metadata/templates/contentful-draft.json` to `metadata/contentful-drafts/<app>.json` and fill trademark, summary, overview, description, websiteurl, and screenshots. The owner reviews the draft before the first Contentful write; AI never writes Contentful directly. The owner applies with `libs contentful-create --app <app> --apply` after review.

## Output

- created files
- upstream references
- automated validation result
- risks
- assigned cadence and update policy
- owner E2E focus

## Rules

- Existence is decided by `libs list --include-archived`, never by checking `apps/<app>/` alone; an archived or internal app also counts as existing.
- If `<app>` exists, stop at step 1, report its status/scope, and ask the user; never fall through to creation.
- The CLI input contract is `metadata/new-app.schema.json`; the issue itself is prose, AI converts it to flags.
- The CLI scaffold reads `metadata/templates/new-app/`; `template/` stays as a human reference and must not be treated as the machine template source.
- Prefer official images or trusted upstream images.
- Keep the app aligned to repository conventions.
- Do not change unrelated apps.
- Produce the report in the same language the user used unless the user asks otherwise.
