# Upstream Spec

This spec defines how upstream facts are discovered for app maintenance.

## Goal

Separate:
- deterministic fact collection
- AI judgment and exception handling

Rule:
- CLI collects facts
- AI interprets facts and makes workflow decisions

## Scan Pipeline

The full update pipeline follows five layers:

1. Release index
   - read the upstream release page or git tags
   - collect known stable version numbers
   - skip prerelease and versions at or below the current version

2. Image verification
   - for each candidate from the release index, verify the image registry has a matching tag
   - candidates are tried from highest to lowest, so a slightly lower image tag wins when the newest has no image yet
   - prefer stable `x.x` image tags over patch tags

3. Structure layer
   - list all dependency images from the local `docker-compose.yml`
   - when `upstream.compose.compose` is declared, diff normalized compose structure
   - emit `compose-drift` facts: services, images, ports, volumes, depends_on, healthcheck, command

4. Research layer
   - AI reads official docs, release notes, and the official compose file
   - produces a change plan: which files to update and whether new pieces must be added

5. Decision layer
   - classify the change as patch, minor, major, or security
   - apply maintenance policy to choose `auto-update`, `review-first`, `defer`, or `skip`
   - owner confirms the final direction

New app flow reuses layers 3-5 and starts from the repository template.

## Source Types

CLI-first source types (inferred from URL patterns, no manual `type` field):
- `dockerhub-tags` - `hub.docker.com/...`
- `ghcr-tags` - `ghcr.io/...`
- `github-releases` - `github.com/.../releases`
- `github-tags` - `github.com/org/repo` (tags are the default GitHub source; no `/tags` suffix needed)
- `raw-compose` - compose files referenced by `upstream.compose.compose`
- `raw-env` - env files referenced by `upstream.compose.env`

AI-only sources:
- any URL listed under `upstream.docs` or found during research
- `human-readme`, `human-doc-page`, `dynamic-web-page`, `login-required-page` remain valid labels for documentation purposes only

Fallback rule:
- if CLI cannot parse a declared source, return `source-error`
- AI may then research and propose a corrected source
- `github-releases` falls back to `github-tags` when the repo publishes no releases

## Scan Outputs

CLI may emit:
- `version-change`
- `compose-drift`
- `config-drift`
- `source-error`

AI consumes these outputs and decides:
- `auto-update`
- `review-first`
- `defer`
- `skip`

## Minimal Upstream Descriptor

Role-based keys, no type fields. CLI infers the source type from URL patterns:

- `image`: image registry tag source (Docker Hub, GHCR, ...) - discover/verify
- `releases`: upstream project version list (GitHub releases/tags) - optional, enables the verified rollback ladder
- `compose.compose`: official compose file - enables compose drift
- `compose.env`: official env example file - enables config drift
- `docs`: URLs for AI research only, any page

Recommended new-app usage:

- always declare `upstream.image`
- add `releases` when the project publishes a reliable upstream release or tag list separate from the image registry, or when the extra source improves candidate verification and rollback confidence
- add `compose.compose` when upstream publishes an official compose file that is relevant to this package's topology comparison
- add `compose.env` when upstream publishes an official env example or config sample that is useful for config drift checks
- omit `releases`, `compose.compose`, or `compose.env` when the source does not exist, is unstable, or has not been verified yet; do not write empty placeholders
- keep `docs` for the human/AI research pages that explain install, upgrade, requirements, or architecture

Migration rule:
- `upstream.image` is the single version source; apps must declare it
- old keys `version_from`, `version_source`, `release_index`, `compose_source`, `config_source`, `ai_reference_sources` are no longer read and must not be written

For image-driven apps:

```json
{
  "upstream": {
    "image": "https://hub.docker.com/_/wordpress",
    "docs": [
      "https://github.com/docker-library/wordpress",
      "https://www.wordpress.org/docs/user_guide/en/install-requirements.html"
    ]
  }
}
```

For compose-driven apps:

