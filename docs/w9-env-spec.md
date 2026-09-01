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
- expose user-editable ports
- describe app identity and networking
- model login credentials when the app has built-in auth
- model external URL replacement when the app needs a public URL during install or startup
- describe bundled dependency shape such as the main database type

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

### User-Editable Ports

These variables end with `_SET` and are intended for owner/user adjustment.

| Variable | Meaning | Typical use |
| --- | --- | --- |
| `W9_HTTP_PORT_SET` | External HTTP port | `- "${W9_HTTP_PORT_SET}:80" # Web Console` |
| `W9_HTTPS_PORT_SET` | External HTTPS port | `- "${W9_HTTPS_PORT_SET}:443" # HTTPS` |
| `W9_DB_PORT_SET` | External DB port for DB products | database packages only |
| `W9_MQ_PORT_SET` | External MQ port | MQ products |
| `W9_SSH_PORT_SET` | Extra SSH port | apps like GitLab |

Rules:

- expose only ports that users are expected to access directly
- do not publish bundled web-app dependency ports such as PostgreSQL or Redis unless the app itself is a database/service product
- every published port line in `docker-compose.yml` must carry an inline `# purpose` comment
- `_SET` keys are translatable and must exist in `i18n/translation.json`

### Internal Identity And Network

| Variable | Meaning | Typical use |
| --- | --- | --- |
| `W9_ID` | App instance identifier | main container name and dependency host prefix |
| `W9_NETWORK` | Shared Docker network name | always `websoft9` unless workflow explicitly says otherwise |
| `W9_HTTP_PORT` | Internal HTTP port | optional metadata/helper var |
| `W9_HTTPS_PORT` | Internal HTTPS port | optional metadata/helper var |

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

### URL And Login

| Variable | Meaning | Typical use |
| --- | --- | --- |
| `W9_URL` | Public host or host:port for the app | external URL placeholder |
| `W9_URL_REPLACE` | Enables init-time URL substitution when config references `${W9_URL}` | URL-aware apps |
| `W9_ADMIN_PATH` | Admin path suffix | `/admin`, `/wp-admin` |
| `W9_LOGIN_USER` | Built-in login username | admin/default-user apps |
| `W9_LOGIN_PASSWORD` | Built-in login password | paired with `W9_LOGIN_USER` |

Rules:

- declare `W9_LOGIN_USER` and `W9_LOGIN_PASSWORD` only when the app has built-in administrator credentials controlled by the package
- never declare only one of the login pair
- declare `W9_URL` for web apps
- set `W9_URL_REPLACE=true` only when app config or env actively references `${W9_URL}`
- typical URL-aware upstream keys include `ROOT_URL`, `BASE_URL`, `SITE_URL`, `APP_URL`, `PUBLIC_URL`, `EXTERNAL_URL`, `HOST`, `DOMAIN`, `PUBLIC_URI`

Examples:

```env
W9_URL=appname.example.com
W9_URL_REPLACE=true
ROOT_URL=http://${W9_URL}
```

```env
W9_URL=appname.example.com
W9_URL_REPLACE=true
AFFINE_SERVER_EXTERNAL_URL=http://${W9_URL}
```

### Password And Crypto Helpers

| Variable | Meaning | Typical use |
| --- | --- | --- |
| `W9_POWER_PASSWORD` | Shared generated password seed for bundled services | DB-backed packages, simple default credentials |
| `W9_ENCRYPT_PASSWORD` | Encrypted password representation | only when the upstream requires it |

Rules:

- use `W9_POWER_PASSWORD` only when it actually drives one or more app/dependency passwords
- do not keep dead helper variables in `.env`
- if the upstream has no package-controlled credential flow, omit these keys

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
3. protected appstore-facing block: `W9_ID`, internal ports, `_SET` ports, `W9_DB_*`, `W9_LOGIN*`, `W9_URL*`, `W9_ADMIN_PATH`, `W9_NETWORK`
4. upstream app environment variables under the bannered “image environment variables” section

Rules:

- keep the section banner and single Docs URL in the image env section
- the “Used by docker-compose.yml” subsection should contain only variables actively passed to containers
- keep “Not used by default” to at most 5 commented variables
- app/upstream variables should come after `W9_*` variables
- keep `W9_HTTP_PORT`, `W9_HTTP_PORT_SET`, `W9_URL`, `W9_URL_REPLACE`, `W9_ADMIN_PATH`, and `W9_LOGIN*` inside the protected block because current appstore parsing expects them there
- if `docker-compose.yml` mounts `./src/...`, the corresponding file must exist

## Variable Reference Style

When an environment variable is referenced as a value, use the braced form `${VAR}`.

Examples:

- `image: ${W9_REPO}:${W9_VERSION}`
- `container_name: ${W9_ID}`
- `- "${W9_HTTP_PORT_SET}:80" # Web Console`
- `name: ${W9_NETWORK}`
- `ROOT_URL=http://${W9_URL}`
- `W9_LOGIN_PASSWORD=${W9_POWER_PASSWORD}`

