---
description: Archive one app or a small batch of apps with metadata handoff
agent: build
argument-hint: [app name] [archive reason]
---

Use the `archive-app` skill to run the archive workflow.

Usage: /libs-archive-app <app name> <archive reason>

If the task input is `help` or empty, echo the usage line, then ask the user for the app name or app list and the archive reason.

If the task input is present, treat it as the workflow input.

$ARGUMENTS
