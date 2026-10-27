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

An issue starts Copilot when it is opened with the `ai` label by an `OWNER`, `MEMBER`, or `COLLABORATOR`, or when the `ai` label is added later by a user with label permission. The issue templates apply `labels: ai` by default, but external issue authors do not trigger assignment on open. Duplicate assignment is skipped when Copilot is already assigned. The assignment workflow uses `COPILOT_ASSIGN_TOKEN` when set, otherwise `MAINTENANCE_STATE_TOKEN`; the token must be a user PAT with `repo` scope that can assign Copilot.

For maintenance scan review, check the apps in the issue checklist and comment `/approve-updates`, or comment `/approve-updates app1, app2` to name apps explicitly. The workflow creates linked child issues deterministically and assigns Copilot to each approved child, so Copilot starts working immediately.

After the Copilot session completes, `Prepare Copilot PR for checks` marks its draft PR ready. That transition triggers `PR checks`; after they pass, the workflow provisions the E2E environment, posts its details, and sends the WeCom notification. The owner performs E2E and manually clicks Merge.

E2E waits for SSH first, then shares a five-minute deadline across Websoft9 startup and all application sync retries. Each sync attempt is capped at 60 seconds. Obsolete PR runs are skipped before provisioning, and environments for superseded commits are not announced as ready. Only `PR checks` is a required merge status; an E2E provisioning failure is reported separately.

The issue-assignment and PR-ready workflows use `COPILOT_ASSIGN_TOKEN` (preferred) or `MAINTENANCE_STATE_TOKEN`, a user PAT with permission to assign Copilot and update pull requests. In **Settings → Copilot → cloud agent → Actions workflow approval**, disable **Require approval for workflow runs** so Copilot-triggered checks can start without manual approval. The `main-protection` ruleset should require `PR checks` and zero approving reviews. A review request from Copilot is informational; the owner still merges manually after E2E.

Keep changes minimal and app-local, validate runnable behavior by deployment, and never commit secrets.
