---
description: Create one new app package and produce a short report
agent: build
---

Use the `new-app` skill to run the new app workflow.

If the task input is empty, ask the user for the app name, trademark, and official upstream references.

If the task input is missing any of these (no trademark, or no official reference URL), ask the user to fill them before starting research.

If the task input is present, treat it as the workflow input.

$ARGUMENTS
