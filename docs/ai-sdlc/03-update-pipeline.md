# Update Pipeline

Trigger:
- daily scheduled scan selects apps whose cadence interval has elapsed since their last successful upstream check
- scan progress is stored in the `MAINTENANCE_SCAN_STATE` repository variable, so scanning never creates repository commits

Steps:
1. Detect upstream version candidates.
2. Compare current version and target version.
3. Classify the candidate as `auto-update`, `review-first`, `defer`, or `skip`.
4. Create or update one issue per app.
5. AI researches upstream release notes and docs. Network probes use a 2s per-attempt budget with at most 2 retries; on local failure, fetch through the remote host's egress instead of extending timeouts.
6. AI edits `.env`, `docker-compose.yml`, `variables.json`, `README.md`, and `src/` when needed for the target version and for any app-local conformance fixes required by current repository rules. When `libs app-check --gate database` reports a bundled DB track as EOL, update it to a vendor-supported alive LTS track in the same update.
7. AI registers any new translatable env key in `i18n/translation.json`.
8. AI runs automated validation.
9. AI syncs the changed app to the test server's websoft9 store with `libs appstore-sync` when the container is reachable; skip within 10s when it is absent.
10. AI publishes the test report.
11. Owner runs final E2E.
12. Owner decides merge, release, defer, or reject.

Archive path:
- if owner decides to retire an app, move it to `archive/apps/`
- update `metadata/maintenance.yaml`
- update `metadata/archive.yaml`
- trigger Contentful metadata sync with `production=false`

Notes:
- Version detection does not change code by itself.
- Cadence intervals are fixed: `weekly` = 7 days, `monthly` = 30 days, `quarterly` = 90 days.
- Apps that were never checked are spread across the cycle with a deterministic hash slot, so the first run does not scan the whole library at once.
- Failed checks retry on the next run; an app is parked after 3 consecutive failures and stops consuming scan budget.
- `--limit` caps how many apps one run scans. Raised or missed runs are not replayed as extra scans.
- A missing or unreadable state value is a hard error, never "everything is due".
- The scan selector lives in `.github/workflows/maintenance-scan.yml`. Reading a variable needs no token, but updating it needs a PAT with repo scope (classic) or Variables read/write (fine-grained); the automatic `GITHUB_TOKEN` cannot write Actions variables. The workflow uses one PAT secret: `MAINTENANCE_STATE_TOKEN`.
- The current scheduled workflow performs detection only. Creating or updating one issue per app is a separate follow-up.
- `review-first` stops before implementation unless owner approves.
- Update work is not limited to version bumping; the changed app must satisfy the current quality gates before handoff.
- Update work should not trigger broad repository-wide template churn; only the minimum relevant app-local conformance fixes should be included.
- Failed automated validation keeps the issue open and blocks owner E2E.
