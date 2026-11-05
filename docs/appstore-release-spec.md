# Appstore Release Specification

| Property | Value |
|------|-----|
| Status | Implementation-ready draft |
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

Some applications need **plaintext secrets** before startup, usually supplied through `.env` before `docker compose up`. `credentials` describes post-deployment retrieval, not pre-startup provisioning. `variables.json` therefore provides `env.secrets`.

It **declares names only, not generation rules**:

```json
{
  "env": {
    "secrets": ["LOCAL_BACKEND_API_KEY", "OH_SECRET_KEY"]
  }
}
```

Semantics (fixed across applications):

- Supply a **plaintext default value** for each random seed in `.env`, also serving as its shape template. Shared values and fixed protocol prefixes use existing variable references rather than independent randomization.
- The consumer generates values **when creating an instance** and writes them into its `.env`. Explicit user settings take precedence over cached values; installation retries reuse the same instance cache. This repository does not promise a generic regeneration interface; existing instances require application-specific rotation.
- **Recreation/redeployment must never automatically regenerate values**: changing keys on every `up` would invalidate data or encryption.
- There is one generation rule: **produce a random string with the current value's shape (length and character classes)**. No length/charset rules are provided.
- Generated values must be safe in `.env`/Compose: **no `$`, spaces, `#`, or newlines** (`$` triggers Compose interpolation). The current consumer supports alphanumeric, hex, hyphen-separated segments, and the fixed `sk-` prefix; this does not promise general base64url, base64, UUID, or JWT generation.
- Defaults are **placeholders/shape templates, not production keys**, and may be committed to Git. They must have the correct shape and approximate production strength.

`W9_POWER_PASSWORD` is a **single-value special case** of this mechanism, equivalent to:

```json
{ "env": { "secrets": ["W9_POWER_PASSWORD"] } }
```

Existing applications using `W9_POWER_PASSWORD` therefore need no migration. When **multiple secrets with different shapes** are required, list their names in `env.secrets`.

Validation rules (`libs app-check --gate policy`):

- Every name in `env.secrets` must exist in that application's `.env`.
- Each default value must be nonempty.
- Added or modified secret declarations/sources must also pass `libs app-check --app <app> --gate secrets`, checking supported template formats, at least 12 random characters, missing/empty references, cycles, and unsupported reference syntax. At least 32 random characters are recommended for production seeds.
- During migration, `--gate secrets` is a separate strict gate, not included in existing `all`/`policy` aggregates. Passing legacy gates does not prove generation compatibility. Semaphore UI's known base64 template still fails; the first batch does not bypass that error.

Non-goals:

- No per-secret length/charset/pattern rules or template language.
- Secrets with specialized formats (check digits, derivation, or particular encodings) remain application-owned (init/entrypoint), outside `env.secrets`.

See the [Application Secret Spec](app-secret-spec.md) for classification, the current consumer format snapshot, repository scan boundaries, post-generation validation, and known specialized follow-ups. The rebuildable `metadata/secret-coverage.json` inventory is neither consumer configuration nor instance secret storage.

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
| Maintaining legacy and v2 during the transition | Not applicable |

---

## 2. Version Semantics

The release system distinguishes three version concepts at the `catalog`, `library`, and `appstore` root levels:

| Version | Meaning | Change Trigger | Format |
|------|------|---------|------|
| `schemaVersion` | Data structure contract version | Field removal, type changes, or file-layout changes | Monotonically increasing string (`"1"`, `"2"`) |
| `datasetVersion` | Data content snapshot version | **Any** content change | Content hash (first 16 hex characters of SHA-256) |
| `channel` | Stability channel | Release target | `dev` / `rc` / `release` |

`catalog`, `library`, and the `appstore` root each have an **independent** `datasetVersion`:

- `catalog.datasetVersion`: Computed from the checksums of the four catalog JSON files.
- `library.datasetVersion`: Computed from serialized `apps-index` content, including the shared database dictionary fingerprint; a dictionary-only change also produces a new version.
- `appstore.datasetVersion`: Computed from the combination of the two above.

