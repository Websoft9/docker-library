# Prompt Fragments

## Candidate Classification

Classify the candidate as `patch`, `minor`, `major`, or `security` using the upstream version and release notes. If the upstream page is a prerelease, beta, or rc, default to `skip` unless the user explicitly asks for prerelease testing.

## Risk Review

Assess whether the update may affect:

- container image tag behavior
- docker compose compatibility
- env keys or defaults
- mounted config files under `src/`
- initialization or login flow
- database or storage compatibility

## Decision Rule

Choose one result only:

- `auto-update`: safe to start implementation now
- `review-first`: owner should review before implementation
- `defer`: track and revisit in the next cadence
- `skip`: no update work should start for this candidate
