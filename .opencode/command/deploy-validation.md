---
description: Prove one app deploys, locally or on a prepared remote server
agent: build
---

Use the `deploy-validation` skill to run the validation workflow.

If the task input is empty, ask the user for the app name.

The default target is remote. The task input may carry `--host <ip> --user <name> --key <path> --path <dir>`; treat the presence of `--host` as remote. If the input says `local`, or no remote server is available on the current machine, use target local.

If remote and `--host` or `--user` is missing, ask the user for them before starting.

The remote SSH key convention is `.secrets/ssh/default.pem` under the repository root (git-ignored, chmod 600). `--key` overrides it with a relative path under `.secrets/ssh/` or an absolute path.

$ARGUMENTS
