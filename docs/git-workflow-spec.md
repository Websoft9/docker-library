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
  - the promoted image is `dev-<pull_request.head.sha>` (the dev commit being merged)
- This works for merge commit, squash, or rebase: the head SHA comes from the PR payload, not from `main` history.
- `main` does **not** promote on `push`, and never rebuilds.
- Promotion reuses the exact dev image, so the released artifact is the validated candidate.

## 3. Image Strategy

- `dev` builds candidate images on `dev` push and pushes:
  - immutable: `dev-<git-sha>` (promotion target)
  - rolling alias: `dev-latest` (convenience only)
- `main` does **not rebuild**.
- `main` promotes the validated `dev-<pull_request.head.sha>` image to stable tags.
- Stable tags come from `W9_VERSION` (see `docs/image-tag-spec.md`).

### Manual Runs

The image workflow (`workflow_dispatch`) targets one app and derives the channel from the selected branch:

- run on `dev` → build `dev-<sha>` + `dev-latest` for the chosen app
- run on `main` → promote the chosen app to stable tags; `source_sha` (the validated `dev-<sha>`) is required
- runs on any other branch are rejected

Manual runs bypass the changed-paths filter, so a single app can be rebuilt or promoted without a new commit.

### Out-of-band Stable Images

A stable tag can also exist because someone pushed it directly (the `app-build --confirm-stable` backdoor).
The next promotion overwrites the stable tags it derives from `W9_VERSION`, always including `:latest`. Promotion:

- fails when the source `dev-<sha>` image is missing;
- warns (does not fail) when a target stable tag already points to a different digest, naming what will be overwritten.

An out-of-band stable image survives only if the same code is present on `dev` and gets merged; otherwise the next promotion replaces it.

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
