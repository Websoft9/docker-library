# Appstore Release Specification

| Property | Value |
|------|-----|
| Status | Root protocol 2; deployment gated pending consumer migration |
| Audience | docker-library maintainers, release owners, and consumer developers |

---

## 1. Core Model

`appstore` is this project's release target: an aggregate artifact containing two constituent datasets:

| Dataset | Content | Source of Truth |
|----------|------|--------|
| **catalog** | Application descriptions (names, categories, summaries, screenshot URLs, logo URLs, etc.) | Contentful |
| **library** | Installation templates (`variables.json`, `.env`, `docker-compose.yml`, etc.) | This repository's `apps/` directory |

**appstore is not a third independent source of truth**: it aggregates and publishes catalog and library.

### Help Fields

Help text in `variables.json` belongs in the `help` object (for example, `help.db`) for display in the interface:

- These are human-readable strings, not computational inputs.
- Computational facts come only from `.env` (for example, `W9_DB_VERSION`) and `metadata/`.
- `help` is an additive field; it does not modify or replace existing fields such as `requirements` or `externalDB`.

Rules for `help` fields:

- Each key contains a single-sentence string.
- State version-specific requirements in the same sentence, for example, `MySQL 8.0+ (7.0+ requires 8.4+)`.
- Do not introduce version-keyed objects and their additional maintenance burden.
- Complex login (for example, one-time initialization followed by fixed credentials) **must** declare `help.login`. The interface must display it **above** the credentials area so users read the instructions before logging in.
- `help.login` must not be omitted: the credentials area shows only the final credentials, leaving users unaware of prerequisite initialization otherwise.

### Credential Retrieval Metadata

`variables.json` may declare a machine-readable `credentials` object for consumers to retrieve dynamic administrator passwords, tokens, and other credentials after deployment.

- `credentials` is a structured declaration used by fixed consumer logic, not human-readable copy.
- It does not replace existing literal credentials in `.env`; if `W9_LOGIN_PASSWORD` is fixed, continue using `.env` directly.
- It supports stage groups (`initial` initialization credentials and `login` login credentials), as well as top-level single-stage slots (`username` / `password` / `token`, equivalent to `login` by default).
- For complex login (one-time initialization followed by fixed final credentials), declare the initial credentials in `credentials.initial` (for example, a temporary password from `container-log` or an unlock password from `container-file`), and the final credentials in `credentials.login` (for example, `container-env` referencing `W9_LOGIN_PASSWORD`). Retain `.env` fields `W9_LOGIN_USER` / `W9_LOGIN_PASSWORD` for the current frontend, and use `help.login` to explain the relationship between initialization and regular login.
- `credentials` describes only where to retrieve credentials; arbitrary host-level shell commands are not permitted in the repository.
- If an installation wizard creates the administrator account rather than the image provisioning one, declare `credentials.none: true` and omit `W9_LOGIN_USER` / `W9_LOGIN_PASSWORD`.

The current contract supports three fixed slots: `username`, `password`, and `token`. Each declares a source for its value, either directly under `credentials.<slot>` (single-stage shorthand) or under `credentials.initial.<slot>` / `credentials.login.<slot>` (stage groups).

Single-stage shorthand:

```json
{
  "credentials": {
    "username": {
      "source": "inline",
      "value": "admin"
    },
    "password": {
      "source": "container-file",
      "path": "/var/jenkins_home/secrets/initialAdminPassword"
    }
  }
}
```

Stage groups (separating `initial` initialization credentials from regular `login` credentials):

```json
{
  "credentials": {
    "initial": {
      "username": {
        "source": "inline",
        "value": "admin"
      },
      "password": {
        "source": "container-log",
        "match": "regex",
        "pattern": "username 'admin' and password '([^']+)'",
        "group": 1
      }
    },
    "login": {
      "username": {
        "source": "inline",
        "value": "admin"
      },
      "password": {
        "source": "container-env",
        "name": "W9_LOGIN_PASSWORD"
      }
    }
  }
}
```

Supported `source` values:

- `inline`: A value embedded directly in `variables.json`, suitable for fixed, nonsensitive login identifiers such as `username`.
- `container-env`: A value in the target application container's runtime environment; the consumer reads the declared `name`.
- `container-file`: A password in a text or structured file inside the target application container; the consumer reads `path` read-only, without assuming that `cat`, `sh`, or any particular userspace tool is available.
- `container-log`: A password in the target application container's logs; the consumer reads `docker logs <W9_ID>` and extracts it using `pattern`.
- `container-cli`: A password retrieved through the official read-only CLI inside the target application container; the consumer executes `argv` directly without shell concatenation.

Field rules:

- Every slot object (under `credentials.<slot>`, `credentials.initial.<slot>`, or `credentials.login.<slot>`) follows the same `credentialSource` contract:
  - `source=inline` requires `value`.
  - `source=container-env` requires `name`.
  - `source=container-file` requires `path`.
  - `source=container-log` requires `pattern`.
  - `source=container-cli` requires `argv`.
- `slot` currently permits only `username`, `password`, and `token`.
- Stage keys support `initial` (first initialization/preflight wizard credentials) and `login` (regular/final login credentials). Use these groups only when the application **has two known credential sets for different stages** (for example, initialization credentials for a wizard followed by package-provided fixed login credentials). For a single package-provided or retrieved credential set, use top-level `credentials.<slot>`, even if users are later prompted to change their password.
- Optional `format` supports `text`, `json`, and `env`.
- `format=json` requires `jsonPath`.
- `format=env` requires `key`.
- Optional `match` supports `substring` and `regex`.
- `match=regex` requires `group`.
- Optional `trim` defaults to `true` in the consumer.
- `credentials` is machine-readable; do not use free text or embed complete shell commands.
- `inline` is primarily for fixed, nonsensitive values; do not embed dynamically generated plaintext secrets in `variables.json`.
- `container-cli.argv` must be an argument array, not a complete shell string, and must not perform side effects such as password resets or creation.
- Legacy `W9_LOGIN_GET_PASSWORD` / `W9_LOGIN_GET_TOKEN` may remain as compatibility fallbacks, but adding them to new or modified apps is no longer recommended.

