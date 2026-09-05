# Image Tag Spec

| Property | Value |
|---|---|
| Status | Adopted (draft until first E2E) |
| Applies to | app maintainers, AI workers, CI/CD maintainers |
| Purpose | Define where a Dockerfile lives, the single source of truth for image tags, and build/push ownership |

## 1. Dockerfile Location

- A custom image app MUST keep its `Dockerfile` at the app root: `apps/<app>/Dockerfile`.
- Build/runtime support files (entrypoint, config templates, scripts) stay under `apps/<app>/src/`.
- The Dockerfile references them with `COPY src/...`.
- Rationale: the image CI trigger and build context expect the root Dockerfile; keeping support files under `src/` matches the `new-app` template.
- `apps/<app>/src/Dockerfile` is NOT a valid location (no CI trigger, drifts from root copies).
- docker-compose.yml in an app package MUST NOT contain a `build` block (final users are pull-only).

## 2. Version Source Of Truth

- `.env` → `W9_VERSION` is the **single source of truth** for the version an app package runs AND for the image tag CI publishes.
- `variables.json` → `edition[].version[]` is the **supported-version list**: many values allowed, for scan/display only. It is NOT a tag source.
- Rule: `W9_VERSION` MUST be one of the community edition versions declared in `variables.json`.

## 3. Tag Rules

Read `W9_VERSION` (strip quotes) and publish to the app image repository (`W9_REPO`).

| Version form | Publish |
|---|---|
| contains `-` (e.g. `v2026.4`, `2026-05-20.143`) | only the exact version tag (`W9_REPO:v2026.4`) |
| semantic `x.y.z` (no `-`) | `W9_REPO:latest`, `W9_REPO:x`, `W9_REPO:x.y`, `W9_REPO:x.y.z` |

CI builds the image with `--build-arg <APP>_VERSION=${W9_VERSION}` so image content and tag always match. The Dockerfile's version ARG default must agree with `W9_VERSION`.

Dev / PR candidate images use a separate namespace so they never overwrite stable tags:

- primary: `W9_REPO:dev-<git-sha>`
- convenience alias: `W9_REPO:dev-latest`

## 4. Build And Push Ownership

- **Final users**: pull-only. No local build required.
- **Developers**: may build locally for verification; MUST NOT push to a shared registry.
- **CI**: the only party that pushes to the shared registry, using CI-managed credentials.
- **Shared build implementation**: `libs app-deploy` delegates any required image build to `libs app-build` (single implementation), so deploy and build never drift. Deploy never pushes images.
- **Shared rules entrypoint**: CI and manual operations derive tags/build-args from `libs app-build-plan`.
- **Controlled backdoor**: `libs app-build --push` is reserved for owner/maintainer use when CI cannot be used. Pushing stable tags outside CI requires explicit confirmation.

Developer local verification (no push required):

```bash
docker build -f Dockerfile --build-arg <APP>_VERSION=${W9_VERSION} -t ${W9_REPO}:${W9_VERSION} .
docker compose up -d
```

## 5. Maintenance

- This spec is repository-wide. Migration applies to the app being worked on; remaining apps migrate when touched.
- Branch promotion policy (dev builds, main promotes) is defined in `docs/git-workflow-spec.md`.
- CI tag channels (same repository, tag differs by branch):
  - `main` push → stable tags from `W9_VERSION` (see Tag Rules).
  - `dev` push → `dev-<git-sha>` (immutable) plus `dev-latest` (rolling alias).
- CI only builds apps whose Dockerfile declares `ARG <APP>_VERSION`; apps without it are not built by CI. Migrate them when touched.
