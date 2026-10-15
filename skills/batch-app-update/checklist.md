# Batch App Update Checklist

- [ ] Confirm the batch scope is approved for implementation
- [ ] Resolve the selector into a concrete app list from `apps/`
- [ ] If initials or mixed selectors were used, show the resolved app list before editing
- [ ] Deduplicate and alphabetize the final app list
- [ ] Choose the failure policy: `continue` or `stop-on-first-failure`
- [ ] Choose the smallest safe concurrency for this batch
- [ ] Run a short feasibility screen before deep work on each app
- [ ] Skip quickly when the app appears to require inference from an official `install.sh` and the expected runtime is more than 5 containers without a clear official Compose spec
- [ ] Check whether any target apps are likely to touch shared files such as `i18n/translation.json` or repository metadata
- [ ] Run each app as an independent `app-update` unit
- [ ] Keep changes app-local for each app
- [ ] Do not run remote deploy validation concurrently unless capacity and isolation are confirmed
- [ ] After each app passes automated validation, run `.venv/bin/libs appstore-sync --app <app>`
- [ ] Do not run `appstore-sync` concurrently on a shared remote target unless isolation is confirmed
- [ ] Record per-app target version, changed files, validation result, appstore sync result, risks, and owner E2E focus
- [ ] Record skip evidence for any `skipped-complex-install` app
- [ ] Separate environment failures from app defects in the final summary
- [ ] Produce one explicit batch summary with per-app outcomes
