---
description: Restore one archived app back to active maintenance
agent: build
argument-hint: [app name] [--cadence monthly --update-policy patch-minor]
---

Use the `restore-app` skill to run the restore workflow.

Usage: /libs-restore-app <app name> [--cadence monthly] [--update-policy patch-minor]

If the task input is `help` or empty, echo the usage line, then ask the user for the app name, and optionally the cadence and update policy.

If the task input is present, treat it as the workflow input.

$ARGUMENTS
