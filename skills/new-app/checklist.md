# New App Checklist

- [ ] Load CLI venv (`make install` if `.venv/` missing), run `make --no-print-directory libs ARGS="list --include-archived --json"`
- [ ] If `<app>` is in the full list (active/archived/internal), report its status, scope, cadence, update_policy and stop (re-input name or terminate)
- [ ] Read the issue prose, extract name, trademark, and at least one official reference URL
- [ ] Read official docs, image references, repository rules, `docs/w9-env-spec.md`, and `metadata/templates/new-app/`
- [ ] Scaffold via `libs app-new --name ... --trademark ... [--version <x.x> --repo <image> --docs-* ... --upstream-releases <url> --upstream-compose <url> --upstream-env <url>]`; it refuses duplicates and runs the quality gates; omitted version/repo become TODO placeholders
- [ ] Fill any missing upstream fields in `variables.json` after research confirms what is applicable; omit fields that are not applicable
- [ ] Fill compose design, upstream metadata, DB version, and i18n keys beyond the skeleton
- [ ] Use braced `${VAR}` form for all environment variable references in `.env`, `docker-compose.yml`, and config templates
- [ ] Decide env groups: enable password group (DB/login apps) and web group (web apps); delete unused groups
- [ ] Apply `docs/w9-env-spec.md` decision rules for `W9_URL`, `W9_URL_REPLACE`, `W9_LOGIN*`, `_SET` ports, and dependency helpers
- [ ] Fill `.env` "image environment variables" section: single Docs URL, used vars, up to 5 unused vars commented out
- [ ] Write `CHANGELOG.md` with the pure-date heading `## YYYY-MM-DD` for the initial change batch
- [ ] Run `libs app-check --app <app>` and deploy/reachability validation
- [ ] Produce a short test report
- [ ] Assign cadence/update policy by writing the app into `metadata/maintenance.yaml` buckets, and state it in the report
- [ ] Write repo catalog fields: copy `metadata/templates/catalog.json` to `metadata/catalog/<app>.json`; fill `catalogBindings` from `metadata/catalog-taxonomy.json` when applicable; owner reviews before `libs catalog-push --app <app> --apply`
