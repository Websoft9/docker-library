# Update Pipeline

Trigger:
- scheduled scan runs every Monday and Thursday at 10:00 China Standard Time and selects apps whose cadence interval has elapsed since their last successful upstream check
- scan progress is stored in the `MAINTENANCE_SCAN_STATE` repository variable, so scanning never creates repository commits

Steps:
1. Detect upstream version candidates.
2. Compare current version and target version.
3. Create one scan-review parent issue per non-dry-run scan, including no-update and undetermined results.
4. Owner reviews the evidence, checks the approved apps in the issue checklist, optionally edits each target version, and comments `/approve-updates`.
5. The scan-review workflow creates one linked child issue per explicitly approved app and assigns Copilot to it. The `/approve-updates` comment is the owner approval that starts the update assessment.
6. AI researches upstream release notes and docs. Network probes use a 2s per-attempt budget with at most 2 retries; on local failure, fetch through the remote host's egress instead of extending timeouts.
7. AI edits `.env`, `docker-compose.yml`, `variables.json`, `README.md`, and `src/` when needed for the target version and for any app-local conformance fixes required by current repository rules. When `libs app-check --gate database` reports a bundled DB track as EOL, update it to a vendor-supported alive LTS track in the same update.
8. AI registers any new translatable env key in `i18n/translation.json`.
9. AI runs automated validation.
10. AI syncs the changed app to the test server's websoft9 store with `libs appstore-sync` when the container is reachable; skip within 10s when it is absent.
11. AI publishes the test report.
12. Owner runs final E2E.
13. Owner decides merge, release, defer, or reject.

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
- Manual runs can set `due_within_days` (0-90) to include apps due within the next N days. The target date is computed in Asia/Shanghai; scanning early updates `ok_at` to the actual scan time, so the next due date moves with the early scan.
- A missing or unreadable state value is a hard error, never "everything is due".
- The scan selector lives in `.github/workflows/maintenance-scan.yml`. Reading a variable needs no token, but updating it needs a PAT with repo scope (classic) or Variables read/write (fine-grained); the automatic `GITHUB_TOKEN` cannot write Actions variables. The workflow uses one PAT secret: `MAINTENANCE_STATE_TOKEN`.
- Each regular scan creates or reuses one parent issue identified by the workflow run ID. The parent stores the scan snapshot and a checklist; owner approval is a `/approve-updates` comment after checking the desired apps. Explicit `/approve-updates app1, app2` remains supported.
- `issue_comment` on a scan-review parent creates the approved child issues and assigns Copilot; it does not edit app files directly.
- Adding the `ai` label is the single issue-assignment trigger, including labels applied by issue templates. When Copilot requests review after its session completes, one `PR checks` run receives `pull_request_target: review_requested`, verifies the latest agent session succeeded, validates the package, publishes the required check on the exact PR head, marks the PR Ready, and provisions E2E. There is no separate Prepare workflow or scheduled polling. Draft creation and intermediate pushes do not create checks; request review again after subsequent commits. Disable Copilot cloud agent's **Require approval for workflow runs** setting to run unattended. The owner confirms E2E and manually merges the PR.
- Scan-review parent issues are created with `GITHUB_TOKEN`, so they do not start the AI workflow on open. The owner comment is the explicit AI trigger.
- `review-first` stops before implementation unless owner approves.
- Update work is not limited to version bumping; the changed app must satisfy the current quality gates before handoff.
- Update work should not trigger broad repository-wide template churn; only the minimum relevant app-local conformance fixes should be included.
- Failed automated validation keeps the issue open and blocks owner E2E.
