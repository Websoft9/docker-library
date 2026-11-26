# W9 Environment Variable Spec

This document is the canonical repository reference for `W9_*` environment variables.

Use it together with:

- `metadata/templates/new-app/.env.tmpl` for `.env` layout
- `cli/libs/validate.py` for machine-enforced policy
- `docs/devops-spec.md` for image tag policy

When examples in existing apps conflict with this document, prefer this document and the current validation rules.

## Scope

`W9_*` variables serve repository-level packaging and deployment conventions. They are not upstream app variables.

Typical uses:

- declare the main image and version
- expose non-port user-editable business parameters (`W9_*_SET`)
- describe app identity and networking
- model login credentials when the app has built-in auth
- describe bundled dependency shape such as the main database type

> Host port publishing, public URLs, and admin paths are NOT modeled via `W9_*` variables. Declare them in `variables.json.access` using literal default Compose ports and upstream native variables per [App Access Spec](app-access-spec.md).

## Always Read First

When creating or updating an app package:

1. read this document for `W9_*` semantics
2. mirror the `.env` section layout from `metadata/templates/new-app/.env.tmpl`
3. make the final package pass `libs app-check --app <app> --gate policy`

## Variable Groups

### Image Identity

| Variable | Meaning | Typical use |
| --- | --- | --- |
| `W9_REPO` | Main app image repository | `image: ${W9_REPO}:${W9_VERSION}` |
| `W9_DIST` | Edition or distribution label | `community`, `enterprise` |
| `W9_VERSION` | Main app image tag | primary app version source |

Rules:

- `W9_VERSION` is required for app packages
- prefer `x.x` tags when upstream publishes a stable `x.x` tag
- use `x.x.x` only when upstream has no usable `x.x` tag or exact patch pinning is required
- keep `upstream.image` in `variables.json` as the single version source reference

### User-Editable Business Inputs (`W9_*_SET`)

Non-port user-editable install parameters end with `_SET` (for example `W9_DEEPSEEK_API_KEY_SET` or `W9_KAFKA_BROKERS_SET`).

Rules:

- use `W9_*_SET` only for non-port business inputs collected at install time; host ports, public URLs, and admin paths live in `variables.json.access` (`W9_*_PORT_SET`, `W9_HTTP_PORT`, `W9_HTTPS_PORT`, `W9_URL`, `W9_URL_REPLACE`, `W9_URL_WITH_PORT`, and `W9_ADMIN_PATH` are prohibited)
- every published port line in `docker-compose.yml` must use a literal default host port (such as `"9001:80"`) or an upstream native port variable declared in `mappedPort`, and must carry an inline `# purpose` comment
- active `W9_*_SET` keys are translatable and must exist in `i18n/translation.json`

### Internal Identity And Network

| Variable | Meaning | Typical use |
| --- | --- | --- |
| `W9_ID` | App instance identifier | main container name and dependency host prefix |
| `W9_NETWORK` | Shared Docker network name | always `websoft9` unless workflow explicitly says otherwise |

Rules:

- `W9_ID` is required
- the main container should normally use `container_name: ${W9_ID}`
- dependency containers usually use suffixes such as `${W9_ID}-postgresql`, `${W9_ID}-redis`, `${W9_ID}-mariadb`
- app packages should use the external shared network with:

```yaml
networks:
  default:
    name: ${W9_NETWORK}
    external: true
```

### Login Credentials

| Variable | Meaning | Typical use |
| --- | --- | --- |
| `W9_LOGIN_USER` | Built-in login username | admin/default-user apps |
| `W9_LOGIN_PASSWORD` | Built-in login password | paired with `W9_LOGIN_USER` |

Rules:

- declare `W9_LOGIN_USER` and `W9_LOGIN_PASSWORD` only when the app has built-in administrator credentials controlled by the package
- never declare only one of the login pair
- when an application requires its public URL or hostname at runtime, declare the upstream native variable (for example `APP_URL`, `ROOT_URL`, `DOMAIN`) in `.env` with a runnable localhost/placeholder default and bind it via `rootUrl` or `host` in `variables.json.access` per [App Access Spec](app-access-spec.md)

### Password And Crypto Helpers

| Variable | Meaning | Typical use |
| --- | --- | --- |
| `W9_POWER_PASSWORD` | Shared generated password seed for bundled services | DB-backed packages, simple default credentials |
| `W9_ENCRYPT_PASSWORD` | Encrypted password representation | only when the upstream requires it |

Rules:

- use `W9_POWER_PASSWORD` only when it actually drives one or more app/dependency passwords
- do not keep dead helper variables in `.env`
- if the upstream has no package-controlled credential flow, omit these keys

### Declared Secrets

When a package ships plain-text secrets that are injected before `docker compose up`
(signing seeds, encryption keys, internal API tokens), declare them in `variables.json`:

```json
{
  "env": {
    "secrets": [
      "LOCAL_BACKEND_API_KEY",
      "OH_SECRET_KEY",
      { "SEMAPHORE_ACCESS_KEY_ENCRYPTION": "base64" }
    ]
  }
}
```

