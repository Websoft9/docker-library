---
name: install-app
description: Use when the user wants to install one app package with a repeatable runbook, choose local vs remote host, pre-check and allocate server ports (prefer 9000-9999), verify Docker Compose deployment health, and return access URL plus backup reminders. Trigger phrases: install app, deploy app, install <app>, 安装应用, 部署应用.
---

# Install App

Install one application using a structured, verifiable workflow contract.

This skill is a generic execution wrapper for app-specific install instructions.  
Use it with per-app facts from `apps/<app>/` and official upstream docs.

Supporting files in this skill:

- `checklist.md`
- `report-template.md`

## Inputs

- app name (required)
- install contract/prompt (required): concrete command sequence and success criteria
- install target (required before execution): `local` or `remote`
- execution mode (optional): `plan_only` | `execute_with_confirmation` | `execute_directly` (default: `execute_with_confirmation`)
- language (optional, default `en`)
- workspace folder chosen by user (optional at planning, required before execution when commands write files)

## Steps

1. Parse the install contract into explicit phases: prerequisites, install, conflict handling, validation, and user handoff.
2. Ask whether to install on `local` or `remote` host before execution. If the user does not specify, ask explicitly instead of assuming.
3. Run prerequisite checks exactly as required by the contract (for example, `docker compose version`). If a mandatory dependency is missing, stop and report the exact blocker.
4. Resolve required server ports before installation: probe occupancy first, then choose available ports with this priority order:
   - contract-required fixed port (if mandatory and free)
   - nearest available port in `9000-9999`
   - contract fallback strategy (for example `--port <free-port>`)
5. In `execute_with_confirmation` mode, present the exact command plan (including selected target and ports) and wait for user confirmation before executing.
6. Execute install commands in the user-selected folder. Keep commands deterministic and non-interactive when possible.
7. Run all required health checks and capture evidence (for example, `docker compose -p <project> ps` and HTTP health endpoint checks).
8. Produce a concise outcome report using `report-template.md`.
9. Provide handoff details: final access URL, credentials retrieval path (if applicable), and backup reminders (such as backing up generated `.env`).

## Output

- install result (`passed` / `failed` / `blocked`)
- install target (`local` / `remote`)
- execution folder
- commands run
- port allocation result (required port, occupancy check, and final port)
- health check evidence
- access URL and next actions

## Rules

- Never invent prerequisites, flags, ports, or health endpoints that are not in the contract or repository facts.
- Always ask for install target (`local` or `remote`) before execution when it is not explicitly given.
- For server-facing ports, prefer available ports in the `9000-9999` range whenever the contract allows custom ports.
- Always check port occupancy before install commands that bind ports.
- If critical input is missing (for example, target folder or required secret), stop and ask the user before execution.
- Do not silently ignore a failed check; surface the first blocking error and its command output.
- Keep changes scoped to the target app/work folder.
- Match output language to user preference.
