# Official Installer Adoption Spec

| Property | Value |
|---|---|
| Status | Draft |
| Applies to | Websoft9 platform integrators, `docker-library` maintainers, AI workers |
| Purpose | Define how Websoft9 adopts and manages an upstream installer-managed deployment without owning the upstream `docker-compose.yml` |

## 1. Scope

This spec defines a second integration model for complex upstream applications whose official deployment is produced by an installer script or installer binary.

Examples:

- PostHog hobby self-host deployment
- other upstreams that generate a Docker Compose project at install time

This spec covers:

- install-time execution ownership
- post-install discovery and registration
- runtime management after adoption
- upgrade and re-adoption flow

This spec does not cover:

- replacing the upstream installer
- rewriting the upstream topology into a repository-managed app package
- owner final E2E judgment
- downstream UI design details

## 2. Problem Statement

Some upstream applications are no longer practical to maintain as a normal repository-managed app package under `apps/<app>`.

Typical reasons:

- the upstream deploy shape changes quickly
- install and upgrade logic include generated files, helper scripts, and migration orchestration beyond a static `docker-compose.yml`
- the upstream deployment is multi-service and tightly coupled to its own boot and migration process

For these applications, Websoft9 should manage the resulting deployment after install rather than own the upstream deployment files as a primary source of truth.

## 3. Integration Model

This spec introduces the `official-installer-adopted` integration model.

Definition:

- upstream installer owns deployment creation
- upstream-generated files are the runtime source of truth
- Websoft9 owns install invocation, discovery, registration, lifecycle actions, and re-adoption after upgrade

This differs from the normal repository app contract:

- repository-managed app: this repository owns `.env`, `docker-compose.yml`, `variables.json`, and app-local support files
- official-installer-adopted app: upstream owns the generated deployment files; Websoft9 stores only adoption metadata and optional thin adapters

## 4. Goals

- allow Websoft9 to support complex upstream stacks without maintaining a drifting copy of the upstream compose topology
- keep lifecycle actions consistent for the operator
- make adopted deployments discoverable and re-adoptable after upgrade
- isolate platform-owned metadata from upstream-owned deployment files

## 5. Non-Goals

- full normalization of installer-managed deployments into repository conventions
- guaranteed multi-instance support when the upstream installer does not support it
- forcing all internal dependency containers onto the shared `websoft9` network
- deep app-specific self-healing beyond the upstream installer and runtime model

## 6. Source Of Truth

For an `official-installer-adopted` deployment:

- upstream-generated deployment files are the runtime source of truth
- Websoft9 adoption metadata is a management cache, not the runtime source of truth
- repository docs or templates may describe the integration, but do not replace the upstream-generated deployment files

Implication:

- if platform metadata and runtime state disagree, the platform must re-discover from runtime state and upstream-owned files

## 7. Minimum Adoption Contract

An upstream deployment is adoptable only when all of the following are true:

1. the installer can be invoked in a controlled working directory
2. the resulting deployment is identifiable as a Docker Compose project or equivalent multi-container unit
3. the install directory can be persisted and revisited later
4. the platform can determine a main entrypoint for user access
5. the platform can execute start, stop, restart, status, and logs against the adopted unit
6. the platform can identify key stateful volumes or storage locations
7. the platform can re-run or invoke the upstream upgrade path
8. the platform can re-discover metadata after upgrade

If any of these are missing, the app is not a good candidate for this model.

## 8. Install Execution Responsibilities

Websoft9 owns the installer execution wrapper.

The wrapper must:

- create or select the target install directory
- inject installer inputs such as domain, version tag, and optional feature keys
- capture install logs
- detect install success or first blocking failure
- record the effective working directory used for installation

Rules:

- the wrapper should prefer non-interactive invocation when upstream supports it
- the wrapper must not assume the upstream installer supports explicit path parameters
- when the installer is directory-sensitive, the wrapper must control the working directory before invocation

## 9. Adoption Discovery

After a successful install, Websoft9 must discover the deployed unit instead of assuming fixed names.

Minimum discovery fields:

- app type
- integration model: `official-installer-adopted`
- install root directory
- primary compose file path
- effective env file path if present
- compose project name
- compose working directory
- main entrypoint service name
- main access surface: scheme, host, port, path
- service inventory
- stateful volumes or storage paths
- primary database service if any
- object storage service if any
- upstream upgrade command or upgrade entrypoint

Preferred discovery sources:

- generated files in the install root
- `docker inspect` labels
- `docker compose config`
- runtime container inventory

## 10. Registration Model

The platform should register adopted deployments in machine-readable metadata.

Recommended registration fields:

```json
{
  "app": "posthog",
  "integration_model": "official-installer-adopted",
  "instance_id": "posthog-001",
  "install_root": "/opt/websoft9/adopted/posthog/posthog-001",
  "project_type": "compose",
  "project_name": "posthog_001",
  "compose_file": "/opt/websoft9/adopted/posthog/posthog-001/docker-compose.yml",
  "env_file": "/opt/websoft9/adopted/posthog/posthog-001/.env",
  "entry_service": "proxy",
  "access": {
    "scheme": "https",
    "host": "posthog.example.com",
    "port": 443,
    "path": "/"
  },
  "services": ["proxy", "web", "worker", "db"],
  "volumes": ["postgres-data", "clickhouse-data"],
  "database": {
    "service": "db",
    "type": "postgresql"
  },
  "upgrade": {
    "command": "./posthog/bin/upgrade-hobby"
  }
}
```

Rules:

- registration metadata must be rebuildable from discovery
- registration must not be the only place where critical runtime facts exist

## 11. Runtime Management Responsibilities

After adoption, Websoft9 must manage the deployment as a project unit, not as a single fixed container name.

Minimum supported actions:

- status
- start
- stop
- restart
- logs
- open main entrypoint
- inspect current service list

Rules:

- runtime actions should target the compose project or equivalent unit
- platform logic must not require a fixed `container_name`
- platform logic should prefer project-scoped commands over raw container-scoped commands

## 12. Network Model

Installer-managed deployments may keep their internal dependencies on private project networks.

Rules:

- the platform must not require every service to join `websoft9`
- only the adopted deployment's main entrypoint needs a platform-visible access path
- platform access may be achieved by host port binding, reverse proxy, or a thin adapter
- internal databases and dependency services may remain on private networks

## 13. Upgrade And Re-Adoption

Upgrade is a first-class part of this model.

Rules:

- the platform should invoke the upstream-supported upgrade path instead of reimplementing it
- after upgrade, the platform must run discovery again
- changes in service inventory, volume inventory, or access shape must refresh registration metadata
- if re-discovery fails, the deployment remains installed but adoption status becomes degraded or blocked

Minimum post-upgrade checks:

- compose project still resolvable
- entry service still reachable
- access surface still valid
- stateful services still present

## 14. Thin Adapter Layer

The platform may apply a thin adapter layer when necessary.

Examples:

- attach only the public entrypoint to the `websoft9` network
- add a reverse-proxy or management sidecar
- add labels or metadata files needed for platform discovery

Rules:

- adapters must be minimal
- adapters must not replace the upstream deployment as the primary source of truth
- adapters should be re-applicable after upgrade
- adapters must avoid deep rewrites of upstream service topology

## 15. Multi-Instance Expectations

This model does not guarantee multi-instance support by default.

Rules:

- instance isolation is supported only when the upstream installer can be safely run in separate directories and with non-conflicting ports or domains
- path isolation, port planning, and domain planning are platform responsibilities
- if the upstream installer is effectively single-instance, the platform must treat the app as single-instance unless an adapter layer adds safe isolation

## 16. Validation Requirements

An adopted deployment should still pass a minimal validation workflow.

Minimum checks:

- installer exited successfully or reached the documented success state
- compose project exists
- expected services are running or healthy
- main entrypoint is reachable
- logs show no blocking startup error
- upgrade path can be identified

These checks are different from the standard repository `apps/<app>` package validation and should be implemented separately.

## 17. Failure States

The platform should model at least these adoption states:

- `installing`: upstream installer still running
- `adopted`: install succeeded and discovery metadata is valid
- `degraded`: deployment exists but some discovery or runtime facts are stale or partially invalid
- `upgrade_in_progress`: upstream upgrade running
- `blocked`: install or re-adoption failed with a first blocking error

## 18. Security Boundaries

Rules:

- the platform must not expose internal dependency services by default only for convenience
- secrets generated by the upstream installer remain upstream-owned runtime secrets
- any platform-side registry of adopted metadata must store only what is required for management
- installer logs may contain sensitive values and must be handled as operational secrets

## 19. PostHog Application Note

PostHog hobby self-hosting is a reference candidate for this model because:

- the official deployment is installer-managed
- the upstream deploy shape includes generated files, helper scripts, and migration orchestration beyond a static compose file
- direct repository maintenance of a drift-free local compose copy is high-cost

Expected PostHog-specific adoption concerns:

- installer working directory controls install path
- installer does not automatically avoid host port conflicts
- runtime shape may change across upgrades
- clickhouse, storage, and migration boot order are installer-coupled

## 20. Open Questions

- should adopted deployments have a repository descriptor file for operator docs only
- how much of the registration metadata should also be rendered into appstore artifacts
- whether the platform should provide a generic adopted-compose inspector command
- whether a generic database GUI sidecar should be attachable to adopted private networks on demand