Rules:

- use `${VAR}` for every variable reference in `.env`, `docker-compose.yml`, and mounted config templates
- do not use the bare `$VAR` form in new or updated app packages
- the policy gate still accepts the legacy bare `$W9_URL` form, so existing packages pass without churn

## `W9_URL_REPLACE` Decision Rule

Use `W9_URL_REPLACE=true` when both are true:

1. the app needs a correct public URL during install, first startup, or URL generation
2. the package actively references `${W9_URL}` in upstream env/config wiring

Do not use it when:

- the app has no web URL concept
- the app is web-based but no packaged config references `${W9_URL}`
- the app URL is discovered externally and not wired through the package

Machine policy is enforced by `cli/libs/validate.py`:

- if `W9_URL_REPLACE` is set, `W9_URL` must also exist
- if `W9_URL_REPLACE` is set, `${W9_URL}` must appear in compose text or in an env value (the gate also accepts the legacy bare `$W9_URL` form)
- if a non-`W9_*` URL-aware key references `${W9_URL}`, `W9_URL_REPLACE` must be `true`

## `validate.py` Rule Mapping

The current policy gate reads `.env` and `docker-compose.yml` and enforces the following repository contract.

### Translation Keys

Source: `TRANSLATABLE_ENV_RE = ^(W9_.*_SET|W9_LOGIN.*)$`

Meaning:

- every `W9_*_SET` key must exist in `i18n/translation.json`
- every `W9_LOGIN*` key must exist in `i18n/translation.json`
- if a new key matches this regex, add the translation entry in the same change

### Login Pair

Source: `login_keys = (W9_LOGIN_USER, W9_LOGIN_PASSWORD)` and `len(login_keys) in (0, 2)`

Meaning:

- login keys are valid only when both are present or both are absent
- do not add only `W9_LOGIN_USER`
- do not add only `W9_LOGIN_PASSWORD`

### URL Declaration

Source: `url_declared_ok = "W9_URL_REPLACE" not in env_map or "W9_URL" in env_map`

Meaning:

- if you set `W9_URL_REPLACE`, you must also declare `W9_URL`

### URL Replace Detection

Source:

- `url_replace_required` becomes true when a non-`W9_*` URL-aware key references `${W9_URL}`
- `url_replace_required` also becomes true when compose text contains `${W9_URL}` (the legacy bare `$W9_URL` form is also matched)

Meaning:

- examples such as `ROOT_URL=http://${W9_URL}`, `APP_URL=http://${W9_URL}`, `AFFINE_SERVER_EXTERNAL_URL=http://${W9_URL}`, or compose values/comments containing `${W9_URL}` make URL replacement an active contract

### URL Replace Enforcement

Source:

- if `W9_URL_REPLACE` is set, then `${W9_URL}` must appear in compose text or an env value
- if `url_replace_required` is true, then `W9_URL_REPLACE` must equal `true`

Meaning:

- do not declare `W9_URL_REPLACE=true` unless the package really references `${W9_URL}`
- if the package references `${W9_URL}`, do not forget `W9_URL_REPLACE=true`
- for URL-aware file-mounted config, keep at least one explicit `${W9_URL}` reference in `.env` or compose so the gate can detect the contract

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

## Translation Rule

Keys requiring entries in `i18n/translation.json`:

- `W9_*_SET`
- `W9_LOGIN*`

Keys that normally do not require translation entries:

- `W9_REPO`
- `W9_DIST`
- `W9_VERSION`
- `W9_ID`
- `W9_NETWORK`
- `W9_DB_VERSION`
- `W9_DB_EXPOSE`
- `W9_URL`
- `W9_URL_REPLACE`

## Common Scenarios

### Simple Web App With Built-In Login

Use:

- `W9_HTTP_PORT_SET`
- `W9_URL`
- `W9_URL_REPLACE` only when app config references `${W9_URL}`
- `W9_LOGIN_USER`
- `W9_LOGIN_PASSWORD`

### Web App With Interactive First Admin Setup

Use:

- `W9_HTTP_PORT_SET`
- `W9_URL`
- `W9_URL_REPLACE` only when config/env references `${W9_URL}`

Do not add login pair unless the package really controls it.

### Web App With Bundled PostgreSQL Or MySQL

Usually add:

- `W9_DB_VERSION`
- `W9_DB_EXPOSE`
- dependency hostnames derived from `${W9_ID}`
- `W9_POWER_PASSWORD` only when the DB/app actually consumes it

### Non-Web Service

Usually add:

- image identity variables
- only the relevant `_SET` ports
- no `W9_URL`
- no login pair unless the service really has built-in credentials

## Pre-Edit Checklist For Agents

Before editing `.env` or `docker-compose.yml`:

1. read this document
2. read `metadata/templates/new-app/.env.tmpl`
3. check whether the app needs `W9_URL_REPLACE`
4. check whether login is package-controlled or interactive
5. use `${VAR}` for all variable references (never bare `$VAR`)
6. run `libs app-check --app <app> --gate policy` after edits