Examples:

```json
{
  "credentials": {
    "username": {
      "source": "inline",
      "value": "admin@example.com"
    },
    "password": {
      "source": "container-env",
      "name": "BOOTSTRAP_INFO",
      "format": "json",
      "jsonPath": "$.admin.password"
    }
  }
}
```

```json
{
  "credentials": {
    "token": {
      "source": "container-log",
      "match": "regex",
      "pattern": "Root Token:\\s*(.+)",
      "group": 1
    }
  }
}
```

```json
{
  "credentials": {
    "token": {
      "source": "container-cli",
      "argv": ["myapp", "admin", "show-bootstrap", "--json"],
      "format": "json",
      "jsonPath": "$.token"
    }
  }
}
```

### Declarative Secrets (`env.secrets`)

Some applications need **plaintext secrets** before startup, usually supplied through `.env` before `docker compose up`. `credentials` describes post-deployment retrieval, not pre-startup provisioning. `variables.json` therefore provides `env.secrets`, while `metadata/secret-rules.json` defines the shared rule dictionary published alongside `metadata/database-types.json`.

Simple fields declare the **variable name only**, while fields requiring a specialized encoding or signature use a **single-key rule object**:

```json
{
  "env": {
    "secrets": [
      "LOCAL_BACKEND_API_KEY",
      "OH_SECRET_KEY",
      { "SEMAPHORE_ACCESS_KEY_ENCRYPTION": "base64" },
      { "AIRFLOW__CORE__FERNET_KEY": "fernet" },
      "JWT_SECRET",
      { "ANON_KEY": "jwt:JWT_SECRET" },
      { "SERVICE_ROLE_KEY": "jwt:JWT_SECRET" }
    ]
  }
}
```

Supported declaration items (defined in `metadata/secret-rules.json`):

- `"KEY"`: Regenerate a random string with the `.env` default value's shape (preserving length and character classes across alphanumeric, hex case, hyphen-separated segments, and the fixed `sk-` prefix). Comma-separated lists (for example, Strapi `APP_KEYS=k1,k2,k3,k4`) regenerate each item independently by shape and rejoin with `,`.
- `{ "KEY": "base64" }`: Use the `random_bytes` generator with standard Base64 encoding. Decode the nonempty `.env` default value to determine byte length $N$, generate $N$ random bytes, and encode as standard Base64. The template length must be verified against the application's upstream requirements; Base64 does not imply a universal security minimum.
- `{ "KEY": "fernet" }`: Generate 32 random bytes and encode as URL-safe Base64 with `=` padding (standard 44-character Fernet key).
- `{ "KEY": "jwt:<SECRET_KEY>" }`: Decode the `.env` default JWT header and payload, update `iat` to the creation timestamp while preserving the original `exp - iat` duration, and sign with the generated value of `<SECRET_KEY>`.

Semantics (fixed across applications):

- The shared dictionary selects a `generator` and typed options (`encoding`, optional raw `bytes`, or `algorithm`); `description` is non-executable documentation. Omitted `bytes` means using the default template's decoded length. JWT declarations require the signing-key variable argument; byte profiles reject arguments. Unknown or invalid dictionary entries must fail, not fall back. Consumers must implement these generators; dictionary publication alone does not enable them.
- Supply a **nonempty default value** for each declared secret in `.env`, serving as its shape/byte-length/JWT payload template. Shared values and fixed protocol prefixes use existing variable references (for example, `string:${CKAN_API_TOKEN_SECRET}`) rather than independent randomization.
- The consumer generates values **when creating an instance** and writes them into its `.env`. Explicit user settings take precedence over cached values; installation retries reuse the same instance cache. This repository does not promise a generic regeneration interface; existing instances require application-specific rotation.
- **Recreation/redeployment must never automatically regenerate values**: changing keys on every `up` would invalidate data or encryption.
- Generated values must be safe in `.env`/Compose: **no `$`, spaces, `#`, or newlines** (`$` triggers Compose interpolation).
- Defaults are **placeholders/templates, not production keys**, and may be committed to Git. They must have the correct shape, byte length, or JWT claims.

`W9_POWER_PASSWORD` and `W9_RCODE` are **implicit platform fields** of this mechanism. Existing applications using `W9_POWER_PASSWORD` for database or login passwords need no repeated declaration. Application-specific signing or encryption keys must be declared in `env.secrets` rather than borrowing `${W9_POWER_PASSWORD}`.

Validation rules (`libs app-check --gate policy` and `--gate secrets`):

- Every declared key in `env.secrets` must exist in that application's `.env` with a nonempty default value.
- `libs app-check --app <app> --gate secrets` checks supported shape templates (at least 12 random characters per item), `base64`/`fernet`/`jwt:<SECRET_KEY>` rule templates, missing/empty references, cycles, and unsupported reference syntax.

See the [Application Secret Spec](app-secret-spec.md) for classification, consumer contract rules, and verification requirements.

Example (`openhands`):

`.env`

```env
LOCAL_BACKEND_API_KEY=Kx7Qm2TpR9wZb4HnV1sLc6Dg0Fj3YaQd
OH_SECRET_KEY=Pv5Rt8Wy2Nk7Mc4Xb1Lz6Df0Gh3Jq9Ue
```

`variables.json`