```json
{
  "upstream": {
    "image": "https://hub.docker.com/r/example/project",
    "releases": "https://github.com/example/project",
    "compose": {
      "compose": "https://raw.githubusercontent.com/example/project/main/docker-compose.yml",
      "env": "https://raw.githubusercontent.com/example/project/main/.env.example"
    },
    "docs": [
      "https://github.com/example/project"
    ]
  }
}
```

For image-driven apps with a project version list (verified rollback ladder):

```json
{
  "upstream": {
    "image": "https://hub.docker.com/_/wordpress",
    "releases": "https://github.com/WordPress/wordpress-develop",
    "compose": {},
    "docs": [
      "https://github.com/docker-library/wordpress",
      "https://www.wordpress.org/docs/user_guide/en/install-requirements.html"
    ]
  }
}
```

Release index rule:
- when `releases` exists, it provides the list of known upstream versions
- CLI takes the top stable versions above the current version
- each candidate is verified against `image` before reporting
- unverified versions are not reported as image updates
- when a stable `x.x` image tag exists above the current version, it wins over patch tags

Rollback ladder:
1. verify candidates against `upstream.image`
2. fall back to `source-error` when the primary source fails
3. AI may then research and propose a corrected source

Rules:
- `url` must point to a stable upstream source
- CLI only handles declared source types
- AI does not replace declared deterministic scan paths in normal operation

## Drift Boundaries

`compose-drift` covers:
- services
- images
- ports
- volumes
- depends_on
- healthcheck
- command or entrypoint

`config-drift` covers:
- env keys
- default values
- required variables
- URL or login related config

## AI Fallback Boundary

When `libs drift` runs:
- always trust `dependency_images`
- trust `compose_drift` when status is `ok`
- trust `config_drift` when status is `ok`

When `compose_drift.status` or `config_drift.status` is:
- `not-declared`: AI may read official docs or propose a better upstream source
- `source-error`: AI may retry source discovery or propose a corrected source

AI SHOULD NOT redo the local dependency inventory or local compose parsing that CLI already produced.

## DB Lifecycle

Embedded database versions are decided from three layers:

1. `variables.json externalDB` - the app's verified requirement result (min / recommended / reason). It is a result cache, not the source of truth; humans or AI verify it against vendor docs and test it.
2. `metadata/db-lifecycle.json` - engine-level lifecycle facts (track and EOL per version), shared by all apps. Refreshed by `libs db-refresh` from the endoflife.date API; the read path treats snapshots older than 45 days as stale. Data changes are reviewed by PR like any data change.
3. Registry tags - tag availability, fetched by the CLI at assessment time (existing `dockerhub-tags` parser).

Schema of `metadata/db-lifecycle.json`:

```json
{
  "version": 1,
  "updated_at": "2026-08-20",
  "engines": {
    "mysql": {
      "source": "https://endoflife.date/api/mysql.json",
      "tracks": [
        { "version": "8.4", "track": "lts", "eol": "2032-04-30" },
        { "version": "9.7", "track": "lts", "eol": "2034-04-21" },
        { "version": "8.0", "track": "lts", "eol": "2026-04-30" }
      ]
    }
  }
}
```

- `track`: `lts` | `innovation` | `short-term` | `stable` (engine semantics; from vendor policy)
- `eol`: ISO date or null when open-ended
- keep rule: alive versions, plus recently EOL'd LTS versions (current or previous calendar year) for decision rationale

Decision rule:

- candidates = available tags ∩ (>= externalDB.min) ∩ alive in db-lifecycle
- LTS/stabled tracks rank above innovation/short-term
- untested majors above the vendor's documented/tested upper bound are not eligible (AI judgment from prose docs)
- the chosen version is recorded back into `externalDB.recommended` with a reason

Division of labor:

- CLI: current `W9_DB_VERSION`, declared min, lifecycle table, registry tags
- AI: vendor-tested upper bound, final pick, recording the verified result into externalDB

## Design Rule

Do not ask CLI to understand arbitrary webpages.

Do not ask AI to perform routine deterministic scanning when a stable source type exists.
