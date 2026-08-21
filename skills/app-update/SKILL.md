---
name: app-update
description: Use when the user wants to implement an approved app update after assessment, update one app to a target version, adjust app files, run validation, and produce a short test report. Trigger phrases: update app, implement update, 升级应用, 更新应用, update <app> to <version>.
---

# App Update

Implement one approved app update with minimal app-local changes.

This skill follows `docs/ai-sdlc/03-update-pipeline.md`, `docs/ai-sdlc/05-quality-gates.md`, and `docs/ai-sdlc/06-test-report-format.md`.

Supporting files in this skill:

- `checklist.md`
- `prompt-fragments.md`
- `report-template.md`

## Inputs

- app name (required)
- target version (required unless already fixed by the issue or approved assessment)
- upstream references (required)

## Steps

1. Read repository facts from `apps/<app>/`, `metadata/maintenance.yaml`, and the app notes when relevant.
2. Read the approved assessment result, if one exists.
3. Read upstream release notes, upgrade notes, image tags, and requirements.
4. Update only the files required for the target version, typically `.env`, `docker-compose.yml`, `variables.json`, `README.md`, and `src/`.
5. Keep changes app-local unless the task explicitly requires cross-repo updates.
6. Apply the version tag policy from `docs/devops-spec.md`: prefer `x.x`, use `x.x.x` only when exact patch pinning is required.
7. If new translatable env keys are introduced, register them in `i18n/translation.json`.
8. Run the `deploy-validation` skill for the changed app.
9. Produce a short test report.

## Output

- files changed
- target version
- automated validation result
- risks
- owner E2E focus

## Rules

- Do not start implementation for a `review-first` candidate unless the owner has approved continuation.
- Keep the smallest correct change.
- Prefer official or trusted upstream images.
- Produce the report in the same language the user used unless the user asks otherwise.
- Use `report-template.md` when the user asks for a formal implementation report.