```json
{
  "env": {
    "secrets": ["LOCAL_BACKEND_API_KEY", "OH_SECRET_KEY"]
  }
}
```

### Pre-Login Steps (`setup.steps`)

Some applications require prerequisite actions before final login: viewing a one-time token in container logs,
reading an initialization password from a container file, running an official read-only CLI for bootstrap information, or opening an initialization wizard.

`variables.json` provides the `setup` object for these steps:

```json
{
  "setup": {
    "summary": "Optional overall summary",
    "steps": [
      {
        "id": "setup-token",
        "text": "View the container logs and copy the one-time setup token.",
        "action": {
          "type": "show-log",
          "service": "portainer",
          "tail": 50
        }
      },
      {
        "id": "setup-wizard",
        "text": "Open the page and complete the initialization wizard.",
        "action": {
          "type": "open",
          "access": "web"
        }
      }
    ]
  }
}
```

Frontend rendering order:

- The `setup` area must precede the login/credentials area.
- `setup.summary` is an optional overall summary.
- `setup.steps[].text` contains human-readable instructions for each step.

Supported v1 `action` types (closed vocabulary):

- `show-log`: Display the raw container logs of a Compose service; fields: `service`, optional `tail`.
- `show-env`: Display a container runtime environment variable; field: `name`.
- `show-file`: Display a container file or read a structured value; fields: `path`, optional `format=text|json|env`, and `jsonPath` / `key`.
- `show-cli`: Run an official read-only CLI in the container and display its output; fields: `argv`, optional `format=text|json|env`, and `jsonPath` / `key`.
- `open`: Open an application entry point; fields: `access`, optional `path`.

Container target rules:

- `show-env` / `show-file` / `show-cli` target the main application container (`${W9_ID}`) by default, consistent with existing `credentials` retrieval rules.
- `show-log` explicitly declares `service` because logs usually need to distinguish Compose services.

Unified `open` and `access` rules:

- `open` does not define its own host/port/scheme.
- `access` must reference an existing key in `variables.json.access` (for example, `web` / `admin` / `api`).
- The final URL's scheme/port come from `access[<key>]`.
- If declared, `action.path` overrides that access entry's default path; otherwise use `access[<key>].path` (default `/`).

Boundaries and non-goals:

- No `pattern` / `group` support.
- No arbitrary shell or host commands.
- No automatic execution of commands with side effects; v1 only renders instructions, displays values, and opens pages.
- No conditional branches, multi-result workflows, or state machines.

Responsibilities relative to `credentials`:

- `setup`: Noncredential instructions or page-entry guidance to view or complete before login (for example, opening a wizard).
- `credentials`: Credential retrieval declarations, using `credentials.initial` and `credentials.login` for distinct stages or top-level `username` / `password` / `token` for a single stage.

Migration guidance:

- When both one-time initialization credentials and fixed final login credentials exist (for example, `graylog`), prefer `credentials.initial` + `credentials.login` to distinguish them directly.
- When logs are unsuitable for regex credential extraction and only need displaying alongside wizard steps, use `setup.steps[].action.type=show-log`.
- Retain `help.login` to explain initialization and final login.

### Responsibility Boundaries

| This Project Owns | This Project Does Not Own |
|-----------|-------------|
| Maintaining installation templates under `apps/` | Providing an online appstore API |
| Fetching catalog data from Contentful | Deciding how downstream consumers (AppOS, Console) consume it |
| Assembling and publishing complete `appstore` artifacts to R2 | Coupling consumer logic into the release specification |
| Publishing current Appstore only; leaving retired destinations untouched | Maintaining or certifying legacy packages for old clients |

---

## 2. Version Semantics

The release system distinguishes three version concepts at the `catalog`, `library`, and `appstore` root levels:

| Version | Meaning | Change Trigger | Format |
|------|------|---------|------|
| `schemaVersion` | Structure and required behavior contract | Incompatible structure, interpretation, or required installation behavior | Monotonically increasing string (`"1"`, `"2"`, `"3"`) |
| `datasetVersion` | Data content snapshot version | **Any** content change | Content hash (first 16 hex characters of SHA-256) |
| `channel` | Stability channel | Release target | `dev` / `rc` / `release` |

`catalog`, `library`, and the `appstore` root each have an **independent** `datasetVersion`:

- `catalog.datasetVersion`: Computed from the checksums of the four catalog JSON files.
- `library.datasetVersion`: Computed from serialized `apps-index` content, including the shared database and secret-rule dictionary fingerprints; a change to either dictionary alone also produces a new version.
- `appstore.datasetVersion`: Computed from the contract configuration plus both component content versions. This identifies a combination, not a third independent dataset. A contract-only change also changes this fingerprint.

Maintainers edit `metadata/appstore-schema.json`; it is the sole source of current root/catalog/library contract numbers. The publisher reads it, and publisher tests derive expected current versions from it rather than repeating literals. The manifest examples below illustrate the migration, not a second version configuration. Routine compatible content updates change only generated fingerprints. A contract bump requires documenting the incompatible behavior; consumers implement it on their own upgrade schedule before accepting that contract. It does not require updating generic test expectations or every documentation example.

Root protocol 2 removes the product-version gate and requires component declarations and checks. The new library contract covers template declarations, `.env` conventions, shared dictionaries, and required installation behavior, including string/object `env.secrets`, random-shape generation, Base64/Fernet/JWT generation, reference resolution and instance-persistent keys. See [the secret contract](app-secret-spec.md). This migration uses library 2; historical code also used index 2 experimentally before reverting to 1. That experimental number alone does not establish compatibility with the current contract. Only consumers verified to implement the current contract are supported; historical clients are not maintained by this publication.

