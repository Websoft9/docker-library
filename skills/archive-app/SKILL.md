---
name: archive-app
description: Use when the user wants to retire one app or a small batch of apps, move apps out of active maintenance, asks for an archive workflow with Contentful handoff, or permanently delete an archived app. Trigger phrases: archive app, retire app, delete app, 下架应用, 归档应用, 删除应用.
---

# Archive App

Retire one app or a small batch of apps from active maintenance.

This skill follows `docs/ai-sdlc/03-update-pipeline.md`, `docs/ai-sdlc/07-issue-contracts.md`, and `docs/ai-sdlc/09-owner-e2e-runbook.md`.

Supporting files in this skill:

- `checklist.md`
- `prompt-fragments.md`
- `report-template.md`

## Inputs

- app name or app list (required)
- archive reason (required)

## Steps

1. Confirm the archive reason and whether the batch shares the same decision.
2. Move each target app from `apps/` to `archive/apps/`.
3. Update `metadata/maintenance.yaml` if needed.
4. Update `metadata/archive.yaml`.
5. Set Contentful retirement flags: for each archived app, preview `.venv/bin/libs catalog-update --app <app> --fields '{"appStore": false, "production": false}'` and include the exact owner `--apply` command in the report.
6. Produce a short archive report.

## Permanent delete

If the issue explicitly requests permanent deletion, do not move the app to archive:

1. Remove `archive/apps/<app>`.
2. Remove the app from `metadata/archive.yaml`.
3. Remove it from `archive/apps/ARCHIVED.md` when present.
4. Do not delete Contentful entries or rewrite Git history unless the issue explicitly asks.

## Output

- archived apps
- archive reason
- metadata changes
- Contentful handoff status, including the exact owner `--apply` command

## Rules

- Default to one app per issue.
- Small batch archive is allowed only when reason and handling are identical.
- Archive is the default. Permanent deletion is an explicit exception: follow the delete scope in the issue, default to removing app files and archive metadata, and never rewrite Git history unless explicitly requested.
- To bring an archived app back, use the `restore-app` skill, not this one.
- Contentful updates use the `contentful_management` Python SDK (installed by `make install`). AI previews `catalog-update`; only the owner runs it with `--apply`.
- Contentful retirement flags for archive are `appStore` and `production`, both set to `false`.
