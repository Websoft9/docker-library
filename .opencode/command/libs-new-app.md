---
description: Create one new app package and produce a short report
agent: build
argument-hint: [app name] [trademark] [official reference URL]
---

Use the `new-app` skill to run the new app workflow.

Usage: /libs-new-app <app name> <trademark> <official reference URL>

If the task input is `help` or empty, echo the usage line, then ask the user for the app name, trademark, and official upstream references.

If the task input is missing any of these (no trademark, or no official reference URL), ask the user to fill them before starting research.

If the task input is present, treat it as the workflow input.

$ARGUMENTS
