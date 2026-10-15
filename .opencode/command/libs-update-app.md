---
description: Implement an approved update for one app and produce a short report
agent: build
argument-hint: [app name] [target version optional]
---

Use the `app-update` skill to run the app update workflow.

The slash command stays action-first (`libs-update-app`) even though the shared skill label is `app-update`.

Usage: /libs-update-app <app name> [target version]

If the task input is `help` or empty, echo the usage line, then ask the user for the app name. The target version is optional: when omitted, detect the best candidate stable version and continue automatically when the choice is clear. A major version jump by itself is not a reason to stop for confirmation, because this workflow updates repository packaging rather than performing a live-instance migration. Ask for confirmation only when the candidate is ambiguous, risky for the package itself, or review-first.

If the task input is present, treat it as the workflow input.

If the task input contains `--report`, `formal`, or `formal-report`, produce the output using `report-template.md` from the skill.

$ARGUMENTS
