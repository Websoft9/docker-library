---
description: Implement an approved update for one app and produce a short report
agent: build
argument-hint: [app name] [target version]
---

Use the `app-update` skill to run the app update workflow.

The slash command stays action-first (`update-app`) even though the shared skill label is `app-update`.

Usage: /update-app <app name> <target version>

If the task input is `help` or empty, echo the usage line, then ask the user for the app name and target version.

If the task input is present, treat it as the workflow input.

If the task input contains `--report`, `formal`, or `formal-report`, produce the output using `report-template.md` from the skill.

$ARGUMENTS
