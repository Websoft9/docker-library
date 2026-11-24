---
name: new-app
description: Use when the user wants to add one new application package, create a new app from official deployment docs, or asks for a new app implementation workflow. Trigger phrases: new app, create app package, add app, 新应用, 新增应用.
---

# New App

Create one new repository app package from official upstream deployment references.

This skill follows `docs/ai-sdlc/04-new-app-pipeline.md`, `docs/ai-sdlc/05-quality-gates.md`, and `docs/ai-sdlc/06-test-report-format.md`.

Supporting files in this skill:

- `checklist.md`
- `prompt-fragments.md`
- `report-template.md`

## Inputs

Access declarations are required. Missing access blocks checks and publishing; an empty array is valid only after confirming no network entry, never as a substitute for research. Validate the current default version and enabled services, and recheck entries when listener configuration or user code changes.

Access follows `docs/app-access-spec.md` and `metadata/access-types.json`. Replace the scaffold's sample access declaration with verified Compose services, container ports, explicit protocols and real purposes. Confirm no network entry before using an empty array; omission is unknown. Run `libs app-check --app <app> --gate access`. Do not infer entries from `W9_URL` or claim live/proxy support from static metadata.

Database declarations follow `docs/app-database-connection-spec.md` and `metadata/database-types.json`. Use `database[]` for verified components, real Compose service names for internal providers, and native `datasource` mappings for external providers. Omit the field for apps without database components; exclude SQLite and etcd, and leave Memcached out until its scope is decided. Do not copy passwords, choose a connection, or create database objects from metadata. Run `libs app-check --app <app> --gate database-metadata` as well as deployment validation. Preserve the separate roles of `externalDB` help and database lifecycle facts.
Pre-startup internal secrets follow `docs/app-secret-spec.md` and `metadata/secret-rules.json`: declare plain `"KEY"` or a single-key object selecting `base64`, `fernet`, or `jwt:<SECRET_KEY>` in `variables.json` `env.secrets`, then run `libs app-check --app <app> --gate secrets`. Verify required lengths and encodings against upstream references; the shared profiles select a generator and typed options, not executable scripts. Websoft9 owns generation and persistence; confirm consumer support before delivery, and never treat a passing template gate as authenticated runtime evidence.

- app name (required)
- trademark (required)
- official references (required): at least one URL for the project repository, image registry, or install docs

If any required input is missing, stop and ask the user for it before researching or scaffolding. Never guess the trademark and never research without at least one official reference URL.

## Steps

