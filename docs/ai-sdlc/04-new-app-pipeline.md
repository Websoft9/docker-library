# New App Pipeline

Trigger:
- owner opens a new app issue

Steps:
1. Issue provides `name` and `trademark`; an official reference URL (`docs.github`, `docs.image`, or `docs.install`) when known. AI researches missing upstream facts.
2. AI researches the real image, version, official install, and compose patterns.
3. AI creates the app from the machine template under `metadata/templates/new-app/`.
4. AI fills `.env`, `docker-compose.yml`, `variables.json`, `README.md`, `CHANGELOG.md`, and `src/`. Author the `access` port-group array per `docs/app-access-spec.md` and run `libs app-check --app <app> --gate access`. Replace scaffold assumptions using upstream evidence; never infer access from URL helper variables. Missing access is unknown, `[]` is confirmed no network entry. Host ports, public URLs and admin paths are mapped through `rootUrl` / `host` / `mappedPort` and `endpoints[].path` instead of `W9_*_PORT_SET`, `W9_HTTP_PORT`, `W9_HTTPS_PORT`, `W9_URL`, `W9_URL_REPLACE` or `W9_ADMIN_PATH`.
5. AI registers any new translatable env key in `i18n/translation.json`.
6. AI runs automated validation.
7. AI publishes the test report.
8. Owner runs final E2E.
9. Owner decides merge and release.

After merge:
- assign a maintenance cadence
- assign an update policy
- ensure Contentful metadata is ready for publish

Rule:
- new app flow uses the same quality gates as update flow
- update flow and new app flow both align the touched app to current repository gates, but update work should keep the smallest correct app-local change set