Release tags identify the source release, not consumer compatibility. Content fingerprints are generated; compatibility changes require an explicit maintainer decision. Once distributed, including to dev consumers, a contract must not gain incompatible requirements without a new version.

Thus **catalog-only description changes do not change `library.datasetVersion`** (and vice versa), allowing clients to identify exactly which dataset needs refreshing.

### 2.1 schemaVersion Compatibility Guarantee

Within a `schemaVersion`, follow an **additive-only** rule:

- Allowed: New fields, files, and app entries only when old implementations can safely ignore the additions.
- Prohibited: Removing existing fields, changing field types, or changing file-naming rules.
- Display-only fields may be ignored. New required execution behavior is not a compatible addition merely because the JSON remains parseable.

**Routine compatible changes update only `datasetVersion`, not `schemaVersion`.**

### 2.2 schemaVersion Upgrade Conditions

Upgrade only when one of the following occurs:
- Removing an existing field.
- Changing a field's type.
- Changing the file layout or manifest structure.
- Requiring new installation behavior, such as a secret generator old consumers cannot execute safely.

Publisher sequence: Document the incompatible change -> bump the affected contract -> validate and publish artifacts. Consumers independently implement and verify support before accepting the new contract; their deployment does not gate publication. Parallel publication of legacy formats is not required.

Optional database declarations were introduced under historical schema 1 without replacing an active product contract. Publication uses the configured library contract consistently in the library manifest, apps-index, apps-delta and embedded `library.json`. Root references repeat each component's schema and dataset versions; the publisher and consumer must verify agreement with the component manifest. New access formats or removal of required password conventions need another contract change; the current contract does not predeclare support for future proposals.

### 2.3 Consumer Compatibility

Consumers maintain their own supported `schemaVersion` list and check downloaded manifests:

```
if manifest.schemaVersion in SUPPORTED:
    consume normally
else:
    reject the update; retain a complete verified local snapshot if one exists
```

This follows the conventions of Helm (`apiVersion`), Docker Registry (`schemaVersion`), and OSTree (`summary.version`).

The publisher owns contract declarations and artifact integrity; each consumer owns its supported versions, upgrade schedule and update activation. Publication does not query consumer deployment status, change consumer configuration or require consumer approval.

Consumers explicitly declare implemented versions in one code module, not a user-editable setting, and must not automatically accept a version merely because the publisher configuration declares it. Before accepting an update, a consumer must support its root contract and the component contracts it consumes; it need not immediately implement every published contract. Reading a prior supported local snapshot for migration or recovery is optional and does not require continued legacy publication. Root 1 obtains component schemas from their manifests; root 2 requires agreement with root declarations. A consumer using the root always checks its protocol, but checks only components it consumes. A catalog-only site need not support the library contract.

Check contracts before any dataset-equality fast path. Compare `(schemaVersion, datasetVersion)` per component; snapshot identities must include root/consumed contract versions or use the protocol-2 combination fingerprint. Missing/corrupt local derived files are repair/sync failures, not evidence of incompatibility. Unsupported contracts report the actual unsupported version; do not claim a client upgrade exists without evidence.

No compatibility error, missing manifest, malformed response or checksum failure may bypass checks by downloading a legacy package. A cold start without a verified usable snapshot is unavailable, not a successful empty store. Already installed instances retain their configuration and keys; supporting them requires old-format readers and explicit app-specific upgrade handling.

---

## 3. Update Granularity

| Dataset | Granularity | Description |
|--------|------|------|
| **catalog** | Whole files | Any JSON change produces a new snapshot; no field-level delta |
| **library** | App level | The unit is `apps/<app>`; change types: `addedApps` / `changedApps` / `removedApps` |

`apps-delta` expresses only the **change scope**; individual app artifacts carry the actual incremental payload. Client update strategy:

1. First installation or local corruption -> download the full package.
2. Incremental update -> download only app packages in `addedApps` + `changedApps`.
3. `removedApps` -> remove locally.
4. Any app update failure -> recover using the full package.

When the library manifest declares `metadata.databaseTypes` (or `metadata.secretRules`), download its `path` and verify its `sha256` and checksum. Older schema 1 manifests may omit these optional entries. Each shared dictionary has a content-addressed filename. An app delta may be empty for dictionary-only changes, but the dictionary update must not be skipped. Validate apps and dictionaries in a temporary snapshot, then activate them together; on failure, retain or restore the last complete local snapshot. Unchanged app packages need no rebuild, and the dictionaries are not duplicated in every app package.

### 3.1 Channel Data Differences

For consistency with the legacy system, `dev` and `release` **do not have identical data scope**:

- `release`: Includes only Contentful product entries with `production=true`.
- `dev`: Does not filter `production`, so it includes more product entries for development, integration, and testing.
- All channels supplement `product_*.json` with `edition -> distribution` information from repository `apps/*/variables.json`, ensuring that version values use arrays.

Thus `dev` is a broader, richer dataset, while `release` is narrower and production-oriented; both use the same `distribution` structure.

### 3.2 Contentful Visibility Flags

`appStore` and `production` are independent visibility flags:

| App State | `appStore` | `production` | Result |
|---|---|---|---|
| Active public, ready for release | `true` | `true` | Visible in dev + release |
| Active public, development only (`variables.json.release=false`) | `true` | `false` | Visible only in dev |
| Internal (`scope=internal`) | `false` | `false` | Not visible in appstore |
| Archived | `false` | `false` | Not visible in appstore |

`production` derives from `release` in `apps/<app>/variables.json`; `appStore` derives from whether the app is active and public in scope. `catalog-push --apply` writes both fields when creating or updating Contentful entries, so they need not be repeated in `metadata/catalog/<app>.json`.

