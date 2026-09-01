---
description: Generate a repository-format test report from validation evidence
agent: build
argument-hint: [app name] [evidence source]
---

Use the `test-report-generation` skill to run the test report workflow.

Usage: /libs-test-report <app name> <evidence source>

If the task input is `help` or empty, echo the usage line, then ask the user for the app name and the validation evidence source.

If the task input is present, treat it as the workflow input.

$ARGUMENTS