1. Load the libs CLI venv first: run `make install` if `.venv/` does not exist, then run `.venv/bin/libs list --include-archived --json`. Get the most complete app list (active + archived + internal). If `<app>` is in the list, stop immediately and report its key attributes (status, scope, cadence, update_policy). Then route: active/frozen → `app-update` skill; archived → `restore-app` skill (`.venv/bin/libs app-restore`); or ask the user to provide a different app name / terminate. Do not create, modify, or overwrite anything.
2. Read the issue requirements and official upstream docs.
3. Read repository rules from `docs/code_owner.md`, `docs/w9-env-spec.md`, and the machine template under `metadata/templates/new-app/`.
4. Research the real image and version from upstream sources.
5. Scaffold the package skeleton with `.venv/bin/libs app-new --name <app> --trademark <brand> --json` plus `--version <x.x>` and `--repo <image>` when the research has already resolved them (otherwise the CLI writes explicit TODO placeholders). When upstream sources are known, also pass `--upstream-releases <url>`, `--upstream-compose <url>`, and `--upstream-env <url>` as applicable so `variables.json` starts with the current repository shape. The command refuses duplicates and runs the quality gates automatically.
6. Fill `.env`, `docker-compose.yml`, `variables.json`, `README.md`, `CHANGELOG.md`, and `src/` beyond the skeleton, following the scaffold todo list. Use `docs/w9-env-spec.md` as the canonical `W9_*` decision source; existing apps are secondary examples only. Enable the password group for DB/login apps; delete unused groups. Follow `docs/app-access-spec.md` for the access port-group array: one group per `(service, container port, transport)` with required `id`, `service`, `port`, `public` and `endpoints`, plus on-demand `requireDomain`, `requireHttps`, `rootUrl`, `host` and `mappedPort` native variable lists. Never add platform port or URL aliases (`W9_*_PORT_SET`, `W9_HTTP_PORT`, `W9_HTTPS_PORT`, `W9_URL`, `W9_URL_REPLACE`, `W9_ADMIN_PATH`): keep the container listener in `docker-compose.yml`, keep the host mapping as a literal default, and point `rootUrl` / `host` / `mappedPort` at the upstream native variables declared in `.env`. Put the browser-facing groups (`endpoints[].roles` containing a `ui` role such as `web`, `admin`, `dashboard`, `notebook` or `remote-desktop`) first with the main one leading: install pre-fills a default domain for every `ui` group and uses the first as the primary domain, while pure `gateway`, `metrics` and internal `api` groups stay out of the default domain set. If the app has no `ui` role, the first URL-capable group is used instead. Set `public` per `docs/app-access-spec.md` section 4.2: `true` only for the main browser UI, a database/cache/queue/search product's own service port, or a port the core feature needs the moment install finishes; `false` for collection/receiver ports, ports that need in-app setup first, internal coordination or cluster ports, `metrics`, and secondary or maintenance entries. Keep the upstream compose port mappings unchanged either way: `public` is the platform install/deploy policy, not a compose edit. In the image environment section, keep only required and user-facing essentials, the single Docs URL, vars actually used by Compose and up to 5 unused vars commented out. Mirror `metadata/templates/new-app/.env.tmpl`: preserve the section banner, Docs URL, "Used by docker-compose.yml" and commented "Not used by default" groups. Use braced `${VAR}` references throughout, not bare `$VAR`.
7. When the app needs a custom image, start from `metadata/templates/new-app/Dockerfile.tmpl` and keep the standard OCI labels (`org.opencontainers.image.*`) unless there is a documented exception.
8. Author `docker-compose.yml` so every published port line carries an inline `# purpose` comment, and never add `# image:` / `# docs:` source comments — the image and documentation sources live only in `variables.json` `upstream`. Update `variables.json` `upstream.image` as the single version source. Reference environment variables in the braced form `${VAR}` (for example `${W9_REPO}`); do not use bare `$VAR` in new files.
9. Register any new translatable env key in `i18n/translation.json`.
10. Healthchecks should default to the main app container only. Add healthchecks to sidecar or dependency containers only when the official upstream compose explicitly defines them or the task explicitly requires them.
11. If a credential or config env var only takes effect on first container startup (the image entrypoint uses a marker file, e.g. `webconsole.security.enabled`), record it in `variables.json` as `env.first_startup_only` (list of env names) so the README auto-renders the warning.
12. If the app creates its initial username, password, or token interactively and the consumer can resolve it after deployment, declare `variables.json.credentials.<slot>` metadata (or stage-grouped `credentials.initial.<slot>` / `credentials.login.<slot>` when initial bootstrap credentials differ from steady-state login credentials) where `<slot>` is `username`, `password`, or `token`. Supported sources are `inline`, `container-env`, `container-file`, `container-log`, and `container-cli`. When the image ships no preset admin and the account is created interactively, declare `credentials.none=true` instead of inventing `W9_LOGIN_*`. Prefer this declarative metadata over legacy `W9_LOGIN_GET_PASSWORD` / `W9_LOGIN_GET_TOKEN` command strings.
13. Keep `apps/<app>/CHANGELOG.md` as the single source of app change history. Use a pure-date heading `## YYYY-MM-DD` as the first-level heading for the initial change batch (the template already injects today's date); list the initial package changes below it. Do not duplicate changelog content into `README.md`.
14. Run `.venv/bin/libs app-gen-readme --app <app> --json` after metadata or README marker content changes so generated sections stay current.
15. For dependency images such as PostgreSQL, MySQL, MariaDB, Redis, or pgvector, prefer `x.x` tags even when upstream examples show `x.x.x`, unless exact patch pinning is demonstrably required. Hard-coded dependency `x.x.x` tags in `docker-compose.yml` are policy drift and should be normalized before handoff.
16. Author `apps/<app>/tests/cases.yml` per `docs/app-tests.md`: keep the built-in adaptive checks and add the minimum app-specific cases the defaults cannot cover, such as `http-basic` for an authenticated console or API, `web-access` for a dedicated health endpoint, or `script` only when built-ins are insufficient. Do not add a case that duplicates a default check.
17. Before validation, run fast preflights: probe registry/docs URLs with a 2s per-attempt budget and at most 2 retries, using the remote host's egress when local access fails; run `.venv/bin/libs app-check --app <app> --gate database`; `libs app-deploy` then auto-selects a free 9000-9999 port if a published port is occupied.
18. Run the `deploy-validation` skill to prove the app deploys.
19. Assign a maintenance cadence and update policy: write the app into the matching buckets of `metadata/maintenance.yaml` (apps not listed inherit the monthly/patch-minor defaults), and state the assignment in the report. The owner reviews it at merge.
20. Write the catalog working copy from the upstream research: copy `metadata/templates/catalog.json` to `metadata/.catalog/<app>.json` (run `libs catalog-pull --app <app> --json` instead when the app already has an entry) and fill trademark, summary, overview, description, websiteurl, screenshots, and `catalogBindings`. Choose `catalogBindings` from `metadata/catalog-taxonomy.json` when it exists; parent/child keys must be valid. Keep `summary` to at most 8 words (prefer 5 or fewer) and `overview` to at most 30 words (prefer 20 or fewer); the `catalog-seed` skill is the canonical reference for these limits. `metadata/.catalog/` is a gitignored local working copy and must not be committed. The owner seeds Contentful with `.venv/bin/libs catalog-push --app <app> --apply`; AI never writes Contentful directly. If the task is only catalog authoring for an existing app, use the `catalog-seed` skill instead of `new-app`.
21. After validation passes and the catalog working copy exists, sync the new app and its catalog data to the test server's websoft9 store: `.venv/bin/libs appstore-sync --app <app>`. The catalog source is the local `metadata/.catalog/<app>.json`, so the sync only carries it when this machine has the working copy. Preflight the `websoft9` container with a <= 10s check; when it is absent or unreachable, skip the sync and record it as skipped.
22. Produce a short test report.

## Output

- created files
- upstream references
- automated validation result
- risks
- assigned cadence and update policy
- owner E2E focus

## Rules

- Existence is decided by `.venv/bin/libs list --include-archived`, never by checking `apps/<app>/` alone; an archived or internal app also counts as existing.
- If `<app>` exists, stop at step 1, report its status/scope, and ask the user; never fall through to creation.
- The CLI input contract is `metadata/new-app.schema.json`; the issue itself is prose, AI converts it to flags.
- The CLI scaffold reads `metadata/templates/new-app/`.
- Prefer official images or trusted upstream images.
- Keep the app aligned to repository conventions.
- `variables.json` should declare the `upstream` structure explicitly when sources are known. `releases`, `compose.compose`, and `compose.env` should be considered during research and scaffold completion, but should be omitted when they are not applicable or not yet verified.
- Keep `upstream.image` as the single version source. Never write `version_from`, `fork_url`, or `requirements.url`.
- Do not change unrelated apps.
- Produce the report in the same language the user used unless the user asks otherwise.