Changes to `metadata/catalog/*.json` receive dry-run validation in PRs. After merging to `main`, the `Sync data to Contentful` workflow runs `catalog-push --apply`.

### 3.3 Additional Product Fields

`ci/scripts/fetch_catalog.py` exports these optional fields to `product_en.json` and `product_zh.json`:

| Contentful Field | Exported JSON Key | Type |
|---|---|---|
| HasEnterprise | `hasEnterprise` | Boolean or null |
| Use Cases | `useCases` | String array or null |
| Keywords | `keywords` | String array or null |

The script requests these Field IDs directly in the existing product query, without schema introspection or dynamic aliases. Field IDs must match the Contentful model exactly; GraphQL query errors stop the export rather than silently dropping fields. Values, including false, empty lists, and null, are preserved without inferred defaults. These are additive catalog extensions; schemaVersion remains 1, and existing channel filters and localization rules are unchanged.

---

## 4. Artifact Model

### 4.1 R2 Directory Layout

```
artifact/appstore/<channel>/
├── catalog/
│   ├── manifest.json
│   ├── full/
│   │   └── latest.zip
│   ├── catalog_en.json
│   ├── catalog_zh.json
│   ├── product_en.json
│   ├── product_zh.json
│   └── *.sha256
├── library/
│   ├── manifest.json
│   ├── apps-index-<datasetVersion>.json
│   ├── apps-delta-<fromVersion>-to-<toVersion>.json
│   ├── metadata/
│   │   ├── database-types-<sha256>.json
│   │   ├── database-types-<sha256>.json.sha256
│   │   ├── secret-rules-<sha256>.json
│   │   └── secret-rules-<sha256>.json.sha256
│   ├── full/
│   │   └── latest.zip
│   └── apps/
│       └── <app>/
│           ├── latest.zip
│           └── latest.zip.sha256
└── manifests/
    └── appstore-manifest.json
```

### 4.2 Design Principles

| Principle | Description |
|------|------|
| Full-package fallback | Rebuilt for every release, for first installation, disaster recovery, and rollback |
| Channels expressed only by directories | `artifact/appstore/<channel>/` isolates `dev` / `rc` / `release`; v2 filenames do not repeat channel semantics |
| Catalog full package retains only latest | Catalog has stable JSON filenames and checksums; `full/latest.zip` is only for cold starts and fallback recovery |
| Library full package retains only latest | Consistent with catalog, v2 R2 retains no historical full snapshots, only `full/latest.zip` |
| Individual app packages use only `latest.zip` | No versioned packages; R2 is a distribution cache, while Git provides audit history |
| Incremental builds | Rebuild only `addedApps` + `changedApps`; leave unchanged apps untouched |
| Upload strategy | One SDK uploader backs up affected objects before writes and rolls back failed uploads; unchanged app packages remain untouched. `check_seed` detects the first release and triggers full seeding |
| No orphan accumulation | Only two files per app, requiring no scheduled cleanup |
| Images | v2 uses online URLs, not bundled binaries |

---

## 5. Manifest Contracts

### 5.1 appstore Root Manifest

```json
{
  "schemaVersion": "2",
  "datasetVersion": "2dccc0f5e5f0d21f",
  "channel": "release",
  "catalog": {
    "schemaVersion": "1",
    "manifest": "catalog/manifest.json",
    "datasetVersion": "7ee7a10b7da49f38"
  },
  "library": {
    "schemaVersion": "2",
    "manifest": "library/manifest.json",
    "datasetVersion": "85f687824c03ef93"
  },
  "generatedAt": "2026-06-09T12:00:00Z"
}
```

Consumers download this single file, check supported root/component contracts, then compare each consumed component's `(schemaVersion, datasetVersion)` to determine which datasets need updating.

### 5.2 catalog Manifest

```json
{
  "schemaVersion": "1",
  "datasetVersion": "7ee7a10b7da49f38",
  "source": "contentful",
  "fullPackage": "full/latest.zip",
  "files": {
    "catalogEn": "catalog_en.json",
    "catalogZh": "catalog_zh.json",
    "productEn": "product_en.json",
    "productZh": "product_zh.json"
  },
  "checksum": {
    "catalogEn": "catalog_en.json.sha256",
    "catalogZh": "catalog_zh.json.sha256",
    "productEn": "product_en.json.sha256",
    "productZh": "product_zh.json.sha256",
    "fullPackage": "full/latest.zip.sha256"
  },
  "generatedAt": "2026-06-09T12:00:00Z"
}
```

### 5.3 library Manifest

```json
{
  "schemaVersion": "2",
  "datasetVersion": "85f687824c03ef93",
  "channel": "release",
  "fullPackage": "full/latest.zip",
  "appsIndex": "apps-index-85f687824c03ef93.json",
  "appsDelta": "apps-delta-7ee7a10b7da49f38-to-85f687824c03ef93.json",
  "appPackagesBase": "apps/",
  "supportsPartialUpdate": true,
  "metadata": {
    "databaseTypes": {
      "path": "metadata/database-types-<sha256>.json",
      "sha256": "<sha256>"
    },
    "secretRules": {
      "path": "metadata/secret-rules-<sha256>.json",
      "sha256": "<sha256>"
    }
  },
  "checksum": {
    "fullPackage": "full/latest.zip.sha256",
    "appsIndex": "apps-index-85f687824c03ef93.json.sha256",
    "appsDelta": "apps-delta-7ee7a10b7da49f38-to-85f687824c03ef93.json.sha256",
    "databaseTypes": "metadata/database-types-<sha256>.json.sha256",
    "secretRules": "metadata/secret-rules-<sha256>.json.sha256"
  },
  "generatedAt": "2026-06-09T12:00:00Z"
}
```

### 5.4 apps-index Entry Structure

