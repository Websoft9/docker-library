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

1. Run `libs scan --app <app> --json` and use its output as the primary version fact source.
2. Run `libs drift --app <app> --json` and use its output as the primary dependency and drift fact source.
3. Read repository facts only when scan or drift outputs are missing required facts.
4. Classify the candidate as `patch`, `minor`, `major`, or `security`.
5. Read upstream release notes, changelog, or upgrade guide.
6. Check whether the candidate fits the app's update policy and cadence.
7. Assess breaking risk for compose, env keys, volumes, init flow, login flow, and data path.
8. Assess the database dependency when `libs drift` lists a DB engine image:
   - Read `W9_DB_VERSION` from `apps/<app>/.env` as the authoritative current DB version.
   - Read `metadata/db-lifecycle.json`; if the engine is missing or the snapshot is stale (older than 45 days), run `libs db-refresh` first.
   - Read the vendor-tested minimum from official release notes or docs, not from `externalDB`.
   - Compute candidates: alive tracks with version >= vendor minimum; LTS/stable preferred over innovation/short-term.
   - Judge the vendor-tested upper bound from release notes or docs; untested majors are not eligible.
   - If the current `W9_DB_VERSION` is EOL'd or a better LTS candidate exists, report a DB finding with recommendation and reason. It does not block the main version decision.
9. Decide one result: `auto-update`, `review-first`, `defer`, or `skip`.

## Output

A short assessment report:

- candidate version
- candidate class
- decision
- short rationale
- database finding (current, min, recommendation + reason, or `no change`)
- upstream references
- owner attention points

## Rules

- Assessment only. Do not edit any files. Exception: `libs db-refresh` may run to refresh the shared `metadata/db-lifecycle.json` fact snapshot.
- DB findings use two machine fact sources: `W9_DB_VERSION` in `.env` is the current version, and `db-lifecycle.json` is the engine lifecycle source. Vendor minimums come from official docs. `externalDB` is user-facing help text only and must not be used for computation.
- Never pick a DB major above the vendor-tested upper bound; prefer LTS over innovation.
- An EOL'd current DB version is a P1 finding; report it even when the app itself needs no update.
- `auto-update` means an implementation issue may start now.
- `review-first` means stop after assessment and wait for owner approval.
- `defer` means record the candidate and check again in the next cadence.
- `skip` means no update work should start for this candidate.
- Prefer `x.x` image tags. Use `x.x.x` only when upstream has no usable `x.x` tag or exact patch pinning is required (see `docs/devops-spec.md`).
- Report in the same language the user used.
- Use `report-template.md` when the user asks for a formal assessment report, or when the adapter layer explicitly requests formal output.
- If `libs drift` returns `not-declared` or `source-error`, AI may research missing upstream sources, but should not redo local dependency inventory already produced by CLI.
