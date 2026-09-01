---
description: Assess whether one app is worth updating before implementation
agent: build
argument-hint: [app name]
---

Use the `update-assessment` skill to run the update assessment workflow.

Usage: /libs-update-assessment <app name>

If the task input is `help` or empty, echo the usage line, then ask the user which app to assess.

If the task input is present, treat it as the workflow input.

If the task input contains `--report`, `formal`, or `formal-report`, produce the output using `report-template.md` from the skill.

$ARGUMENTS
