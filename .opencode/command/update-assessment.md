---
description: Assess whether one app is worth updating before implementation
agent: build
---

Use the `update-assessment` skill to run the update assessment workflow.

If the task input is empty, ask the user which app to assess.

If the task input is present, treat it as the workflow input.

If the task input contains `--report`, `formal`, or `formal-report`, produce the output using `report-template.md` from the skill.

$ARGUMENTS
