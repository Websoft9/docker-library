---
name: update-assessment
description: Use when the user wants to assess whether an app is worth updating, check for a newer upstream version, or asks for an update decision before implementation. Trigger phrases: update assessment, assess update, 更新评估, 是否值得更新, check if <app> is worth updating.
---

# Update Assessment

Assess whether one repository app is worth updating, before any code change.

This skill implements `docs/ai-sdlc/10-update-assessment-workflow.md`.

Supporting files in this skill:

- `checklist.md`
- `facts-to-collect.md`
- `prompt-fragments.md`
- `report-template.md`

## Inputs

- app name (required)
- candidate version (optional, detected when missing)

## Steps

1. Read repository facts:
   - `apps/<app>/variables.json`
   - `apps/<app>/.env`
   - `apps/<app>/docker-compose.yml`
   - `metadata/maintenance.yaml`
   - `docs/ai-sdlc/02-maintenance-policy.md`
2. Detect the newest upstream candidate from `variables.json` `version_from` or the official release source.
3. Classify the candidate as `patch`, `minor`, `major`, or `security`.
4. Read upstream release notes, changelog, or upgrade guide.
5. Check whether the candidate fits the app's update policy and cadence.
6. Assess breaking risk for compose, env keys, volumes, init flow, login flow, and data path.
7. Decide one result: `auto-update`, `review-first`, `defer`, or `skip`.

## Output

A short assessment report:

- candidate version
- candidate class
- decision
- short rationale
- upstream references
- owner attention points

## Rules

- Assessment only. Do not edit any files.
- `auto-update` means an implementation issue may start now.
- `review-first` means stop after assessment and wait for owner approval.
- `defer` means record the candidate and check again in the next cadence.
- `skip` means no update work should start for this candidate.
- Prefer `x.x` image tags. Use `x.x.x` only when upstream has no usable `x.x` tag or exact patch pinning is required (see `docs/devops-spec.md`).
- Report in the same language the user used.
- Use `report-template.md` when the user asks for a formal assessment report, or when the adapter layer explicitly requests formal output.
