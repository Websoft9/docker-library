---
description: Prove one app deploys, locally or on a prepared remote server
agent: build
argument-hint: [app name] [--ssh-host ip --ssh-user name --ssh-secret-path path --deploy-root dir]
---

Use the `deploy-validation` skill to run the validation workflow.

Usage: /libs-deploy-validation <app name> [--ssh-host ip --ssh-user name] [--ssh-secret-path path] [--deploy-root dir] [local]

If the task input is `help` or empty, echo the usage line, then ask the user for the app name.

The default target comes from `.secrets/remote.env` (`TARGET=...`); when the profile file is absent, fall back to local. The task input may carry `--ssh-host <ip> --ssh-user <name> --ssh-secret-path <path> --deploy-root <dir>`; treat the presence of `--ssh-host` as remote. If the input says `local`, force target local.

If the resolved target is remote and `--ssh-host` is missing, ask the user for it before starting. `--ssh-user` is optional and defaults from `.secrets/remote.env` or `root`.

The remote SSH secret-path convention is `.secrets/ssh/default.pem` under the repository root (git-ignored, chmod 600). `--ssh-secret-path` overrides it with a relative path under `.secrets/ssh/` or an absolute path. The file may contain either a private key or a password: first detect which it is, then build the SSH auth fragment accordingly. Always add `-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=15`: the dedicated ephemeral test server may be reimaged, so a stale `~/.ssh/known_hosts` entry must never block automation. The default deploy root is `/opt/websoft9-test/apps`.

$ARGUMENTS
