# Prompt Fragments

## Braced Reference Rule

Whenever `.env` or `docker-compose.yml` is touched, convert **every** environment-variable reference in the whole file to the braced form `${VAR}`. Do not leave bare `$VAR` on old untouched lines of an edited file. Verify with a scan before handoff (for example `grep -nE '\$W9_[A-Z_]+'`). This overrides the urge to keep old lines as-is for cosmetic reasons; the braced conversion is part of a file-level edit, not unrelated churn.

## Minimal Change Rule

Update only what is required for the approved target version. Avoid unrelated cleanup, refactors, or speculative improvements.

## Validation Rule

Run the relevant quality gates for the changed app. Prefer app-local validation evidence over generic statements.

## Report Rule

Summarize:

- target version
- changed files
- automated checks
- risks
- owner E2E focus
