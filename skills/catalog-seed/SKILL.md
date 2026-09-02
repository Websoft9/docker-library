---
name: catalog-seed
description: Use when the user wants to create or update one app's repo commercial data file under metadata/catalog, choose catalog bindings, and preview the Contentful push. Trigger phrases: catalog data, 商业数据, catalog file, create catalog metadata, 更新商业文案.
---

# Catalog Authoring

Create or update one app's repo catalog file under `metadata/catalog/`.

This skill follows `docs/appstore-release-spec.md` and `docs/ai-sdlc/06-test-report-format.md`.

Supporting files in this skill:

- `checklist.md`
- `prompt-fragments.md`
- `report-template.md`

## Inputs

- app name (required)
- trademark (optional when it can be confirmed from `variables.json` or upstream docs)
- official docs or website (optional but preferred for better summary/description quality)

## Steps

1. Confirm `apps/<app>/variables.json` exists. If the app is missing, stop and route: new package work uses `new-app`, not this skill.
2. Read `metadata/templates/catalog.json`, `metadata/catalog.schema.json`, and `metadata/catalog-taxonomy.json` when category bindings are needed.
3. Read `apps/<app>/variables.json`, app README/Notes when useful, and the official website/docs when needed.
4. Create or update `metadata/catalog/<app>.json` with `trademark`, `summary`, `overview`, `description`, `websiteurl`, `screenshots`, and optional `catalogBindings`.
5. Keep category bindings in `catalogBindings` as `{ "parentKey": "...", "childKey": "..." }`, and choose only keys that exist in `metadata/catalog-taxonomy.json`.
6. Preview the result with `.venv/bin/libs catalog-push --app <app> --json`. Fix schema or taxonomy errors before handoff.
7. Produce a short report.

## Output

- catalog file path
- filled fields
- category bindings
- preview result
- owner review focus

## Rules

- This skill edits repo catalog data only; it does not apply writes to Contentful.
- Prefer concise, factual commercial writing over marketing fluff.
- Unless the user explicitly asks otherwise, write the repo catalog fields in English because the current Contentful write path targets `en-US`.
- Do not invent screenshots or website URLs; use verified upstream sources only.
- If category choice is ambiguous, use the fewest correct bindings and note the ambiguity in the report.
