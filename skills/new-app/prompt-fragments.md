# Prompt Fragments

## Access Rule

Missing access blocks validation and publishing. Every package requires verified entries or confirmed no network entry; never use an empty array to disguise missing research.

Use `docs/app-access-spec.md` and run `libs app-check --app <app> --gate access`. Replace the scaffold port group with verified services, container ports, transport protocols, default publishing and endpoints. Empty entries mean confirmed no network entry; omission is unknown. Validate safe public paths/query, keep the primary group first, and never infer groups from URL helper variables or claim proxy support. Host ports and public URLs belong to native variables referenced by `rootUrl`, `host` and `mappedPort`, not to `W9_*_PORT_SET`, `W9_HTTP_PORT`, `W9_HTTPS_PORT`, `W9_URL`, `W9_URL_REPLACE` or `W9_ADMIN_PATH`.

## Exists Check Rule

Before anything else, load the CLI venv (`make install` if `.venv/` missing) and run `.venv/bin/libs list --include-archived --json`. If `<app>` is in the full list (active, archived, or internal), stop and report its key attributes (status, scope, cadence, update_policy), then ask the user to re-input a different name or terminate; existing apps go through the app-update or restore-app skill.

## Issue To Flags Rule

The issue is prose. AI reads it, extracts name, trademark, and official reference URLs, researches the image and version, then calls `.venv/bin/libs app-new` with flags. The CLI never reads GitHub or an issue body; it only validates flags and scaffolds.

## Template Rule

The machine scaffold source is `metadata/templates/new-app/`. Start from repository conventions and only add the minimum app-specific fields required by upstream.

## TODO Placeholder Rule

Omitted version/repo become explicit `TODO` placeholders in the generated files. Never pass fake values such as `latest` or the app name as the image repo.

## Validation Rule

Prove the app can be deployed, not just generated.

Database metadata follows `docs/app-database-connection-spec.md`: declare verified components as `database[]`, use `metadata/database-types.json`, and validate with `libs app-check --app <app> --gate database-metadata`. Omit declarations for apps without database components. Metadata is not database provisioning or connection-selection logic.

## Credential Source Rule

When an app does not control a fixed first admin username, password, or token in `.env` but the consumer can resolve it after deployment, declare declarative `variables.json.credentials.<slot>` metadata (or stage-grouped `credentials.initial.<slot>` / `credentials.login.<slot>` when initial bootstrap credentials differ from steady-state login credentials) where `<slot>` is `username`, `password`, or `token`. Supported sources are `inline`, `container-env`, `container-file`, `container-log`, and `container-cli`. Prefer this over embedding full commands in `W9_LOGIN_GET_PASSWORD` or `W9_LOGIN_GET_TOKEN`.
