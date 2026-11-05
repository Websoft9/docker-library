# Restore App Checklist

- [ ] Verify the app is archived via `.venv/bin/libs list --include-archived --json` (`status: archived`)
- [ ] Confirm cadence and update policy with the user
- [ ] Preview with `.venv/bin/libs app-restore --app <app> --dry-run --json`
- [ ] Inspect `database_metadata` and migration `todo`; verify legacy sources against Compose and native inputs using `docs/app-database-connection-spec.md`, then pass the `database-metadata` gate before publishing
- [ ] Run `.venv/bin/libs app-restore --app <app>` to move back and update metadata
- [ ] Preview Contentful listing flags: `.venv/bin/libs catalog-update --app <app> --fields '{"appStore": true, "production": true}'`
- [ ] Hand `catalog-update --apply` to the owner
- [ ] Assess `W9_VERSION` staleness; route to `app-update` if outdated
- [ ] Run `.venv/bin/libs app-check --app <app>` and produce a short test report
- [ ] Recommend `release-readiness-check`; owner E2E decides
