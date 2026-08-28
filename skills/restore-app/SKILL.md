---
name: restore-app
description: Use when the user wants to bring one archived app back to active maintenance, re-enable an archived app, or asks for a restore workflow. Trigger phrases: restore app, unarchive app, bring back app, 恢复应用, 重新上架.
---

# Restore App

Restore one archived app back to active maintenance. This is the inverse of the `archive-app` skill.

This skill follows `docs/ai-sdlc/03-update-pipeline.md`, `docs/ai-sdlc/05-quality-gates.md`, and `docs/ai-sdlc/06-test-report-format.md`.

Supporting files in this skill:

- `checklist.md`
- `prompt-fragments.md`
- `report-template.md`

## Inputs

- app name (required)
- cadence (optional, default monthly)
- update policy (optional, default patch-minor)

## Steps

1. Confirm the app is archived: run `make install` if `.venv/` does not exist, then `make --no-print-directory libs ARGS="list --include-archived --json"`. The app must appear with `status: archived`. If it is active or missing, stop and route: active → `app-update` skill; missing → `new-app` skill.
2. Confirm cadence and update policy with the user (defaults: monthly / patch-minor).
3. Preview with `make --no-print-directory libs ARGS="restore --app <app> --cadence <c> --update-policy <p> --dry-run --json"` and show the actions.
4. Run the real restore with the same command without `--dry-run`.
5. Restore Contentful listing flags: for the restored app, preview `make libs ARGS="contentful-update --app <app> --fields '{\"appStore\": true, \"production\": true}'"` and hand the `--apply` run to the owner.
6. Run a stale-version assessment: check `W9_VERSION` in `apps/<app>/.env` against the upstream image; if outdated, hand over to the `app-update` skill.
7. Run the `deploy-validation` skill and produce a short test report.
8. Recommend running `release-readiness-check` before publishing; owner E2E decides.

## Output

- restored app
- cadence and update policy assigned
- metadata changes
- Contentful handoff status
- stale-version assessment result
- owner E2E focus

## Rules

- Restore only apps that exist in `archive/apps/`; never overwrite an existing active app.
- Restore is not release: a stale version must go through `app-update` before publish.
- One app per issue unless the batch shares the same cadence and policy.
- Do not delete app history.
- Contentful updates use the `contentful_management` Python SDK (installed by `make install`). AI previews `contentful-update`; only the owner runs it with `--apply`.
- Contentful listing flags for restore are `appStore` and `production`, both set to `true`.
