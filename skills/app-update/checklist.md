# App Update Checklist

- [ ] Confirm the update is approved for implementation
- [ ] Read app-local files under `apps/<app>/`
- [ ] Read `docs/w9-env-spec.md` before editing `.env` or `docker-compose.yml`
- [ ] Read upstream release notes and upgrade notes
- [ ] Choose `x.x` or `x.x.x` tag using repository policy
- [ ] Update only required files
- [ ] Use braced `${VAR}` form for **all** environment-variable references in every edited file (`.env`, `docker-compose.yml`, mounted config templates), not only the lines changed this run
- [ ] Scan edited files for remaining bare `$VAR` references and fix all hits before handoff
- [ ] Fix minimum app-local conformance drift required by current gates or generation rules
- [ ] Author or refresh `apps/<app>/tests/cases.yml` per `docs/app-tests.md` (built-in checks plus the minimum app-specific cases)
- [ ] Keep changes app-local
- [ ] Update `apps/<app>/CHANGELOG.md` with a pure-date heading `## YYYY-MM-DD` for this change batch
- [ ] Register new translatable env keys in `i18n/translation.json` if needed
- [ ] When an interactive app exposes its initial password or token from a container file or logs, prefer `variables.json.credentials.password` over the legacy `W9_LOGIN_GET_PASSWORD`
- [ ] Run structure, policy, deploy, and reachability checks when applicable
- [ ] Produce a short test report
