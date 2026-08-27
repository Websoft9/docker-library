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

Naming guidance:
- shared skill names are workflow labels and MAY differ from user-facing adapter command names
- adapter command names SHOULD prefer action-first intent phrases such as `update-app` or `new-app`
- do not mix multiple naming orders within the same adapter surface unless there is a compatibility reason

Current adapters:
- opencode: `.opencode/opencode.json` via `skills.paths`

Shared skills:
- `update-assessment`
- `app-update`
- `new-app`
- `archive-app`
- `restore-app`
- `deploy-validation`
- `test-report-generation`
- `release-readiness-check`
