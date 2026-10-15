---
name: batch-app-update
description: Use when the user wants to update a batch of apps in one run, using either an explicit app list or one or more starting letters such as n,m to target all apps whose names start with those letters. Orchestrates per-app updates through the existing app-update workflow, supports controlled concurrency, and returns a batch summary. Trigger phrases: batch app update, bulk update apps, 批量更新应用, update apps starting with n,m.
---

# Batch App Update

Implement a batch of approved app updates by orchestrating repeated single-app `app-update` runs.

This skill is a thin wrapper over `app-update`. It does not replace the single-app workflow or redefine update rules.

## Inputs

- app selector (required)
- selector mode: `app-list`, `initials`, or `auto` (default `auto`)
- target version policy (optional: per-app auto-detect by default)
- concurrency (optional: default `2`)
- failure policy (optional: `continue` by default; alternative `stop-on-first-failure`)
- complexity skip policy (default `skip-complex-install`)

## Selector Rules

1. `app-list` means an explicit list of app names such as `n8n, nocodb, netdata`.
2. `initials` means one or more starting letters such as `n,m`; resolve them to all `apps/<name>` directories whose app name starts with any listed letter.
3. Initial matching is case-insensitive.
4. Deduplicate the resolved app list and sort it alphabetically before execution.
5. If a selector resolves to zero apps, stop and report the unmatched selector.
6. Mixed input is allowed when the caller is clear, for example explicit apps plus initials. Resolve everything into one final app list before execution.

## Steps

1. Resolve the selector into a concrete app list from `apps/*`.
2. Report the resolved app list before making edits when the selector came from initials or mixed input.
3. Run a quick packaging-feasibility screen for each app before deep update work.
4. If the app passes the screen, run the `app-update` workflow as one independent unit.
5. After the app finishes automated validation successfully, run `.venv/bin/libs appstore-sync --app <app>` using the remote-aware defaults from `.secrets/remote.env` or explicit remote arguments when provided.
6. If the app fails the screen under the default complexity skip policy, mark it as `skipped-complex-install`, record the reason, and continue.
7. Keep app-local scope. Do not merge unrelated fixes across apps.
8. Collect per-app results: target version, changed files, validation result, appstore sync result, risks, and owner E2E focus.
9. Produce one batch summary after all apps finish or after the configured stop condition is reached.

## Complexity Skip Rules

1. Perform only a short feasibility check before spending time on an app with unclear upstream packaging.
2. If the official upstream provides a clear Docker Compose example, container manifest, or equivalent deployment spec, proceed normally.
3. If the official upstream does not provide a clear Docker Compose specification and the package would need to be inferred mainly from an official `install.sh` script, do not spend much time reverse-engineering it.
4. If the expected runtime shape is more than `5` containers or services and there is no clear official Docker Compose specification, mark the app as `skipped-complex-install`.
5. For a skipped complex install app, record brief evidence only: estimated container count, the missing official compose fact, and the install script or doc source that forced inference.
6. Skipped complex install apps stay in the batch summary for later manual follow-up; they are not treated as update failures.

## Concurrency Rules

1. Batch execution may run concurrently, but only with controlled fan-out.
2. Default concurrency is `2` apps at a time.
3. Use concurrency `1` when the batch is small, when the apps are likely to touch shared files, or when remote validation capacity is limited.
4. Do not run more than `3` apps at once unless the caller explicitly requests more and the environment is known to tolerate it.
5. If multiple apps may edit the same shared file, do not edit them in parallel. Typical shared-file risks include `i18n/translation.json`, repository metadata, or any root-level generated artifact.
6. Upstream research and candidate detection may happen in parallel.
7. File edits and validation may run in parallel only when the active apps are not expected to touch the same shared files and the deploy target capacity is sufficient.
8. Remote deployment validation should usually stay at concurrency `1` unless the owner explicitly confirms enough remote capacity and isolation.
9. `appstore-sync` should usually stay at concurrency `1` on a shared remote target unless the owner explicitly confirms enough isolation.
10. When any app introduces a new translatable env key or another shared-file change, finish that app first, refresh the worktree facts, then continue with the remaining apps.

## Failure Handling

1. Under `continue`, record the failure and continue with the remaining apps.
2. Under `stop-on-first-failure`, stop scheduling new apps after the first blocking failure, but still report results for apps already in progress.
3. A `review-first` or ambiguous target for one app does not block the whole batch under `continue`; mark that app as `needs owner decision` and continue.
4. Validation environment failures must be reported separately from app defects.
5. If `appstore-sync` fails after tests pass, keep the app result distinct from update validation failure: record it as an appstore handoff block for manual E2E preparation.

## Output

Return a batch report in the same language as the user:

- resolved app list
- execution order and concurrency used
- per-app target version
- per-app result: `updated`, `needs owner decision`, `failed`, `skipped`
- per-app skip reason when applicable, including `skipped-complex-install`
- per-app validation result
- per-app appstore sync result
- per-app risks
- apps blocked by shared-file conflicts or environment limits
- apps blocked at appstore sync handoff
- owner E2E focus for the successful apps

## Rules

- Reuse `app-update` as the source of truth for single-app update behavior.
- Do not weaken any `app-update` requirement just because the work is batched.
- Prefer small independent batches over one very large unbounded run.
- Keep reports explicit per app; do not collapse multiple app outcomes into one generic summary.
- When the caller does not provide a concurrency value, choose the smallest value that preserves throughput without increasing shared-file conflict risk.
