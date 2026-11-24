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
   - keep the configured tag literal for reports and discovery (`v`, `.x`, `-lts`, `-core`, etc.); normalization is only for numeric comparisons
   - among newer stable tags, prefer the same variant tokens before version freshness, then partial token overlap, then other variants as fallback; plain tags prefer plain successors. Within the selected similarity tier, apply the minor-tag policy and choose the newest version
   - image-only channels such as `-lts`/`-core` are discovered from the registry rather than replaced by a plain release-index version; Docker Hub also queries the existing suffix so busy unrelated tags do not hide that channel
   - scans return up to three distinct stable newer image tags in that order; unavailable release-index candidates are omitted. `latest_version` remains the first recommendation, while `latest_candidates` contains the list. Review tables show the list with the first marked recommended; approval defaults to that first tag and owner edits remain authoritative
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
- `ecr-public` - `gallery.ecr.aws/...` or `public.ecr.aws/...`
- `registry-v2-tags` - Docker Registry HTTP API V2 / OCI-compatible registry URLs, including registry image references such as `registry.example.com/group/app`
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
- GitHub release/tag URLs used as the primary version source are read directly; a separate registry verification is only possible when `upstream.image` points to a supported image registry

## Network Failure Diagnosis

- Distinguish DNS resolution, connection, TLS, HTTP/authentication, and response-parsing failures. Record the source URL, runner environment, failure stage, and HTTP status when available.
- In Copilot Cloud, DNS or connection failures may be caused by the runner's outbound firewall or hostname allowlist. Check whether the upstream registry hostname is allowed; if it is missing, add that hostname to the applicable allowlist and retry from the same runner.
- A DNS failure alone does not prove an allowlist block or an invalid upstream URL. If the policy cannot be checked or the retry cannot confirm access, report the source as unavailable with the suspected environment limitation; do not interpret it as no update.
- HTTP responses such as `401` or `403` are not DNS failures. Preserve the status and registry authentication challenge so that authentication or authorization issues can be diagnosed separately.

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
- registry URLs may use the registry's web URL or its image reference; OCI-compatible registries are queried through the standard `/v2/<repository>/tags/list` endpoint, with bearer-token challenges handled from the registry response
- version matching uses the configured current tag to retain meaningful prefixes and variants, so tags such as `pg18-trixie` and `stable-11248` can be compared without treating arbitrary label numbers as versions
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

Public address settings use native variables declared in `variables.json.access`. Default
templates must not rely on the consumer substituting legacy URL or port aliases.

## AI Fallback Boundary

When `libs app-drift` runs:
- always trust `dependency_images`
- trust `compose_drift` when status is `ok`
- trust `config_drift` when status is `ok`

When `compose_drift.status` or `config_drift.status` is:
- `not-declared`: AI may read official docs or propose a better upstream source
- `source-error`: AI may retry source discovery or propose a corrected source

AI SHOULD NOT redo the local dependency inventory or local compose parsing that CLI already produced.

## DB Lifecycle

Embedded database versions are decided from three layers:

1. Official release notes or vendor documentation - the vendor-tested minimum and upper bound. `variables.json externalDB` remains user-facing verified help only and is never a computation input.
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

- candidates = available tags ∩ (>= vendor-tested minimum from official docs) ∩ alive in db-lifecycle
- LTS/stabled tracks rank above innovation/short-term
- untested majors above the vendor's documented/tested upper bound are not eligible (AI judgment from prose docs)
- record the chosen version and official references in the assessment; any verified `externalDB` help update remains separate from computation
- implementation rule: when the current bundled track is EOL and the vendor supports a newer alive LTS, update `W9_DB_VERSION` in the same app update; run `libs app-check --app <app> --gate database` and record the change in `CHANGELOG.md`

Division of labor:

- CLI: current `W9_DB_VERSION`, lifecycle table, registry tags
- AI: vendor-tested minimum and upper bound from official docs, final pick, recording the verified result in the assessment

## Design Rule

Do not ask CLI to understand arbitrary webpages.

Do not ask AI to perform routine deterministic scanning when a stable source type exists.

## Runtime Credential Metadata

Some apps generate an initial username, password, or token at first startup instead of taking it from `.env`,
or use separate credentials for first-time initialization (`initial`) and steady-state sign-in (`login`).
For these cases, app packages may declare machine-readable credential sources in `variables.json`.

Single-stage shorthand shape:

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

Two-stage shape (`initial` + `login`):

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

Rules:

- fixed slots are `username`, `password`, and `token`
- slots may be declared directly under `credentials.<slot>` (single-stage shorthand) or grouped by stage
  under `credentials.initial.<slot>` (one-time bootstrap/setup credentials) and `credentials.login.<slot>`
  (steady-state login credentials)
- `inline` means the credential value is stored directly in `variables.json`; use it mainly for fixed,
  non-sensitive values such as `username`
- `container-env` means the credential value is read from the target container runtime environment by `name`
- `container-file` means the password is stored in a file inside the target container; consumers should
  read `path` in a read-only way and must not assume `cat`, `sh`, or other specific user-space tools exist