Rules:

- plain variable names regenerate a same-shaped random string (including comma-separated lists); single-key objects select a closed-vocabulary rule (`base64`, `fernet`, or `jwt:<SECRET_KEY>`)
- each declared name must exist in `.env` with a non-empty default template or supported variable reference; a template is not a production secret
- do not borrow `${W9_POWER_PASSWORD}` for application encryption or signing keys that have length or character-class constraints
- consumers regenerate values once on instance creation and overwrite the instance `.env`; redeploy must never auto-rotate them
- `W9_POWER_PASSWORD` and `W9_RCODE` remain implicit platform password seeds
- the canonical consumer contract lives in `docs/appstore-release-spec.md`
- new or changed secret inputs must pass `libs app-check --app <app> --gate secrets`; see `docs/app-secret-spec.md`

### Dependency Modeling

| Variable | Meaning | Typical use |
| --- | --- | --- |
| `W9_DB_VERSION` | Main bundled DB image tag | `postgres:${W9_DB_VERSION}`, `pgvector/pgvector:${W9_DB_VERSION}` |
| `W9_DB_EXPOSE` | Main database type used by the app | `postgresql`, `mysql`, `mariadb`, `mongodb`, `redis` |

Rules:

- use `W9_DB_VERSION` when the package bundles a primary database image and the tag should stay easy to update
- `W9_DB_VERSION` is not a translatable key
- `W9_DB_EXPOSE` describes the main bundled database/service type for operator understanding
- for dependency images such as PostgreSQL, MySQL, MariaDB, Redis, or pgvector, prefer `x.x` tags over hard-coded `x.x.x` tags unless exact patch pinning is required

Examples:

```env
W9_DB_VERSION=16
W9_DB_EXPOSE=postgresql
```

```env
W9_DB_VERSION=pg16
W9_DB_EXPOSE=postgresql
```

## `.env` Layout Contract

Mirror `metadata/templates/new-app/.env.tmpl`.

Recommended order:

1. image identity: `W9_REPO`, `W9_DIST`, `W9_VERSION`
2. optional password seed such as `W9_POWER_PASSWORD` when the package truly controls passwords
3. protected appstore-facing block: `W9_ID`, `W9_DB_*`, `W9_LOGIN*`, optional non-port `W9_*_SET`, `W9_NETWORK`
4. upstream app environment variables under the bannered “image environment variables” section

Rules:

- keep the section banner and single Docs URL in the image env section
- the “Used by docker-compose.yml” subsection should contain only variables actively passed to containers (or mapped via `access` `rootUrl` / `host` / `mappedPort`)
- keep “Not used by default” to at most 5 commented variables
- app/upstream variables should come after `W9_*` variables
- keep `W9_ID`, `W9_LOGIN*`, and `W9_NETWORK` inside the protected block
- if `docker-compose.yml` mounts `./src/...`, the corresponding file must exist

## Variable Reference Style

When an environment variable is referenced as a value, use the braced form `${VAR}`.

Examples:

- `image: ${W9_REPO}:${W9_VERSION}`
- `container_name: ${W9_ID}`
- `- "9001:80" # Web Console`
- `name: ${W9_NETWORK}`
- `W9_LOGIN_PASSWORD=${W9_POWER_PASSWORD}`

Rules:

- use `${VAR}` for every variable reference in `.env`, `docker-compose.yml`, and mounted config templates
- whenever `.env`, `docker-compose.yml`, or a mounted config template is edited, convert **every** variable reference in the whole file to the braced form `${VAR}`; do not leave bare `$VAR` on old, otherwise-untouched lines of an edited file

## `validate.py` Rule Mapping

The current policy gate reads `.env` and `docker-compose.yml` and enforces the following repository contract.

### Translation Keys

Source: `TRANSLATABLE_ENV_RE = ^(W9_.*_SET|W9_LOGIN.*)$`

Meaning:

- every non-port `W9_*_SET` key must exist in `i18n/translation.json`
- every `W9_LOGIN*` key must exist in `i18n/translation.json`
- if a new key matches this regex, add the translation entry in the same change

### Login Pair

Source: `login_keys = (W9_LOGIN_USER, W9_LOGIN_PASSWORD)` and `len(login_keys) in (0, 2)`

Meaning:

- login keys are valid only when both are present or both are absent
- do not add only `W9_LOGIN_USER`
- do not add only `W9_LOGIN_PASSWORD`

### Deprecated Access Variables Rejected

Source: `deprecated_access_env_keys = [key for key in env_keys if is_deprecated_w9_access_key(key)]`

Meaning:

- `.env`, `docker-compose.yml`, and `src/` must not contain `W9_*_PORT_SET`, `W9_HTTP_PORT`, `W9_HTTPS_PORT`, `W9_DB_PORT`, `W9_API_PORT`, `W9_URL`, `W9_URL_REPLACE`, `W9_URL_WITH_PORT`, `W9_ADMIN_PATH`, or `W9_LOGIN_ConnectURL`
- declare port groups, domain constraints, and native variable bindings (`rootUrl`, `host`, `mappedPort`) in `variables.json.access` per [App Access Spec](app-access-spec.md)

