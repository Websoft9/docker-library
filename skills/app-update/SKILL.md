---
name: app-update
description: Use when the user wants to implement an approved app update after assessment, update one app to a target version, adjust app files, run validation, and produce a short test report. Trigger phrases: update app, implement update, 升级应用, 更新应用, update <app> to <version>.
---

# App Update

Implement one approved app update with minimal app-local changes.

When the caller provides only an app name, first detect a candidate target version and gather upstream references, then present that candidate for owner confirmation before implementation. Do not skip confirmation unless the target version is already fixed by an issue, an approved assessment, or an explicit owner instruction in the current conversation.

This skill follows `docs/ai-sdlc/03-update-pipeline.md`, `docs/ai-sdlc/05-quality-gates.md`, and `docs/ai-sdlc/06-test-report-format.md`.

Supporting files in this skill:

- `checklist.md`
- `prompt-fragments.md`
- `report-template.md`

## Inputs

- app name (required)
- target version (optional at entry; required before editing files unless already fixed by the issue, an approved assessment, or an explicit owner confirmation after detection)
- upstream references (required before editing files)

## Steps

1. Read repository facts from `apps/<app>/`, `metadata/maintenance.yaml`, and the app notes when relevant.
2. If the caller did not provide a target version, detect a candidate target version first by checking the current package version, the upstream image tags, and the upstream release notes or changelog. If the candidate is not already fixed by issue context or approved assessment, stop and obtain owner confirmation before editing files.
3. Read `docs/w9-env-spec.md` before touching `.env` or `docker-compose.yml`; use it as the canonical `W9_*` reference, then mirror `metadata/templates/new-app/.env.tmpl` for layout.
4. Read the approved assessment result, if one exists.
5. Read upstream release notes, upgrade notes, image tags, and requirements.
6. Update only the files required for the target version and any app-local files that must change to satisfy current repository quality gates or generation rules, typically `.env`, `docker-compose.yml`, `variables.json`, `README.md`, `CHANGELOG.md`, and `src/`.
7. Keep changes app-local unless the task explicitly requires cross-repo updates.
8. Apply the version tag policy from `docs/devops-spec.md`: prefer `x.x`, use `x.x.x` only when exact patch pinning is required.
9. If new translatable env keys are introduced, register them in `i18n/translation.json`.
10. When `.env` is touched, keep the "image environment variables" section intact and mirror the template layout in `metadata/templates/new-app/.env.tmpl`: keep the section banner, the Docs URL, the "Used by docker-compose.yml" group, and the commented "Not used by default" group. Refresh the single Docs URL if the upstream changed, keep only the variables required by the current package shape plus any user-facing essentials, keep the used vars aligned with `docker-compose.yml`, and keep commented unused vars at no more than 5. Follow the decision rules in `docs/w9-env-spec.md` for `W9_URL`, `W9_URL_REPLACE`, login pairs, `_SET` ports, and dependency helpers. Use a domain-style `W9_URL` placeholder (for example `appname.example.com` or `example.youdomain.com`); do not use `internet_ip:${W9_HTTP_PORT_SET}`. Whenever `.env` is touched at all, convert every environment-variable reference in the whole file to the braced form `${VAR}`; do not leave bare `$VAR` in the file even on lines that were already present.
11. When `docker-compose.yml` is touched, ensure every published port line carries an inline `# purpose` comment and that no `# image:` / `# docs:` source comments remain — image and documentation sources live only in `variables.json` `upstream`. Convert every environment-variable reference in the whole file to the braced form `${VAR}` (for example `${W9_REPO}`, `${W9_HTTP_PORT_SET}`), not just the lines being changed.
12. When a credential or config env var only takes effect on first container startup (the image's entrypoint uses a marker file, e.g. `webconsole.security.enabled`), record that fact in `variables.json` as `env.first_startup_only` (a list of such env names). The README generator then auto-renders the warning; keep the "how to rotate" solution in the hand-written README Change Password section or Notes instead of in metadata.
13. When an app does not control a built-in admin password in `.env` but the password or token can be resolved after startup from inside the application container or from its logs, declare a declarative source in `variables.json.credentials.password` using `container-file` or `container-log`. Prefer this over adding the legacy `W9_LOGIN_GET_PASSWORD` command string.
14. Healthchecks should default to the main app container only. Add healthchecks to sidecar or dependency containers only when the official upstream compose explicitly defines them or the task explicitly requires them.
15. If the target app has app-local drift against the current repository rules (for example template, metadata, env policy, or generated README expectations), fix the minimum blocking or directly relevant items as part of the same update.
16. Keep `apps/<app>/CHANGELOG.md` as the single source of app change history. Use a pure-date heading `## YYYY-MM-DD` as the first-level heading for each change batch; list all changes for that date below it. Do not duplicate changelog content into `README.md`.
17. Run `.venv/bin/libs app-gen-readme --app <app> --json` after metadata or README marker content changes so generated sections stay current.
18. For dependency images such as PostgreSQL, MySQL, MariaDB, Redis, or pgvector, prefer `x.x` tags even when upstream examples show `x.x.x`, unless exact patch pinning is demonstrably required. Hard-coded dependency `x.x.x` tags in `docker-compose.yml` are policy drift and should be normalized before handoff.
19. Verify braced references: scan the touched `.env` and `docker-compose.yml` for any remaining bare `$VAR` reference (for example `grep -nE '\$W9_[A-Z_]+'`); fix every hit to `${VAR}` before handoff. A file that was touched must contain no bare `$VAR` anywhere.
20. Ensure `apps/<app>/tests/cases.yml` exists and reflects the app's real functional path. Follow `docs/app-tests.md`: keep the built-in adaptive checks and add the minimum app-specific cases the defaults cannot cover, such as `http-basic` for an authenticated console or API, `web-access` for a dedicated health endpoint, or `script` only when built-ins are insufficient. Do not add a case that duplicates a default check.
21. Run the `deploy-validation` skill for the changed app.
22. Produce a short test report.

## Output

- files changed
- target version
- automated validation result
- risks
- owner E2E focus

## Rules

- Do not start implementation for a `review-first` candidate unless the owner has approved continuation.
- When only an app name is provided, discovery is allowed, but file edits must wait until the owner confirms the detected candidate version unless approval already exists in issue context or a prior assessment.
- Keep the smallest correct change.
- The update is not a blind version bump. The changed app must still pass the current quality gates after the work is complete.
- Do not perform broad cosmetic template re-alignment. Fix only the app-local conformance items that are blocking, directly relevant to the update, or required by current gates and generators.
- Keep `upstream.image` as the single version source. Never write `version_from`, `fork_url`, or `requirements.url`.
- Do not hand off an app whose only functional coverage is the default adaptive checks when its core path needs an app-specific check; author or refresh `apps/<app>/tests/cases.yml`.
- Prefer official or trusted upstream images.
- Produce the report in the same language the user used unless the user asks otherwise.
- Use `report-template.md` when the user asks for a formal implementation report.
