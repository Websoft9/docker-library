---
name: libs
description: Use when working on a Websoft9 docker-library issue, update, new app, bug, archive, restore, or batch task. Routes the issue's hidden workflow marker to the canonical workflow documents and skills under skills/.
---

# Libs Workflows

Read `AGENTS.md` first. The canonical workflow documents and skills are under `skills/`; this skill only routes to them.

The first hidden marker in the issue body selects the workflow:

- `new-app`: read `skills/new-app/SKILL.md`.
- `update-app`: read `skills/update-assessment/SKILL.md`, then `skills/app-update/SKILL.md` when the decision is `auto-update`.
- `batch-update`: read `skills/batch-app-update/SKILL.md`.
- `bug-report`: investigate the problem and fix it when the cause and fix are clear.
- `change-request`: research the request and implement the smallest correct change; for research-only requests, report findings without changing code.
- `archive-app`: read `skills/archive-app/SKILL.md`.
- `restore-app`: read `skills/restore-app/SKILL.md`.
- `delete-app`: use `skills/archive-app/SKILL.md` for metadata handling, then apply the permanent-delete scope stated in the issue.

Before changing runnable behavior, also read `docs/ai-sdlc/05-quality-gates.md`. Follow the repository conventions in `AGENTS.md`, run the required tests, and leave branch, commit, and pull request creation to Copilot.

If the marker is missing or the required information is insufficient, state the blocking question in the issue and stop.
