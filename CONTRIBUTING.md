# Contributing

This repository uses an AI-first delivery model: owners decide demand and the final E2E result; AI handles research, implementation, validation, and reporting.

## Start here

- `AGENTS.md`
- `docs/vision.md`
- `docs/architecture.md`
- `docs/ai-sdlc/README.md`
- `skills/README.md`

## Workflow

1. Open an issue for one app or one coherent task.
2. The AI workflow starts automatically and uses the matching skill.
3. Review the AI pull request to `main`; it links the issue and includes the latest test report. Use a Conventional Commits title such as `fix: ...`, `feat: ...`, or `ci: ...`.
4. The owner performs final E2E; release is a semver tag on `main`.

`main` is protected by the `main-protection` ruleset: PR-only, squash merges, linear history, and no force pushes or branch deletion.

## Issue automation

Adding the `ai` label starts Copilot. The issue templates apply `labels: ai` by default, so template creation emits the same label event; the assignment workflow does not also listen for issue opening. Duplicate assignment is skipped when Copilot is already assigned. The assignment workflow uses `COPILOT_ASSIGN_TOKEN` when set, otherwise `MAINTENANCE_STATE_TOKEN`; the token must be a user PAT with `repo` scope that can assign Copilot.

For maintenance scan review, check the apps in the issue checklist and comment `/approve-updates`, or comment `/approve-updates app1, app2` to name apps explicitly. The workflow creates linked child issues deterministically and assigns Copilot to each approved child, so Copilot starts working immediately.

When Copilot requests review after finishing its session, `PR checks` handles `pull_request_target: review_requested`. Within that single workflow run it confirms the latest agent session succeeded, validates the PR, publishes the required `PR checks` check on the exact PR head commit, marks the successful PR Ready, and provisions E2E. The owner performs E2E and manually clicks Merge. No separate Prepare workflow, scheduled polling, PR approval, or manual Ready transition is required.

Draft creation, intermediate pushes, and the automatic Ready transition do not create workflow runs. The normal pre-merge flow has three runs: issue assignment, Copilot agent, and PR checks (including E2E). For a manually authored same-repository PR, request a reviewer to start checks. After further commits, request review again; a new head commit needs its own successful check before merging. Multiple reviewer requests can each trigger a run, so request one reviewer per handoff.

PRs modifying `.github/workflows/pr-checks.yml` also run checks on opening or pushing through a path-filtered `pull_request` trigger. This lets trigger changes validate themselves before the new `pull_request_target` configuration exists on `main`; app-only PRs do not use this compatibility trigger.

PR validation runs in a separate read-only job without secrets or persisted checkout credentials. Commit-status publishing and Ready transitions use `GITHUB_TOKEN` in metadata-only jobs; cloud credentials are only used by the E2E job with base-branch tooling.

E2E waits for SSH first, then shares a five-minute deadline across Websoft9 startup and all application sync retries. Each sync attempt is capped at 60 seconds. Obsolete PR runs are skipped before provisioning, and environments for superseded commits are not announced as ready. Only `PR checks` is a required merge status; an E2E provisioning failure is reported separately.

In **Settings → Copilot → cloud agent → Actions workflow approval**, disable **Require approval for workflow runs** so Copilot-triggered checks can start without manual approval. The `main-protection` ruleset should require `PR checks` and zero approving reviews. A review request from Copilot starts automation; it does not require the owner to submit an approving review.

Keep changes minimal and app-local, validate runnable behavior by deployment, and never commit secrets.
