# Update Pipeline

Trigger:
- daily schedule selects all apps whose cadence is due

Steps:
1. Detect upstream version candidates.
2. Compare current version and target version.
3. Classify the candidate as `auto-update`, `review-first`, `defer`, or `skip`.
4. Create or update one issue per app.
5. AI researches upstream release notes and docs.
6. AI edits `.env`, `docker-compose.yml`, `variables.json`, `README.md`, and `src/` when needed for the target version and for any app-local conformance fixes required by current repository rules.
7. AI registers any new translatable env key in `i18n/translation.json`.
8. AI runs automated validation.
9. AI publishes the test report.
10. Owner runs final E2E.
11. Owner decides merge, release, defer, or reject.

Archive path:
- if owner decides to retire an app, move it to `archive/apps/`
- update `metadata/maintenance.yaml`
- update `metadata/archive.yaml`
- trigger Contentful metadata sync with `production=false`

Notes:
- Version detection does not change code by itself.
- `review-first` stops before implementation unless owner approves.
- Update work is not limited to version bumping; the changed app must satisfy the current quality gates before handoff.
- Update work should not trigger broad repository-wide template churn; only the minimum relevant app-local conformance fixes should be included.
- Failed automated validation keeps the issue open and blocks owner E2E.
