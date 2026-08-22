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
- target: local | remote (default remote)
- remote host (required when target=remote)
- remote user (optional when target=remote; defaults to `root`)
- remote path (default `/opt/websoft9-test`)
- remote key (default `.secrets/ssh/default.pem` under the repository root; git-ignored, chmod 600; never commit it)

## Steps

1. Run the gates locally: `make --no-print-directory libs ARGS="check --app <app> --json"`. On failure, stop and report the first blocking error.
2. target=remote: sync the app directory to the server, then record the server identity in the evidence:
   `tar czf - apps/<app> | ssh -i <key> <user>@<host> "mkdir -p <remote_path> && tar xzf - -C <remote_path>"`
3. Ensure the shared network exists on the execution target: `docker network create websoft9 || true`.
4. Run `docker compose -f <path>/<app>/docker-compose.yml --env-file <path>/<app>/.env config --quiet`; stop on failure.
5. Run `docker compose ... up -d` and wait for containers to reach running or healthy state.
6. Verify behavior: when the app declares `W9_HTTP_PORT_SET`, probe `http://localhost:<port>` on the target (public IP probing is acceptable too; no secrecy is required). Otherwise verify the expected command output, exit code, or listening port.
7. Check container logs for blocking errors.
8. Cleanup in all outcomes: `docker compose ... down -v`. For remote, the server itself stays running; deletion stays manual.
9. Return validation evidence: gates, deploy, reachability, logs, cleanup, and the server identity when remote.

## Output

- target and server identity (remote only)
- structure gate result
- policy gate result
- deploy result
- reachability result
- log check result
- cleanup status
- first blocking error (when failed)

## Rules

- Validation only; never modify app files.
- Never skip a failed gate; report the first blocking error.
- When the remote user is not provided, default to `root`. If SSH auth fails with the default user, stop and ask the user for the correct user and key; do not retry with guessed users.
- The server is assumed dedicated and ephemeral; its IP is public information and is recorded openly in the report.
- Environment limitations (e.g. registry unreachable, missing docker daemon) are reported as environment blocks, not app defects.
- `down -v` runs even when validation fails; server deletion stays manual.
- Produce evidence in the same language the user used unless the user asks otherwise.
