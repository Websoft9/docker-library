---
name: release-readiness-check
description: Use when the user wants to know whether a task is ready for owner E2E, merge, or release, or asks for a final release gate summary. Trigger phrases: release readiness, ready to ship, 发布前检查, 是否可发布.
---

# Release Readiness Check

Assess whether one task is ready for owner E2E, merge, or release.

This skill follows `docs/ai-sdlc/05-quality-gates.md`, `docs/ai-sdlc/06-test-report-format.md`, and `docs/ai-sdlc/09-owner-e2e-runbook.md`.

Supporting files in this skill:

- `checklist.md`
- `report-template.md`

## Inputs

- app name or task scope (required)
- latest test report (required)
- latest issue or PR state (optional)

## Steps

1. Read the latest test report.
2. Check whether gates 0-3 are satisfied.
3. Identify any missing evidence.
4. Summarize owner E2E focus.
5. Output one readiness result.

## Output

- readiness: ready-for-e2e | blocked | not-enough-evidence
- blocking points
- owner focus

## Rules

- This is a gate review, not implementation.
- Do not mark ready when evidence is missing.