Thus **catalog-only description changes do not change `library.datasetVersion`** (and vice versa), allowing clients to identify exactly which dataset needs refreshing.

### 2.1 schemaVersion Compatibility Guarantee

Within a `schemaVersion`, follow an **additive-only** rule:

- Allowed: New fields, files, and app entries.
- Prohibited: Removing existing fields, changing field types, or changing file-naming rules.
- Consumers must continue working when ignoring unknown fields.

**This means 99% of routine changes update only `datasetVersion`, not `schemaVersion`.**

### 2.2 schemaVersion Upgrade Conditions

Upgrade only when one of the following occurs:
- Removing an existing field.
- Changing a field's type.
- Changing the file layout or manifest structure.

Upgrade sequence: Announce in advance -> coexist during transition -> upgrade consumers -> retire the old format.

After migrating database connection declarations from objects to `database[]`, the library manifest, apps-index, apps-delta, and generated `library.json` use `schemaVersion: "2"`; catalog and root manifest structures remain version 1. The root manifest explicitly declares `library.schemaVersion` as version 2. Consumers must check the library contract; do not distribute new-format apps to old clients before upgrade, including through legacy download entry points. Schema compatibility for old objects does not prove that old clients support the new arrays.

### 2.3 Consumer Compatibility

Consumers maintain their own supported `schemaVersion` list and check downloaded manifests:

```
if manifest.schemaVersion in SUPPORTED:
    consume normally
else:
    fall back to the last successful datasetVersion snapshot and prompt for upgrade
```

This follows the conventions of Helm (`apiVersion`), Docker Registry (`schemaVersion`), and OSTree (`summary.version`).

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

Library version 2 also requires downloading `metadata.databaseTypes.path` from the manifest and verifying its `sha256` and checksum. The dictionary has a content-addressed filename. An app delta may be empty for dictionary-only changes, but the dictionary update must not be skipped. Validate apps and dictionary in a temporary snapshot, then activate them together; on failure, retain or restore the last complete local snapshot. Unchanged app packages need no rebuild, and the dictionary is not duplicated in every app package.

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
│   │   └── database-types-<sha256>.json.sha256
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
| Upload strategy | `aws s3 sync` (no deletion by default); `check_seed` detects the first release and triggers full seeding |
| No orphan accumulation | Only two files per app, requiring no scheduled cleanup |
| Images | v2 uses online URLs, not bundled binaries |

---

## 5. Manifest Contracts

### 5.1 appstore Root Manifest

```json
{
  "schemaVersion": "1",
  "datasetVersion": "2dccc0f5e5f0d21f",
  "channel": "release",
  "catalog": {
    "manifest": "catalog/manifest.json",
    "datasetVersion": "7ee7a10b7da49f38"
  },
  "library": {
    "manifest": "library/manifest.json",
    "datasetVersion": "85f687824c03ef93",
    "schemaVersion": "2"
  },
  "generatedAt": "2026-06-09T12:00:00Z"
}
```

