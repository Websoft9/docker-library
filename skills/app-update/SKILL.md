---
name: app-update
description: Use when the user wants to implement an approved app update after assessment, update one app to a target version, adjust app files, run validation, and produce a short test report. Trigger phrases: update app, implement update, 升级应用, 更新应用, update <app> to <version>.
---

# App Update

Implement one approved app update with minimal app-local changes.

This skill follows `docs/ai-sdlc/03-update-pipeline.md`, `docs/ai-sdlc/05-quality-gates.md`, and `docs/ai-sdlc/06-test-report-format.md`.

Supporting files in this skill:

- `checklist.md`
- `prompt-fragments.md`
- `report-template.md`

## Inputs

- app name (required)
- target version (required unless already fixed by the issue or approved assessment)
- upstream references (required)

## Steps

1. Read repository facts from `apps/<app>/`, `metadata/maintenance.yaml`, and the app notes when relevant.
2. Read `docs/w9-env-spec.md` before touching `.env` or `docker-compose.yml`; use it as the canonical `W9_*` reference, then mirror `metadata/templates/new-app/.env.tmpl` for layout.
3. Read the approved assessment result, if one exists.
4. Read upstream release notes, upgrade notes, image tags, and requirements.
5. Update only the files required for the target version and any app-local files that must change to satisfy current repository quality gates or generation rules, typically `.env`, `docker-compose.yml`, `variables.json`, `README.md`, `CHANGELOG.md`, and `src/`.
6. Keep changes app-local unless the task explicitly requires cross-repo updates.
7. Apply the version tag policy from `docs/devops-spec.md`: prefer `x.x`, use `x.x.x` only when exact patch pinning is required.
8. If new translatable env keys are introduced, register them in `i18n/translation.json`.
9. When `.env` is touched, keep the "image environment variables" section intact and mirror the template layout in `metadata/templates/new-app/.env.tmpl`: keep the section banner, the Docs URL, the "Used by docker-compose.yml" group, and the commented "Not used by default" group. Refresh the single Docs URL if the upstream changed, keep only the variables required by the current package shape plus any user-facing essentials, keep the used vars aligned with `docker-compose.yml`, and keep commented unused vars at no more than 5. Follow the decision rules in `docs/w9-env-spec.md` for `W9_URL`, `W9_URL_REPLACE`, login pairs, `_SET` ports, and dependency helpers. Whenever `.env` is touched at all, convert every environment-variable reference in the whole file to the braced form `${VAR}`; do not leave bare `$VAR` in the file even on lines that were already present.
10. When `docker-compose.yml` is touched, ensure every published port line carries an inline `# purpose` comment and that no `# image:` / `# docs:` source comments remain — image and documentation sources live only in `variables.json` `upstream`. Convert every environment-variable reference in the whole file to the braced form `${VAR}` (for example `${W9_REPO}`, `${W9_HTTP_PORT_SET}`), not just the lines being changed.
11. When a credential or config env var only takes effect on first container startup (the image's entrypoint uses a marker file, e.g. `webconsole.security.enabled`), record that fact in `variables.json` as `env.first_startup_only` (a list of such env names). The README generator then auto-renders the warning; keep the "how to rotate" solution in the hand-written README Change Password section or Notes instead of in metadata.
12. Healthchecks should default to the main app container only. Add healthchecks to sidecar or dependency containers only when the official upstream compose explicitly defines them or the task explicitly requires them.
13. If the target app has app-local drift against the current repository rules (for example template, metadata, env policy, or generated README expectations), fix the minimum blocking or directly relevant items as part of the same update.
14. Keep `apps/<app>/CHANGELOG.md` as the single source of app change history. Use a pure-date heading `## YYYY-MM-DD` as the first-level heading for each change batch; list all changes for that date below it. Do not duplicate changelog content into `README.md`.
15. Run `.venv/bin/libs app-gen-readme --app <app> --json` after metadata or README marker content changes so generated sections stay current.
16. For dependency images such as PostgreSQL, MySQL, MariaDB, Redis, or pgvector, prefer `x.x` tags even when upstream examples show `x.x.x`, unless exact patch pinning is demonstrably required. Hard-coded dependency `x.x.x` tags in `docker-compose.yml` are policy drift and should be normalized before handoff.
17. Verify braced references: scan the touched `.env` and `docker-compose.yml` for any remaining bare `$VAR` reference (for example `grep -nE '\$W9_[A-Z_]+'`); fix every hit to `${VAR}` before handoff. A file that was touched must contain no bare `$VAR` anywhere.
18. Run the `deploy-validation` skill for the changed app.
19. Produce a short test report.

## Output

- files changed
- target version
- automated validation result
- risks
- owner E2E focus

## Rules

- Do not start implementation for a `review-first` candidate unless the owner has approved continuation.
- Keep the smallest correct change.
- The update is not a blind version bump. The changed app must still pass the current quality gates after the work is complete.
- Do not perform broad cosmetic template re-alignment. Fix only the app-local conformance items that are blocking, directly relevant to the update, or required by current gates and generators.
- Keep `upstream.image` as the single version source. Never write `version_from`, `fork_url`, or `requirements.url`.
- Prefer official or trusted upstream images.
- Produce the report in the same language the user used unless the user asks otherwise.
- Use `report-template.md` when the user asks for a formal implementation report.
