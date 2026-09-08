# Git Workflow Spec

| Property | Value |
|---|---|
| Status | Adopted |
| Applies to | maintainers, AI workers, CI/CD maintainers |
| Purpose | Define branch roles, artifact promotion, and minimum gates |

## 1. Branch Roles

- `dev` is the integration branch for ongoing app/package work.
- `main` is the stable release branch and receives changes **only via PR merge from `dev`**.
- Direct commits to `main` are not allowed; promotion to stable happens on PR merge.

## 2. Promotion Trigger

- Promotion is driven by the PR that merges `dev` into `main`:
  - event: `pull_request` `closed` with `merged == true` and `base == main`
  - the promoted image is derived from `pull_request.head.sha` (the dev commit being merged)
- This works for merge commit, squash, or rebase: the head SHA comes from the PR payload, not from `main` history.

## 3. Image Strategy

- `dev` builds candidate images on `dev` push and pushes:
  - immutable: `dev-<git-sha>` (promotion target)
  - rolling alias: `dev-latest` (convenience only)
- `main` does **not rebuild**.
- `main` promotes the validated `dev-<pull_request.head.sha>` image to stable tags.
- Stable tags come from `W9_VERSION` (see `docs/image-tag-spec.md`).

## 4. Minimum Gates

Before a `dev` PR is merged into `main`:

- repository automation gates pass (`app-check`, CLI/tests, workflow syntax)
- deploy-validation for each changed custom-image app on its `dev-<head.sha>` candidate

After promotion to `main`, run a light smoke check on the promoted stable tag:

- image/tag exists
- `docker compose up -d` succeeds
- health or web entry responds

## 5. Rationale

- Build heavy custom images once on `dev`.
- Use the PR head SHA so promotion is precise regardless of merge strategy.
- Keep `main` as a promote branch, not a second build branch.
