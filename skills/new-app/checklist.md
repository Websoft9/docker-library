# New App Checklist

- [ ] Validate the `new-app-request` block via `libs new-app --validate-issue` (when the task input comes from an issue)
- [ ] Load CLI venv (`make install` if `.venv/` missing), run `make --no-print-directory libs ARGS="list --include-archived --json"`
- [ ] If `<app>` is in the full list (active/archived/internal), report its status, scope, cadence, update_policy and stop (re-input name or terminate)
- [ ] Read official docs, image references, repository rules, and `metadata/templates/new-app/`
- [ ] After research resolves the real image and version, scaffold via `libs new-app --from-issue ... --version <x.x> --repo <image>` (or direct flags); it refuses duplicates and runs the quality gates
- [ ] Fill compose design, upstream metadata, DB version, and i18n keys beyond the skeleton
- [ ] Run `libs check --app <app>` and deploy/reachability validation
- [ ] Produce a short test report and recommend cadence/update policy
