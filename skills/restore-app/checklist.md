# Restore App Checklist

- [ ] Verify the app is archived via `libs list --include-archived --json` (`status: archived`)
- [ ] Confirm cadence and update policy with the user
- [ ] Preview with `libs restore --app <app> --dry-run --json`
- [ ] Run `libs restore --app <app>` to move back and update metadata
- [ ] Assess `W9_VERSION` staleness; route to `app-update` if outdated
- [ ] Run `libs check --app <app>` and produce a short test report
- [ ] Recommend `release-readiness-check`; owner E2E decides
