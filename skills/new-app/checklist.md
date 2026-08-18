# New App Checklist

- [ ] Load CLI venv (`make install` if `.venv/` missing), run `make --no-print-directory libs ARGS="list --include-archived --json"`
- [ ] If `<app>` is in the full list (active/archived/internal), report its status, scope, cadence, update_policy and stop (re-input name or terminate)
- [ ] Read official docs and image references
- [ ] Read `template/` files
- [ ] Create `apps/<app>/`
- [ ] Fill `.env`, `docker-compose.yml`, `variables.json`, `README.md`, and `src/`
- [ ] Register new translatable env keys in `i18n/translation.json` if needed
- [ ] Run structure, policy, deploy, and reachability checks
- [ ] Produce a short test report
- [ ] Recommend cadence and update policy