```json
{
  "app": "nginx",
  "name": "Nginx",
  "hash": "d80b08f74959...",
  "versions": ["1.26", "latest"],
  "path": "apps/nginx",
  "updatedAt": "2026-09-20T09:52:48Z",
  "package": { "latest": "apps/nginx/latest.zip" },
  "checksum": { "latest": "apps/nginx/latest.zip.sha256" }
}
```

Clients compare the `hash` field to detect app changes.

The apps-index root includes the same `metadata` dictionary fingerprints as the library manifest. Full packages retain the installation paths `library/metadata/database-types.json` and `library/metadata/secret-rules.json`. Content-addressed filenames serve incremental distribution without changing the installation paths. The removed `database-defaults.json` draft is not used for publishing or declaration resolution.

The library `datasetVersion` hashes the index's content fields, including app fingerprints and shared metadata, but excludes root `generatedAt`, app `updatedAt`, and the version field itself. Republishing identical content preserves the version; changing only the database or secret-rule dictionary changes it. Consumers must still check local shared metadata for missing or corrupt files even when the cached dataset version matches.

`updatedAt` is the last content-change time for the entire application template directory (`apps/<app>`), taken from the Git commit's author date in UTC. It is display-only ("last updated"), not an incremental-update input. Without usable Git history, fall back to this release's `generatedAt`.

---

## 6. Release Process

### 6.1 Triggers

| Event | channel |
|------|---------|
| Push to `main` | `dev` |
| Published GitHub Release (`release.published`, stable tag with its commit on `main`) | `release` |
| `workflow_dispatch` | Manually select `dev` / `rc` |

For a stable release, use GitHub **Releases -> Draft a new release**, select or create an `X.Y.Z` tag (for example, `0.9.0`, targeting main), then click **Publish release**. Pushing a tag or saving a draft does not publish artifacts; prereleases do not enter the stable channel. The Action checks out the published Release's tag, not the latest main at execution time. No committed version-number change is required. Do not use a `v` prefix or prerelease suffix, or move/overwrite stable tags.

Version sources:

- Stable releases: The tag name identifies the GitHub Release and the full package's embedded `library.json.Version`. Release attachments are the root manifest, its checksum and the changelog.
- dev/rc: Use `<channel>-<commit SHA>`, for example, `dev-abcdef123456`.
- Source code does not maintain the root `library.json`; releases generate it inside full artifacts for source traceability. It does not imply legacy uploads remain enabled.
- All three v2 `datasetVersion` values remain content-derived, independent of stable tag versions.
- Library deltas use the last successfully published apps index in the same channel, identified by that channel's published Appstore manifest. `fromVersion` is that index's library `datasetVersion`, not a Git SHA, release tag, or root Appstore version. Compare published and current app fingerprints to compute added, changed, and removed apps. Release tags still determine image-promotion baselines, not library dataset versions.
- Baseline readers accept current or earlier positive integer contract versions with the validated index identity/fingerprint shape. A different contract discards the incremental baseline after validation, rebuilds every app package and sets `supportsPartialUpdate: false` with `fromVersion: initial`. Same-contract baselines retain incremental behavior. Future/malformed schemas and invalid channel/version/app fingerprints remain publication errors. Accepting an old index for rebuild planning does not imply consumer support for installing that contract.
- Without a published baseline, build all app packages and set `supportsPartialUpdate: false`. Storage failures, malformed baselines, and checksum mismatches fail publishing rather than silently selecting a first publication.

### 6.2 CI Pipeline (`appstore-publish.yml`)

```
1. For release, compare build-input hashes between the current tag and the preceding reachable lower-version tag of a published stable Release (bare tags are not baselines). Invoke docker.yml only for changed custom images; skip it if none changed. The first release selects all buildable apps. Only selected-app image failures block Appstore artifacts.
2. Check out the release tag (fetch-depth: 0), resolve channel/version; validate stable tag format and main ancestry for release.
3. Read the channel's published Appstore manifest from R2, download its referenced library apps index and checksum, and verify version/channel/checksum. Pass it as --previous-apps-index. If no published manifest exists, select --all-apps without partial-update support.
4. Fetch catalog source data from Contentful.
5. Run `ci/scripts/library_publish.py` to build current Appstore artifacts only, normalizing product distribution structures from repository variables.json. Do not fetch bundled legacy logos/screenshots or build legacy distribution ZIPs.
6. Back up all R2 objects that this publication will overwrite; abort before any writes if backup fails.
7. Upload Appstore data packages and checksums, then component manifests, and finally the root manifest. Restore previous objects and delete newly created objects if any upload fails.
8. Use the existing short CDN TTL for current artifacts; do not purge frozen legacy objects.
9. Update the existing GitHub Release's generated changelog area and upload attachments, preserving manual notes.
```

The Action manages the Release body between `<!-- generated-changelog:start -->` / `<!-- generated-changelog:end -->`. Reruns replace only that area, preserving manual content outside it. The changelog uses the explicit commit range from the previous stable tag to the current tag. Only `published` triggers publishing; editing a Release description does not retrigger it.

Image candidates are identified by Dockerfile build-input hashes, preferably `dev-src-<hash>`. Historical candidates must come from successful main builds with inputs identical to this release. Do not guess a SHA from an arbitrary app's last commit or fall back to `dev-latest`. If a changed app lacks a candidate, manually run docker.yml from main (channel=dev, app, target_ref=release tag), then rerun the stable release. Missing images for historically unchanged apps require separate manual builds (same target_ref, dev then promote), not repeated attempts in later Releases. A separate callback creates a `bug` Issue after manual promotion failure, deduplicated by app + target ref; repeat failures append run links, and success requires manual closure. A matrix app failure does not cancel other apps, but blocks subsequent Appstore uploads.

