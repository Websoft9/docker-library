# Git Workflow Spec

| Property | Value |
|---|---|
| Status | Adopted |
| Applies to | maintainers, AI workers, CI/CD maintainers |
| Purpose | Define branch roles, artifact channels, and minimum gates |

## 1. Branch Roles

- `main` is the only long-lived branch and the repository default branch.
- Feature, fix, and app-update work uses short-lived branches that target `main` via PR.
- There is no long-lived `dev` branch.
- `main` is protected: PR-only, squash merge, linear history, required `PR checks`.
- `main` is always the integration and release-ready branch. A release is a tag on `main`, not a separate branch.

## 2. Artifact Channels

- Push to `main` publishes the `dev` channel:
  - appstore artifacts under the `dev` channel
  - candidate images tagged `dev-<git-sha>` and `dev-latest`
- Publishing a stable GitHub Release with a semver tag such as `0.9.0` publishes the `release` channel (a tag push alone does not):
  - appstore artifacts under the `release` channel
  - stable images promoted from exact-context candidate tags before Appstore publication
  - existing GitHub Release changelog/assets updated
- Manual `workflow_dispatch` may choose the channel explicitly.

## 3. Image Strategy

- A `main` push builds candidate images for changed custom-image apps:
  - immutable: `dev-<git-sha>` (promotion target)
  - rolling alias: `dev-latest` (convenience only)
- A published stable Release does **not** rebuild. It promotes every custom app's exact-context candidate to stable tags. Main builds also record `dev-src-<Dockerfile-input-hash>`; legacy commit candidates require a successful main build and identical build inputs.
- Stable tags come from `W9_VERSION` (see `docs/image-tag-spec.md`).
- Promotion resolves and pins a manifest digest, never uses floating `dev-latest`, and fails with a backfill instruction when no matching candidate exists. Build a missing historical candidate manually at the release tag, then re-run the failed release jobs.

### Manual Runs

The image workflow (`workflow_dispatch`) targets one app and uses an explicit channel:

- `channel=dev` → build `dev-<sha>` + `dev-latest` for the chosen app
- `channel=promote` → promote the chosen app to stable tags; resolve an exact-context candidate unless an explicit `source_sha` is supplied
- runs from an unexpected branch or tag are not part of the normal flow

### Out-of-band Stable Images

A stable tag can also exist because someone pushed it directly (the `app-build --confirm-stable` backdoor).
The next promotion overwrites the stable tags it derives from `W9_VERSION`, always including `:latest`. Promotion:

- fails when the source `dev-<sha>` image is missing;
- warns (does not fail) when a target stable tag already points to a different digest, naming what will be overwritten.

## 4. Minimum Gates

Before a PR is merged into `main`:

- required `PR checks` pass (`maintenance-check`, CLI tests, build tests)
- deploy-validation for each changed custom-image app when applicable
- the PR is squash-merged; no direct pushes or merge commits

After publishing a GitHub Release:

- the promoted stable image exists
- `docker compose up -d` succeeds
- health or web entry responds

## 5. Rationale

- Build heavy custom images once on `main`; promote the exact-context image after publishing a Release.
- Keep one long-lived branch so integration does not drift.
- Use tags for release boundaries and auditability.
