---
name: deploy-validation
description: Use when an app package has been created or changed and must be proven deployable. Runs structure/policy gates, docker compose deploy, reachability, and log checks, and returns validation evidence. Trigger phrases: run validation, deploy check, validate deployment, 部署验证, 验证应用.
---

# Deploy Validation

Prove one app package deploys correctly. Shared by the `new-app`, `app-update`, and `restore-app` workflows.

This skill follows `docs/ai-sdlc/05-quality-gates.md` and `docs/ai-sdlc/06-test-report-format.md`.

Supporting files in this skill:

- `checklist.md`
- `prompt-fragments.md`
- `report-template.md`

## Inputs

- app name (required)
- target: local | remote (default from `.secrets/remote.env`; fallback local)
- ssh host (required when target=remote)
- ssh user (optional when target=remote; defaults to `root`)
- deploy root (default `/opt/websoft9-test/apps`; the app target is `<deploy_root>/<app>`)
- ssh secret path (default `.secrets/ssh/default.pem` under the repository root; git-ignored, chmod 600; never commit it)

## Steps

1. Run the gates locally: `make --no-print-directory libs ARGS="check --app <app> --json"`. On failure, stop and report the first blocking error.
2. Run `make --no-print-directory libs ARGS="app-deploy --app <app> [--target <local|remote>] [--ssh-host <ip> --ssh-user <name> --ssh-secret-path <path> --deploy-root <dir>] --json"` to perform the compose deployment primitive. It handles local vs remote resolution, sync, network creation, `config`, `up -d`, and `ps` evidence.
3. Run `make --no-print-directory libs ARGS="app-tests --app <app> [--base-url <url>] [--ssh-host <ip> --ssh-user <name> --ssh-secret-path <path> --deploy-root <dir>] --json"` to perform functional checks. When `tests/cases.yml` is absent, the command still runs the default required checks.
4. Check container logs for blocking errors.
5. Cleanup in all outcomes with `make --no-print-directory libs ARGS="app-deploy --app <app> [--target <local|remote>] [--ssh-host <ip> --ssh-user <name> --ssh-secret-path <path> --deploy-root <dir>] --down --json"`. For remote, the server itself stays running; deletion stays manual.
6. Return validation evidence: gates, deploy, functional checks, logs, cleanup, and the server identity when remote.

## Output

- target and server identity (remote only)
- structure gate result
- policy gate result
- deploy result
- functional check result
- log check result
- cleanup status
- first blocking error (when failed)

## Rules

- Validation only; never modify app files.
- Never skip a failed gate; report the first blocking error.
- When the ssh user is not provided, default to `root`. If SSH auth fails with the default user, stop and ask the user for the correct user and secret path; do not retry with guessed users.
- The server is assumed dedicated and ephemeral; its IP is public information and is recorded openly in the report.
- Environment limitations (e.g. registry unreachable, missing docker daemon) are reported as environment blocks, not app defects.
- `down -v` runs even when validation fails; server deletion stays manual.
- Produce evidence in the same language the user used unless the user asks otherwise.
