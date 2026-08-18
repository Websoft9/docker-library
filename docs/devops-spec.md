# DevOps Spec

| Property | Value |
|---|---|
| Status | Draft |
| Applies to | `docker-library` maintainers, AI workers, CI/CD maintainers |
| Purpose | Define automation boundaries, command contracts, and gate ownership |

---

## 1. Scope

This spec defines how repository automation is structured in `docker-library`.

It covers:

- app lifecycle actions
- automated validation and testing
- generated repository files
- version scanning
- publish artifact build
- external metadata sync

It does not cover:

- production operations
- cloud infrastructure governance
- owner final E2E judgment
- downstream consumer runtime behavior

---

## 2. Layers

### 2.1 Core Logic

Core logic is the single implementation of repository actions.

Examples:

- app create or archive
- metadata updates
- README generation
- `docker compose` validation
- deployment checks
- publish artifact assembly
- Contentful sync

Core logic MUST NOT contain:

- workflow orchestration
- release publishing
- R2 upload logic
- branch or approval policy

### 2.2 CLI

The CLI exposes core logic as a stable command interface for AI, CI, and local automation.

The CLI MUST:

- use explicit arguments
- return stable exit codes
- support human-readable output
- support `--json` for machine use

The CLI MAY support `--dry-run` for mutating commands.

The CLI MUST NOT contain:

- workflow trigger logic
- secret management policy
- GitHub release creation
- owner-only E2E decisions

### 2.3 Make

`make` is optional.

If present, it SHOULD only provide:

- short aliases
- common defaults
- small command wrappers

`make` MUST NOT be the primary implementation layer.

### 2.4 CI/CD

CI/CD is the orchestration layer.

CI/CD MUST own:

- triggers
- runner setup
- secret injection
- calling the CLI
- artifact upload
- release steps
- blocking policy

CI/CD MUST NOT duplicate repository logic already implemented in core logic or CLI.

### 2.5 Skills

Skills are shared agent workflows under `skills/`.

Skills MUST own:

- workflow steps and sequencing
- decision rules that need judgment
- report and handoff formats
- calling the CLI for deterministic actions

Skills MUST NOT:

- reimplement CLI logic
- contain agent-specific tool syntax
- make owner-only decisions

### 2.6 Layer Responsibilities

| Layer | Does | Does not do |
|---|---|---|
| Core Logic | implement repository actions once | orchestration, policy |
| CLI | expose core logic with stable args, exit codes, `--json` | decisions, approvals |
| Skills | agent workflow, judgment, calls CLI | reimplement CLI, own final E2E |
| Make | optional human shortcuts to CLI | primary implementation |
| CI/CD | triggers, secrets, artifacts, blocking | duplicate core or CLI logic |

---

## 3. Call Flow

Allowed call paths:

- Human -> `make` -> CLI -> core logic
- AI -> `skills/` -> CLI -> core logic
- CI/CD -> CLI -> core logic

Direct workflow calls to single scripts are allowed during migration, but the target state SHOULD be CLI-first.

---

## 4. Command Contract

Recommended CLI shape:

```bash
libs <action> [options]
```

Current first-version commands are app-default commands. Secondary resource groups may be introduced later only when they become stable first-class domains.

Rules:

- single app: `--app <name>`
- multiple apps: `--apps <a,b,c>` or repeated `--app`
- all targets: `--all`
- output path: `--output-dir`
- publish channel: `--channel`
- machine output: `--json`
- preview mode: `--dry-run`

Business inputs SHOULD be passed as arguments, not hidden in environment variables.

Environment variables MAY be used for:

- tokens
- secrets
- CI-injected context

Recommended exit codes:

- `0`: success
- `1`: validation or business failure
- `2`: invalid arguments
- `3`: external dependency failure
- `4`: missing prerequisite
- `5`: internal error

---

## 5. First-Version Commands

Implemented now:

```bash
libs list
libs info --app <name>
libs scan --selection due
libs check --app <name> --gate all
libs check --app <name> --gate structure
libs check --app <name> --gate policy
libs report --app <name>
libs archive --app <name> --dry-run
```

Planned next:

```bash
libs check --app <name> --gate deploy
libs check --app <name> --gate reachability
libs new --app <name>
libs docs-readme --app <name>
libs contentful-sync --app <name>
libs publish-build --channel dev
```

### 5.1 App Scope

`apps/<app>/variables.json` MAY declare `scope`:

- `public`: default; eligible for appstore publishing
- `internal`: maintained but excluded from appstore publishing

Rules:

- apps stay in `apps/` regardless of scope
- `internal` apps still participate in cadence, scan, check, and archive flows
- publishing pipelines filter on scope
- `release` remains the readiness flag, not the visibility flag

---

## 6. Quality Gate Ownership

Gate ownership MUST match `docs/ai-sdlc/05-quality-gates.md`.

| Gate | Executed by | Blocked by |
|---|---|---|
| Gate 0: Structure | CLI / AI / CI | CI |
| Gate 1: Policy | CLI / AI / CI | CI |
| Gate 2: Deploy | CLI / AI / CI | CI |
| Gate 3: AI Verification | CLI / AI | CI or task flow |
| Gate 4: Owner E2E | Owner | Owner |

Rules:

- Gates 0-3 MUST be executable through the CLI.
- Gate 4 MUST remain owner-only.
- CI SHOULD block on CLI results, not on duplicated YAML logic.

---

## 7. Version Tag Policy

Version selection rules for `W9_VERSION`:

- Prefer `x.x` tags when the upstream image publishes a stable `x.x` tag.
- Use `x.x.x` only when:
  - upstream does not provide a usable `x.x` tag, or
  - an exact patch pin is required for compatibility, migration safety, or a known upstream regression.
- Do not use prerelease tags unless the task explicitly targets prerelease testing.

These rules MUST apply to both manual edits and AI-driven update workflows.

---

## 8. Non-Goals

The CLI is not the place for:

- issue creation
- PR creation
- merge policy
- branch protection
- release approval
- owner E2E decisions

Those concerns belong to platform workflows or human process.

---

## 9. Adoption Order

Recommended order:

1. Normalize existing `build/*.py` inputs and outputs.
2. Introduce a thin unified CLI.
3. Update workflows to call the CLI.
4. Add `make` only if maintainers need local shortcuts.

Recommended first command groups:

1. `check`
2. `report`
3. `archive`
4. `list`
5. `scan`

---

## 10. Relation to Other Docs

This spec complements, and does not replace:

- `docs/architecture.md`
- `docs/ai-sdlc/*.md`
- `docs/appstore-release-spec.md`
- `docs/upstream-spec.md`

In short:

- architecture defines repository structure
- AI-SDLC defines process and gates
- appstore release spec defines publish artifacts
- upstream spec defines source types and scan fact boundaries
- this spec defines automation boundaries and command contracts
