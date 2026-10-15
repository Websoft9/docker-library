---
description: Implement approved updates for a batch of apps selected by app names or initials
agent: build
argument-hint: [app list | initials] [options optional]
---

Use the `batch-app-update` skill to run the batch app update workflow.

The slash command stays action-first (`libs-batch-update-app`) even though the shared skill label is `batch-app-update`.

Usage: `/libs-batch-update-app <selector>`

Supported selector forms:

- explicit app list, for example `n8n,nocodb,netdata`
- initials, for example `n,m` to target all apps whose names start with `n` or `m`
- mixed input when clear, for example `n8n,n,m`

Supported options:

- `--mode auto|app-list|initials`
- `--concurrency 1|2|3`
- `--continue`
- `--stop-on-first-failure`
- `--report`

Default behavior:

- selector mode defaults to `auto`
- concurrency defaults to `2`
- failure policy defaults to `continue`
- apps that appear to require reverse-engineering from an official `install.sh` without a clear official Compose spec, especially when the runtime likely exceeds 5 containers, should be skipped quickly and recorded in the batch summary for later manual follow-up
- after each app passes automated validation, run `libs appstore-sync --app <name>` so the updated package is synced into the appstore environment for the later manual E2E pass

If the task input is `help` or empty, echo the usage line, then ask the user for the selector.

If the task input is present, treat it as the workflow input.

If the task input contains `--report`, `formal`, or `formal-report`, produce the output using `report-template.md` from the skill.

$ARGUMENTS
