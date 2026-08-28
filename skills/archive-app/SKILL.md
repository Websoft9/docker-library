---
name: archive-app
description: Use when the user wants to retire one app or a small batch of apps, move apps out of active maintenance, or asks for an archive workflow with Contentful handoff. Trigger phrases: archive app, retire app, 下架应用, 归档应用.
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
5. Set Contentful retirement flags: for each archived app, preview `make libs ARGS="contentful-update --app <app> --fields '{\"appStore\": false, \"production\": false}'"` and hand the `--apply` run to the owner.
6. Produce a short archive report.

## Output

- archived apps
- archive reason
- metadata changes
- Contentful handoff status

## Rules

- Default to one app per issue.
- Small batch archive is allowed only when reason and handling are identical.
- Do not delete app history.
- To bring an archived app back, use the `restore-app` skill, not this one.
- Contentful updates use the `contentful_management` Python SDK (installed by `make install`). AI previews `contentful-update`; only the owner runs it with `--apply`.
- Contentful retirement flags for archive are `appStore` and `production`, both set to `false`.
