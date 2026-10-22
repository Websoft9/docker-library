# Install App Checklist

- [ ] Confirm app name and install contract
- [ ] Confirm install target (`local` or `remote`)
- [ ] Confirm execution mode (`plan_only` / `execute_with_confirmation` / `execute_directly`)
- [ ] Confirm target folder before running write/install commands
- [ ] Run prerequisite checks (for example Docker + Compose v2)
- [ ] Identify required server ports and check occupancy before install
- [ ] Prefer available ports in `9000-9999` when custom ports are supported
- [ ] Execute install commands from the contract
- [ ] Handle remaining port conflicts per contract rule
- [ ] Run required service and endpoint health checks
- [ ] Return final URL, evidence, and backup reminders
