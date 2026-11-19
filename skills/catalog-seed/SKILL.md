---
name: catalog-seed
description: Use when the user wants to pull, create or update one app's local catalog working copy under metadata/.catalog, choose catalog bindings, and push it to Contentful. Trigger phrases: catalog data, 商业数据, catalog file, create catalog metadata, 更新商业文案.
---

# Catalog Authoring

Create or update one app's local catalog working copy under `metadata/.catalog/`.

Contentful is the catalog source of truth. `metadata/.catalog/` is a gitignored local working copy used to seed a missing entry or to push deliberate content changes; it is never committed and no CI job reads it.

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
4. Pull the current Contentful state first: `.venv/bin/libs catalog-pull --app <app> --json`. This needs `CONTENTFUL_GRAPHQL_TOKEN` in the environment or `.secrets/contentful.env`; use `--from artifact` only when the published snapshot is enough. When the app already has an entry, edit the pulled values; use `metadata/templates/catalog.json` only for an app with no entry yet.
5. Create or update `metadata/.catalog/<app>.json` with `trademark`, `summary`, `overview`, `description`, `websiteurl`, `screenshots`, and optional `catalogBindings`. Keep `summary` and `overview` within the Field Length Limits below.
6. Keep category bindings in `catalogBindings` as `{ "parentKey": "...", "childKey": "..." }`, and choose only keys that exist in `metadata/catalog-taxonomy.json`.
7. Preview the result with `.venv/bin/libs catalog-push --app <app> --json`. Fix schema or taxonomy errors before handoff.
8. Produce a short report.

## Field Length Limits

- `summary`: at most 8 words; prefer 5 words or fewer.
- `overview`: at most 30 words; prefer 20 words or fewer.
- `description`: no hard limit; keep it factual and concise.

Count the words before writing. Aim for the preferred length; use the maximum only when the shorter form would drop essential meaning.

## Output

- catalog working copy path (`metadata/.catalog/<app>.json`)
- filled fields
- category bindings
- preview result
- owner action: first seed (`--apply`) or deliberate content replacement (`--apply --overwrite`)
- owner review focus

## Contentful write rules

Contentful is authoritative. `metadata/.catalog/` is a gitignored local working copy: never commit it.

| Situation | Command |
|---|---|
| Entry does not exist yet (baseline seed) | `libs catalog-push --app <app> --apply` |
| Entry exists, only version/resources/flags changed | `libs catalog-push --app <app> --apply` (machine fields only) |
| Deliberately replace content in Contentful | `libs catalog-push --app <app> --apply --overwrite` |
| Read the latest Contentful content back | `libs catalog-pull --app <app> --apply` (live) or `--from artifact` for the published snapshot |

| App state | `app_store` | `production` |
|---|---|---|
| Active public app, ready for release | `true` | `true` |
| Active public app, dev only (`release=false`) | `true` | `false` |
| Internal (`scope=internal`) | `false` | `false` |
| Archived | `false` | `false` |

`production` follows `variables.json.release`. `app_store` is derived from the app being active and public; do not add it to `metadata/.catalog/<app>.json`. Contentful's field ID is `app_store`; GraphQL exposes it as `appStore`.

## Rules

- This skill edits the local working copy only; it never writes Contentful itself. Only the owner runs `--apply`.
- Pull before editing. The working copy is seed data: after the first write Contentful is authoritative, and later pushes must not overwrite content unless the owner explicitly passes `--overwrite`.
- Never commit `metadata/.catalog/`; it is gitignored and shared state lives in Contentful.
- Prefer concise, factual commercial writing over marketing fluff.
- Enforce the Field Length Limits: `summary` ≤ 8 words (prefer ≤ 5), `overview` ≤ 30 words (prefer ≤ 20).
- Unless the user explicitly asks otherwise, write the repo catalog fields in English because the current Contentful write path targets `en-US`.
- Do not invent screenshots or website URLs; use verified upstream sources only.
- If category choice is ambiguous, use the fewest correct bindings and note the ambiguity in the report.
