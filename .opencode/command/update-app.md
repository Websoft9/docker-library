---
description: Implement an approved update for one app and produce a short report
agent: build
---

Use the `app-update` skill to run the app update workflow.

If the task input is empty, ask the user for the app name and target version.

If the task input is present, treat it as the workflow input.

If the task input contains `--report`, `formal`, or `formal-report`, produce the output using `report-template.md` from the skill.

$ARGUMENTS
