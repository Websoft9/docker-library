# AI-SDLC

This repository uses an AI-first SDLC for app updates and new app delivery.

Principles:
- Human only decides demand and final E2E result.
- AI owns research, implementation, automated validation, and report output.
- Every task starts from an issue.
- Every release candidate passes the same quality gates.

Model:
- `metadata/maintenance.yaml` is repository metadata
- `metadata/archive.yaml` stores archived app metadata
- issues are the work queue

Flow:
1. Issue defines the work.
2. AI researches and edits the app.
3. CI and AI run automated checks.
4. AI submits a test report.
5. Owner runs final E2E and decides merge or reject.

Docs:
- `01-operating-model.md`
- `02-maintenance-policy.md`
- `03-update-pipeline.md`
- `04-new-app-pipeline.md`
- `05-quality-gates.md`
- `06-test-report-format.md`
- `07-issue-contracts.md`
- `08-pr-contracts.md`
- `09-owner-e2e-runbook.md`
