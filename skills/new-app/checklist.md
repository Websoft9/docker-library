# New App Checklist

- [ ] Load CLI venv (`make install` if `.venv/` missing), run `make --no-print-directory libs ARGS="list --include-archived --json"`
- [ ] If `<app>` is in the full list (active/archived/internal), report its status, scope, cadence, update_policy and stop (re-input name or terminate)
- [ ] Read the issue prose, extract name, trademark, and at least one official reference URL
- [ ] Read official docs, image references, repository rules, and `metadata/templates/new-app/`
- [ ] Scaffold via `libs new-app --name ... --trademark ... [--version <x.x> --repo <image> --docs-* ...]`; it refuses duplicates and runs the quality gates; omitted version/repo become TODO placeholders
- [ ] Fill compose design, upstream metadata, DB version, and i18n keys beyond the skeleton
- [ ] Decide env groups: enable password group (DB/login apps) and web group (web apps); delete unused groups
- [ ] Fill `.env` "image environment variables" section: single Docs URL, used vars, up to 5 unused vars commented out
- [ ] Run `libs check --app <app>` and deploy/reachability validation
- [ ] Produce a short test report
- [ ] Assign cadence/update policy by writing the app into `metadata/maintenance.yaml` buckets, and state it in the report
- [ ] Draft Contentful fields: copy `metadata/templates/contentful-draft.json` to `metadata/contentful-drafts/<app>.json`; owner reviews before `libs contentful-create --app <app> --apply`
