# Prompt Fragments

## Access Rule

Missing access blocks validation and publishing. Preserve declaration completeness and review entries against the current default version/configuration.

Follow `docs/app-access-spec.md` and run `libs app-check --app <app> --gate access` for changed access port groups. Preserve group IDs, verify container listeners and report unknown/unverified facts. The deprecated `{"entries": [...]}` shape has no compatibility path beyond the migration window; migrate it to the port-group array and never reintroduce `W9_*_PORT_SET`, `W9_HTTP_PORT`, `W9_HTTPS_PORT`, `W9_URL`, `W9_URL_REPLACE` or `W9_ADMIN_PATH`. Metadata validity does not prove runtime reachability or domain binding.

## Braced Reference Rule

Whenever `.env` or `docker-compose.yml` is touched, convert **every** environment-variable reference in the whole file to the braced form `${VAR}`. Do not leave bare `$VAR` on old untouched lines of an edited file. Verify with a scan before handoff (for example `grep -nE '\$W9_[A-Z_]+'`). This overrides the urge to keep old lines as-is for cosmetic reasons; the braced conversion is part of a file-level edit, not unrelated churn.

## Minimal Change Rule

Update only what is required for the approved target version. Avoid unrelated cleanup, refactors, or speculative improvements.

## Validation Rule

Run the relevant quality gates for the changed app. Prefer app-local validation evidence over generic statements.

When database declarations are touched, use `docs/app-database-connection-spec.md` and run `libs app-check --app <app> --gate database-metadata`. Keep lifecycle checks separate. For declaration-only changes, report metadata evidence and do not claim a runtime deployment.

## Report Rule

Summarize:

- target version
- changed files
- automated checks
- risks
- owner E2E focus