- `container-log` means the consumer reads `docker logs <W9_ID>` output and extracts the password by
  `pattern`; `match=regex` with a capture `group` is allowed when a plain substring is not enough
- `container-cli` means the consumer runs a read-only in-container CLI command expressed as `argv`
  without shell wrapping; use this only when the app exposes an official credential-printing command
- `format=json` with `jsonPath` and `format=env` with `key` may be used for structured outputs
- keep this metadata declarative; do not store full shell commands in `variables.json`
- prefer `credentials.<slot>` (or `credentials.initial.<slot>` / `credentials.login.<slot>`) over the
  legacy `W9_LOGIN_GET_PASSWORD` or `W9_LOGIN_GET_TOKEN` when a touched app needs this behavior

## Access Metadata

`variables.json` access metadata declares how a user reaches the app. It records static
facts only: which entries exist, which Compose service and container port each targets,
and which wire protocol it speaks. It does not record hosts, domains, certificates,
reachability, or proxy capability.

Existing access values are unused development placeholders, not an enabled runtime contract.
They may be replaced or removed without preserving old keys or supporting both formats.
The Schema and CLI require the port-group shape below. Undeclared access remains unknown and
fails the access gate and publication; it must not be replaced with an unjustified empty array.
The library does not infer port groups or implement the downstream instance resolver.

### Supported Shape

```json
{
  "access": [
    {
      "id": "notebook",
      "service": "tensorflow",
      "port": 8888,
      "public": true,
      "endpoints": [
        {"roles": ["notebook"], "scheme": "http", "path": "/"}
      ]
    },
    {
      "id": "tensorboard",
      "service": "tensorflow",
      "port": 6006,
      "public": true,
      "endpoints": [
        {"roles": ["dashboard"], "scheme": "http", "path": "/"}
      ]
    }
  ]
}
```

- `access` is an ordered array of port groups (`[]` when the package exposes no network entry).
  Order it so the browser-facing groups (`kind == ui`) come first and the main one leads: install
  pre-fills a default domain for every group whose `endpoints[].roles` include a `ui` role, and the
  first of them becomes the instance primary domain. When the app has no `ui` role at all, the first
  URL-capable group is used instead. Pure `gateway`, `metrics` and internal `api` groups belong after
  the `ui` groups because they are not default domain targets. See [app-access-spec.md](app-access-spec.md).
- Each group requires `id`, `service`, `port`, `public`, and `endpoints`. `id` is the stable
  reference used by instance port settings, domain bindings and per-group gateway configuration.
- `port` is a container port and `protocol` (default `tcp`) is the transport; the same numeric
  port on TCP and UDP is two groups. Only default-active long-running services belong here, not
  one-shot `init` containers or disabled mutually exclusive profiles.
- `public` is the default host-publishing switch and must agree with the repository default
  `docker-compose.yml` mapping. `requireDomain` / `requireHttps` mark groups that cannot be
  reached by bare IP or must always use TLS.
- `rootUrl`, `host` and `mappedPort` list native environment variable names that receive the
  group's effective public URL, public host form and host port. Each name must be declared in
  `.env` and written by exactly one declaration. They are not platform aliases.
- Each endpoint requires `roles` and `scheme`. `roles` (functional purpose) and `scheme` (wire
  protocol) are orthogonal and validated against `metadata/access-types.json`; every role must
  allow that `scheme`. Order roles by `kind` (`ui` → `api` → `infra`). Merge roles when the
  service, resolved port, scheme, path and query describe the same endpoint.
  Kinds are role-derived groups for display and filtering, not connection methods or proxy
  capabilities.
- `service` is a Compose service name. Consumers resolve targets from the configuration used by
  the running instance, not unapplied `.env` changes. Compose-only mappings are expected
  configuration, not proof of a live address. Runtime lookup is scoped to the app instance,
  service, and enabled configuration. Inactive or absent containers are not ready; ambiguous
  targets are errors, not first-match choices.
- `path` and `query` are allowed only for path-capable schemes; `path` is an access path,
  not a proxy routing or rewrite rule.
- For reverse proxying, `http`, `https`, `ws` and `wss` endpoints are domain-binding candidates
  regardless of role or UI. The platform confirms proxy and app support and chooses routing;
  service/port equality does not prescribe how many domains to use.
- Do not declare internal cluster ports or WebRTC media transports as app access endpoints.
  Published media transports must be explicitly exempted in Compose per the access spec.
  Optional collection inputs intended for operator use can be declared with empty `endpoints`.
  Internal database dependencies belong to the `database` contract.
- `defaultScheme` and legacy fixed surface keys are rejected.
- Static checks compare target-service `ports` / `expose` evidence, per transport, from the
  default `.env`; explicit conflicts fail, missing evidence is reported as unverified.
  Deployment tests verify actual listeners, protocols, and access paths. Published mappings
  alone do not prove them.
- Endpoint paths follow the safety rules in the access spec.
  Query credential-field checks supplement, but cannot replace, review of public static values.

Structure and validation rules: [app-access-spec.md](app-access-spec.md).
Run `libs app-check --app <app> --gate access`; `app-info` and reports expose `access_metadata`.
