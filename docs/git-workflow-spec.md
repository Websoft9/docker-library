# Git Workflow Spec

| Property | Value |
|---|---|
| Status | Draft |
| Applies to | maintainers, AI workers, CI/CD maintainers |
| Purpose | Define branch roles, artifact promotion, and minimum gates |

## 1. Branch Roles

- `dev` is the integration branch for ongoing app/package work.
- `main` is the stable release branch.
- Direct feature work belongs on topic branches merged into `dev`.
- `main` should receive only validated promotions from `dev`.

## 2. Image Strategy

- `dev` builds candidate images and pushes dev tags:
  - immutable: `dev-<git-sha>`
  - rolling alias: `dev-latest`
- `main` does **not rebuild** custom app images.
- `main` promotes the already validated `dev-<git-sha>` image to stable tags.
- Stable tags come from `W9_VERSION` (see `docs/image-tag-spec.md`).

## 3. Minimum Gates

Promotion from `dev` to `main` requires:

- passing repository automation gates (`app-check`, CLI/tests, workflow syntax as applicable)
- deploy-validation for each changed custom-image app on the `dev` candidate image
- owner sign-off that the `dev` candidate artifact is the one being promoted

After promotion on `main`, run a light smoke check against the promoted stable tag:

- image/tag exists
- `docker compose up -d` succeeds
- health or web entry responds

## 4. Rationale

- Build heavy custom images once on `dev`.
- Keep `main` as a release/promote branch, not a second build branch.
- Reduce artifact cost while preserving release confidence.