### Dependency Tag Policy

Source:

- non-variable dependency images matching `redis|postgres|postgresql|mysql|mariadb|pgvector`
- hard-coded patch tags matching `x.x.x...` are collected as policy drift

Meaning:

- `redis:7.0` is acceptable
- `postgres:${W9_DB_VERSION}` is acceptable
- `pgvector/pgvector:pg16` is acceptable
- `redis:7.0.7` is policy drift unless exact patch pinning is required and intentionally modeled

### Practical Editing Rule

When editing `.env` or `docker-compose.yml`, do not guess from old apps first. Instead:

1. read this spec
2. mirror `.env.tmpl`
3. run `libs app-check --app <app> --gate policy`
4. use existing apps only to fill a genuine gap not already covered here

## Login Variable Decision Rule

Add `W9_LOGIN_USER` and `W9_LOGIN_PASSWORD` when the package controls initial built-in credentials.

Examples:

- yes: apps that seed a known admin user/password from env
- no: apps that create the first admin interactively in the browser
- no: apps with no built-in auth

### Complex Or Multi-Stage Login

Some apps log in in two stages: a one-time bootstrap credential (often generated at first startup and
shown in the container logs or a bootstrap file) followed by a fixed account that the package controls.
Treat this as a complex login:

- keep the fixed final credential in `.env` as `W9_LOGIN_USER` and `W9_LOGIN_PASSWORD`; the current
  front end renders these directly
- group `variables.json.credentials` by stage using `credentials.initial` (for the one-time bootstrap
  credential, e.g. `source=container-log` or `source=container-file`) and `credentials.login` (for the
  steady-state login credential, pointing `password` at `W9_LOGIN_PASSWORD` with `source=container-env`
  instead of copying the literal value, so it follows `.env`)
- top-level `credentials.<slot>` remains valid as the shorthand when an app only needs a single credential
  set
- keep `variables.json.help.init` for the first-start steps (creating the administrator, reading a
  temporary password, running a bootstrap command) and `variables.json.help.login` for how to sign in
  once the credentials exist
- `help.init` is required whenever `credentials.initial` is declared or a slot uses `container-log` /
  `container-file`: when a front end renders only the final account and password from `.env`, users still
  need `help.init` to know how the initial bootstrap step works
- `help.login` is required whenever the app has a built-in account or token to sign in with, and must not
  repeat the initialization steps owned by `help.init`

## Translation Rule

Keys requiring entries in `i18n/translation.json`:

- non-port `W9_*_SET`
- `W9_LOGIN*`

Keys that normally do not require translation entries:

- `W9_REPO`
- `W9_DIST`
- `W9_VERSION`
- `W9_ID`
- `W9_NETWORK`
- `W9_DB_VERSION`
- `W9_DB_EXPOSE`

## Common Scenarios

### Simple Web App With Built-In Login

Use:

- `W9_LOGIN_USER`
- `W9_LOGIN_PASSWORD`
- upstream native public URL / host variable in `.env` (only when required by the app) bound via `rootUrl` or `host` in `variables.json.access`

### Web App With Interactive First Admin Setup

Use:

- `W9_ID`, `W9_NETWORK`, and image identity keys in `.env`
- port groups and endpoints in `variables.json.access`

Do not add login pair unless the package really controls it.

If the consumer can resolve a generated username, password, or token after deployment, prefer declaring a
machine-readable `variables.json.credentials.<slot>` source such as `inline`, `container-env`,
`container-file`, `container-log`, or `container-cli` instead of adding `W9_LOGIN_USER` /
`W9_LOGIN_PASSWORD` or the legacy `W9_LOGIN_GET_PASSWORD` / `W9_LOGIN_GET_TOKEN` command string.

### Web App With Bundled PostgreSQL Or MySQL

Usually add:

- `W9_DB_VERSION`
- `W9_DB_EXPOSE`
- dependency hostnames derived from `${W9_ID}`
- `W9_POWER_PASSWORD` only when the DB/app actually consumes it

### Non-Web Service

Usually add:

- image identity variables
- infrastructure port groups in `variables.json.access`
- no login pair unless the service really has built-in credentials

## Pre-Edit Checklist For Agents

Before editing `.env` or `docker-compose.yml`:

1. read this document
2. read `metadata/templates/new-app/.env.tmpl`
3. read `docs/app-access-spec.md` and keep host ports, public URLs and admin paths out of `.env`
4. check whether login is package-controlled or interactive
5. once you edit a file, use `${VAR}` for **all** variable references in it (never bare `$VAR`, even on lines you did not otherwise change)
6. scan the edited files for remaining bare `$VAR` references before handoff
7. run `libs app-check --app <app> --gate policy` after edits