Stable artifacts are published only to R2, with the GitHub Release updated alongside them. The Release becomes visible when Publish is clicked; this does not mean all downstream artifacts have finished publishing. Check the Action result.

After all stable-release uploads and the GitHub Release update succeed, send a WeCom notification using the same `WECOM_WEBHOOK` as maintenance scans, including the version, release-note summary, full Release, Appstore artifacts, and run links. Do not notify for dev/rc. Truncate summaries by UTF-8 byte limits. Shared `ci/scripts/wecom_notify.py` handles Markdown messages, API `errcode` checks, and bounded retries; each use case owns its message template. A missing webhook or failed notification produces a warning without affecting release success. Successful reruns send notifications again.

### 6.3 Upload Strategy

| Target | Command | R2 Path |
|------|------|--------|
| v2 catalog | S3 SDK | `appstore/<channel>/catalog/` |
| v2 library metadata | S3 SDK | `appstore/<channel>/library/` |
| v2 individual app packages | S3 SDK | `appstore/<channel>/library/apps/` |
| dev app version index | S3 SDK | `appstore/dev/library/apps-verson.json` |
| v2 manifests | S3 SDK | `appstore/<channel>/manifests/` |
| retired legacy library | No writes | `<channel>/websoft9/plugin/library/` |
| retired legacy media | No writes | `<channel>/websoft9/plugin/media/` |

`ci/scripts/appstore_upload.py` performs one backup-and-rollback upload. Existing R2 paths and filenames remain unchanged.

Before any remote operations, require all three manifests and their checksum files, and verify that each checksum matches its manifest bytes and filename. Missing, malformed or mismatched manifest checksums abort publication. Before any writes, download every existing destination object in the upload plan and preserve its content headers and custom metadata. Only explicit not-found responses identify new objects; permission, storage, and backup-download failures abort publication. Credentials require object read, write, and delete access, as well as the existing baseline-listing permission.

Upload packages, data, and checksums before component manifests. Write the root manifest checksum immediately before the root manifest, which is the final object. V2 objects retain `Cache-Control: public, max-age=60`. Unchanged app packages and unrelated destination objects are not modified.

On upload failure or a catchable interruption, restore every attempted existing object, including the failing upload, and delete attempted new objects. Any rollback failure is a publication failure, not success. The workflow retains the recovery journal and available old object copies in an `appstore-upload-backup-<channel>-<run>-<attempt>` diagnostic artifact for seven days. GitHub Release updates happen only after successful R2 upload; failures in those later steps do not roll back an already completed R2 publication.

This is compensating rollback, not an atomic multi-object transaction. Readers or CDN caches can still observe mixed versions during upload or rollback. A killed runner, an uncatchable termination, or a failed rollback can prevent restoration; diagnostic artifact upload also requires a live runner. Eliminating that window requires a separately agreed immutable-snapshot layout and single-entry-point activation. Consumers must reject inconsistent combinations and retain their prior snapshot. This change adds no Contentful writes.

---

## 7. Legacy Compatibility

Legacy library/media publication is retired for all channels. The workflow builds and uploads only the current Appstore under `appstore/<channel>/`. Existing legacy objects remain at their paths without maintenance or old-client compatibility guarantees; the publisher neither overwrites nor deletes them. Even stale local `legacy/` output must never enter the upload plan:

| Artifact | v2 Path | Legacy Path |
|------|--------|------------|
| catalog | `appstore/<channel>/catalog/` | `<channel>/websoft9/plugin/media/` (packaged as `media.zip`) |
| library | `appstore/<channel>/library/` | `<channel>/websoft9/plugin/library/` (packaged as `library-*.zip`) |

Historical media packages bundled `json/` + `logos/` + `screenshots/`. Current Appstore directories contain no image binaries and use online URLs instead. No historical package restoration, certification or old-client test matrix is required to publish current artifacts. This retirement does not certify that any retained package is usable.

Publication uses the normal dev/rc/release triggers and validates producer-owned artifacts. No consumer-readiness variables or approvals are required, including before stable image promotion. Consumer compatibility is checked by each consumer, not by this workflow.

Consumer maintainers independently test unsupported schemas, cold start without cache, dictionary-only changes, cross-contract full activation when migrating supported snapshots, interrupted updates, mixed CDN versions and unchanged installed instances. These are consumer acceptance checks, not publication prerequisites. Consumers must verify root/component/index versions and app hashes against the selected index before activation, with bounded retries on mixed versions. Checksums beside independently changing payloads alone do not prove a consistent combination. A verified compatible cached snapshot may remain usable after a failed update, but neither a compatibility failure nor a download failure may trigger a legacy download.

---

## 8. Validation Gates

Releases must pass all checks below; abort on any failure:

1. All four core catalog JSON files can be generated.
2. catalog/library/appstore manifests have complete, traceable fields.
3. `apps-index` and `apps-delta` can be generated, with app-level delta structure.
4. All checksums match actual files.
5. Individual app artifacts can be generated (`latest.zip` + `.sha256` for every changed app).
6. The root manifest is traceable to catalog and library.
7. Legacy destinations are absent from the upload plan.

---

## 9. Current Scope

| # | Item |
|---|------|
| 1 | Produce current Appstore only; preserve legacy destinations without writes |
| 2 | Add `artifact/appstore/<channel>/{catalog,library,manifests}` |
| 3 | Establish separate `schemaVersion` + `datasetVersion` at each of the three levels |
| 4 | Validate publication artifacts; leave compatibility and upgrade decisions to consumers |
| 5 | Fix library update granularity at app level |
| 6 | v2 catalog and library full packages output only `full/latest.zip`; individual app packages retain `latest.zip` |
| 7 | Cover all artifacts with manifests and checksums |
| 8 | Automatically seed the first release fully; build incrementally thereafter |

