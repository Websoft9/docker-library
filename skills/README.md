# Shared Skills

`skills/` is the canonical source for project skills shared across agents.

Rules:
- keep skill bodies agent-agnostic
- describe intent, inputs, outputs, and decision rules
- keep agent-specific invocation in adapter layers such as `.opencode/command/`
- repository-specific facts and paths are allowed

Running the CLI from a skill:
- call `.venv/bin/libs ...` directly; the CLI auto-detects proxy environment variables and neutralizes a wildcard `no_proxy`
- use `libs --proxy <url> ...` only when the host proxy is not exported
- `make libs ARGS="..."` is optional convenience, not a required convention
- do not use `make cli`; it starts an interactive shell for humans

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
