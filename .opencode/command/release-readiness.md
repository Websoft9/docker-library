---
description: Check whether an app task is ready for owner E2E or release
agent: build
argument-hint: [app name | task scope]
---

Use the `release-readiness-check` skill to run the release readiness workflow.

Usage: /release-readiness <app name | task scope>

If the task input is `help` or empty, echo the usage line, then ask the user for the app name or task scope.

If the task input is present, treat it as the workflow input.

$ARGUMENTS