Consumers download this single file and compare `catalog.datasetVersion` and `library.datasetVersion` to determine which datasets need updating.

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
    }
  },
  "checksum": {
    "fullPackage": "full/latest.zip.sha256",
    "appsIndex": "apps-index-85f687824c03ef93.json.sha256",
    "appsDelta": "apps-delta-7ee7a10b7da49f38-to-85f687824c03ef93.json.sha256",
    "databaseTypes": "metadata/database-types-<sha256>.json.sha256"
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

The apps-index root includes the same `metadata` dictionary fingerprint as the library manifest. Full packages retain the installation path `library/metadata/database-types.json`. Content-addressed filenames serve incremental distribution without changing the installation path. The removed `database-defaults.json` draft is not used for publishing or declaration resolution.

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

- Stable releases: The tag name is the sole version source for the GitHub Release, legacy `library.json.Version`, and `library-<version>.zip`.
- dev/rc: Use `<channel>-<commit SHA>`, for example, `dev-abcdef123456`.
- Source code does not maintain the root `library.json`; releases generate it for old-client compatibility and include it in full artifacts.
- All three v2 `datasetVersion` values remain content-derived, independent of stable tag versions.
- The release incremental baseline uses a stable version tag in the current commit history; without one, build all app packages.

### 6.2 CI Pipeline (`appstore-publish.yml`)

```
1. For release, compare build-input hashes between the current tag and the preceding reachable lower-version tag of a published stable Release (bare tags are not baselines). Invoke docker.yml only for changed custom images; skip it if none changed. The first release selects all buildable apps. Only selected-app image failures block Appstore artifacts.
2. Check out the release tag (fetch-depth: 0), resolve channel/version; validate stable tag format and main ancestry for release.
3. Check whether R2 apps/ is empty -> mark first release if empty (--all-apps).
4. Fetch catalog source data from Contentful.
5. Run `ci/scripts/library_publish.py` to build all artifacts (v2 + legacy), normalizing product distribution structures from repository variables.json.
6. Upload v2 artifacts to the new R2 paths (`channel` is directory-only; full-package entry points use `latest.zip`).
7. Upload legacy artifacts to the old R2 paths (for legacy consumers).
8. Purge Cloudflare caches.
9. Update the existing GitHub Release's generated changelog area and upload attachments, preserving manual notes.
```

The Action manages the Release body between `<!-- generated-changelog:start -->` / `<!-- generated-changelog:end -->`. Reruns replace only that area, preserving manual content outside it. The changelog uses the explicit commit range from the previous stable tag to the current tag. Only `published` triggers publishing; editing a Release description does not retrigger it.

Image candidates are identified by Dockerfile build-input hashes, preferably `dev-src-<hash>`. Historical candidates must come from successful main builds with inputs identical to this release. Do not guess a SHA from an arbitrary app's last commit or fall back to `dev-latest`. If a changed app lacks a candidate, manually run docker.yml from main (channel=dev, app, target_ref=release tag), then rerun the stable release. Missing images for historically unchanged apps require separate manual builds (same target_ref, dev then promote), not repeated attempts in later Releases. A separate callback creates a `bug` Issue after manual promotion failure, deduplicated by app + target ref; repeat failures append run links, and success requires manual closure. A matrix app failure does not cancel other apps, but blocks subsequent Appstore uploads.

Stable artifacts are published only to R2, with the GitHub Release updated alongside them. The Release becomes visible when Publish is clicked; this does not mean all downstream artifacts have finished publishing. Check the Action result.

After all stable-release uploads and the GitHub Release update succeed, send a WeCom notification using the same `WECOM_WEBHOOK` as maintenance scans, including the version, release-note summary, full Release, Appstore artifacts, and run links. Do not notify for dev/rc. Truncate summaries by UTF-8 byte limits. Shared `ci/scripts/wecom_notify.py` handles Markdown messages, API `errcode` checks, and bounded retries; each use case owns its message template. A missing webhook or failed notification produces a warning without affecting release success. Successful reruns send notifications again.

### 6.3 Upload Strategy

| Target | Command | R2 Path |
|------|------|--------|
| v2 catalog | `aws s3 sync` | `appstore/<channel>/catalog/` |
| v2 library metadata | `aws s3 sync --exclude "apps/*"` | `appstore/<channel>/library/` |
| v2 individual app packages | `aws s3 cp --recursive` | `appstore/<channel>/library/apps/` |
| v2 manifests | `aws s3 sync` | `appstore/<channel>/manifests/` |
| legacy library | `aws s3 sync` | `<channel>/websoft9/plugin/library/` |
| legacy media | `aws s3 sync` | `<channel>/websoft9/plugin/media/` |

All `sync` operations use the default add/overwrite behavior and do not delete existing destination files.

---

## 7. Legacy Compatibility

During the transition, legacy and v2 coexist through the **same workflow, using different R2 paths**:

| Artifact | v2 Path | Legacy Path |
|------|--------|------------|
| catalog | `appstore/<channel>/catalog/` | `<channel>/websoft9/plugin/media/` (packaged as `media.zip`) |
| library | `appstore/<channel>/library/` | `<channel>/websoft9/plugin/library/` (packaged as `library-*.zip`) |

**Legacy `media.zip` retains the old format**: `json/` + `logos/` + `screenshots/`, with images downloaded from Contentful URLs and bundled. v2 directories contain no image binaries and use online URLs instead.

Each push produces both artifact sets; retire legacy upload steps after the migration window closes.

---

## 8. Validation Gates

Releases must pass all checks below; abort on any failure:

1. All four core catalog JSON files can be generated.
2. catalog/library/appstore manifests have complete, traceable fields.
3. `apps-index` and `apps-delta` can be generated, with app-level delta structure.
4. All checksums match actual files.
5. Individual app artifacts can be generated (`latest.zip` + `.sha256` for every changed app).
6. The root manifest is traceable to catalog and library.
7. Legacy compatibility artifacts are complete.

---

## 9. Phase 1 Scope

| # | Item |
|---|------|
| 1 | Produce v2 and legacy in one workflow, with independent directory and naming rules |
| 2 | Add `artifact/appstore/<channel>/{catalog,library,manifests}` |
| 3 | Establish separate `schemaVersion` + `datasetVersion` at each of the three levels |
| 4 | Bring legacy library/catalog build logic back into this project |
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

Consumers need no additional state file: **the last successfully downloaded `appstore-manifest.json` is the complete state record**. Compare a newly downloaded manifest with the locally cached previous manifest when updating.

### 11.1 First Installation (Cold Start)

```
1. Download appstore-manifest.json.
2. Check schemaVersion compatibility -> abort if incompatible.

3. Download the full catalog:
   -> Download catalog/manifest.json.
  -> Download full/latest.zip (fixed entry point).
  -> Verify full/latest.zip.sha256.
   -> Extract locally.

4. Download the full library:
  -> Download full/latest.zip (all app templates).
  -> Verify full/latest.zip.sha256.
   -> Extract to the local apps/ directory.

5. Download and cache apps-index-<datasetVersion>.json.
  -> Read each app's updatedAt (last template-change time).

6. Save the downloaded appstore-manifest.json locally as the state record.
```

### 11.2 Incremental Updates

```
1. Download the latest appstore-manifest.json.

2. Compare the new manifest with the locally cached previous one:
   -> If catalog.datasetVersion differs:
       Download catalog/manifest.json -> compare checksums -> download changed JSON files.
   -> If library.datasetVersion differs:
       Download apps-index-<datasetVersion>.json and replace the local cache.
         (This is the only source of updatedAt for unchanged apps.)
       if supportsPartialUpdate:
         Download apps-delta -> download latest.zip for changed/added apps.
       else:
         Download the full package.
   -> If both match: Do nothing and finish.

3. After successful update, replace the cached manifest with the new one.
```

**Typical Request Costs**:

| Scenario | HTTP Requests |
|------|----------|
| No changes | 1 (appstore-manifest.json, ~200B) |
| One catalog file changed | 3 (root manifest + catalog manifest + one JSON) |
| Two library apps changed | 4 (root manifest + library manifest + delta + two ZIPs) |

> Displaying `updatedAt` adds one `apps-index` request to a library update (approximately 136 KB, or 24 KB gzipped).

### 11.3 Failure Recovery

```
If any incremental-update download or verification fails:
  -> Fallback: Download library/full/latest.zip and replace local apps/ completely.
  -> Replace the cached manifest with the downloaded manifest.

If schemaVersion is not locally supported:
  -> Do not update data; retain the previously cached manifest.
  -> Prompt the user to upgrade the client.
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