---

## 10. Industry References

This specification follows the **Static Artifact Repository** model (Helm Chart Repo, OSTree Summary, APT Repo):

| Feature | Reference | This Specification |
|------|------|--------|
| Index discovery | Helm `index.yaml` | `apps-index-{dsv}.json` |
| Incremental updates | OSTree static-deltas | `apps-delta-{from}-to-{to}.json` |
| Verification chain | APT `Release` + SHA-256 | `*.sha256` across all three manifest levels |
| Channel isolation | Debian stable/testing | `dev` / `rc` / `release` |
| Artifact signing | Phase 2 | Planned |

> **Phase 2 outlook**: Artifact signing (TUF/Helm provenance) and SLSA provenance attestations.

---

## 11. Consumer Guide

Consumers need no additional version-state file: **the manifest of the last successfully verified and activated snapshot is the state record**. A downloaded but unactivated manifest must never replace it. Compare a newly downloaded manifest with that cached manifest when updating; active snapshot files must still exist and pass validation.

### 11.1 First Installation (Cold Start)

```
1. Download appstore-manifest.json.
2. Check root protocol, fetch consumed component manifests, verify root/reference agreement,
   then check component contracts -> abort if incompatible.

3. Download the full catalog:
   -> Download catalog/manifest.json.
  -> Download full/latest.zip (fixed entry point).
  -> Verify full/latest.zip.sha256.
   -> Extract locally.

4. Download the full library:
  -> Download full/latest.zip (all app templates).
  -> Verify full/latest.zip.sha256.
  -> Stage library/apps/ and library/metadata/ (including both shared dictionaries) in a temporary local snapshot.

5. Download and cache apps-index-<datasetVersion>.json.
  -> Verify its contract/version against the library manifest; verify extracted app hashes and dictionaries against the index.
  -> Read each app's updatedAt (last template-change time).

6. Activate the validated snapshot, then save the downloaded appstore-manifest.json as the state record.
```

### 11.2 Incremental Updates

```
1. Download the latest appstore-manifest.json.
   Check supported contracts before the no-change fast path.

2. Compare the new manifest with the locally cached previous one:
   -> If catalog (schemaVersion, datasetVersion) differs:
       Download catalog/manifest.json -> compare checksums -> download changed JSON files.
   -> If library (schemaVersion, datasetVersion) differs:
       Download library/manifest.json and verify that its contract and datasetVersion match the root reference.
       Download and stage apps-index-<datasetVersion>.json.
         (This is the only source of updatedAt for unchanged apps.)
       if the library contract is unchanged and supportsPartialUpdate and the delta matches the cached and target library.datasetVersion:
         Download apps-delta -> stage changed/added app ZIPs and apply removals.
       else:
         Download and verify the full package; stage its apps/ and metadata/ together.
       Independently compare each metadata dictionary's sha256 with its local copy.
         Download its content-addressed path when changed, missing, or corrupt.
         Verify its SHA-256/checksum and stage it at the corresponding metadata logical path.
         Do not skip this step when addedApps/changedApps/removedApps are all empty.
   -> If all consumed contract/content pairs match:
       Still repair a missing/corrupt local dictionary using the library manifest's metadata entry.
       Otherwise, finish without downloading app packages.

3. Verify extracted app hashes against the selected index. Reject mixed root/component/payload versions
   and retry with a bounded policy. Activate consumed catalog/library changes and their indexes/dictionaries
   together, then replace the cached manifest.
```

**Typical Request Costs**:

| Scenario | HTTP Requests |
|------|----------|
| No changes | 1 (appstore-manifest.json, ~200B) |
| One catalog file changed | 3 (root manifest + catalog manifest + one JSON) |
| Two library apps changed; dictionary unchanged | 6 (root manifest + library manifest + apps index + delta + two ZIPs) |
| Dictionary also changed | One additional dictionary payload request |

> Counts exclude separate checksum requests and assume the local dictionary is intact. Library-update counts include the `apps-index` request used for per-app hashes and `updatedAt`.

### 11.3 Failure Recovery

```
If any incremental-update download or verification fails:
  -> Keep the last complete local snapshot and cached manifest unchanged.
  -> Optional fallback: Download and verify library/full/latest.zip into a temporary snapshot.
  -> Restore apps/, indexes and all declared metadata dictionaries together, never apps/ alone.
  -> Activate and advance cached state only after the complete fallback passes validation.

If a consumed schemaVersion is not locally supported:
  -> Do not update data; retain the previously cached manifest.
  -> Report the unsupported contract; offer an upgrade only when one is known to support it.
```

### 11.4 Recommended Cache Policy

| Resource | Recommendation | Reason |
|------|------|------|
| `appstore-manifest.json` | Cache-Control: 60s | Entry point; updates must be discovered promptly |
| `catalog/manifest.json` | Cache-Control: 60s | Very small, changes infrequently |
| `catalog/full/latest.zip` | Cache-Control: 60s | Cold-start/recovery entry point; replacements must become available promptly |
| `apps-index-*.json` | Cache-Control: 60s | App index and updatedAt; downloaded again only when datasetVersion changes |
| `apps-delta-*.json` | Cache-Control: 60s | Very small |
| `apps/{app}/latest.zip` | Cache-Control: 60s | Small templates; changes must become available immediately |
| `library/full/latest.zip` | Cache-Control: 60s | Fixed full-library entry point |
| `*.sha256` | Match the corresponding file | Cache checksums together with the files they verify |
| `catalog_*.json / product_*.json` | Cache-Control: 3600 | Descriptive data, changes moderately often |
