# Shared Skills

`skills/` is the canonical source for project skills shared across agents.

Rules:
- keep skill bodies agent-agnostic
- describe intent, inputs, outputs, and decision rules
- keep agent-specific invocation in adapter layers such as `.opencode/command/`
- repository-specific facts and paths are allowed

Current adapters:
- opencode: `.opencode/opencode.json` via `skills.paths`

Shared skills:
- `update-assessment`
- `app-update`
- `new-app`
- `archive-app`
- `restore-app`
- `test-report-generation`
- `release-readiness-check`
