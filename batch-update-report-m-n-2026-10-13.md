## Batch Update Report

- selector mode: initials
- selector input: `m,n`
- resolved apps: `mariadb, matomo, mattermost, mautic, meilisearch, metabase, milvus, mlflow, mongodb, moodle, mysql, n8n, neo4j, nextcloud, nextjs, nginx, nginxproxymanager, nifi, nodejs, nodered, nopcommerce`
- failure policy: continue
- concurrency used: assessment parallelized; remote deploy validation and appstore sync effectively serialized after environment conflicts
- overall decision: partially-blocked

## Per-App Results

- app: `mattermost`
  result: updated
  skip reason:
  current version: `11.11`
  target version: `11.11.1`
  files changed: `apps/mattermost/.env`, `apps/mattermost/variables.json`, `apps/mattermost/CHANGELOG.md`, `apps/mattermost/README.md`
  validation: passed `app-check`, remote deploy, web reachability, and `/api/v4/system/ping`
  appstore sync: passed
  risks: package still uses shared remote ports `9001/8443`; owner E2E should confirm first-run admin flow and Calls port behavior
  owner E2E focus: confirm login, team creation/core chat path, and site URL behavior behind platform proxy

- app: `n8n`
  result: updated
  skip reason:
  current version: `2.43.4`
  target version: `2.43.4`
  files changed: existing worktree changes in `apps/n8n/*` plus `apps/n8n/tests/`
  validation: passed `app-check`, remote deploy, and web reachability
  appstore sync: passed
  risks: validation only proved reachability, not authenticated first-run workflow
  owner E2E focus: verify first access, workflow editor load, and webhook/base URL behavior

- app: `neo4j`
  result: updated
  skip reason:
  current version: `2026.07`
  target version: `2026.09`
  files changed: existing worktree changes in `apps/neo4j/.env`, `CHANGELOG.md`, `README.md`, `variables.json`, `tests/cases.yml`
  validation: passed after rerunning sequentially; remote deploy and web reachability OK
  appstore sync: passed
  risks: release-line jump is calendar-tag based; browser UI passed but Bolt usage was not validated
  owner E2E focus: verify browser console, default credentials flow, and Bolt connectivity

- app: `nextcloud`
  result: updated
  skip reason:
  current version: `34.0`
  target version: `35.0`
  files changed: existing worktree changes in `apps/nextcloud/.env`, `CHANGELOG.md`, `README.md`, `variables.json`, `tests/cases.yml`
  validation: passed `app-check`, remote deploy, and `/login` reachability
  appstore sync: passed
  risks: only automated login-page reachability checked; upgrade path with real persisted data not exercised
  owner E2E focus: verify install/login flow, storage setup, and bundled MySQL behavior

- app: `nginx`
  result: updated
  skip reason:
  current version: `1.29`
  target version: `1.31`
  files changed: existing worktree changes in `apps/nginx/.env`, `CHANGELOG.md`, `README.md`, `docker-compose.yml`, `src/cmd.sh`, `variables.json`, `tests/cases.yml`
  validation: passed `app-check`, remote deploy, and web reachability
  appstore sync: passed
  risks: package still validates only the demo/default page path
  owner E2E focus: confirm container starts cleanly from appstore and default content renders as expected

- app: `nginxproxymanager`
  result: updated
  skip reason:
  current version: `2.10.4`
  target version: `2.16.0`
  files changed: existing worktree changes in `apps/nginxproxymanager/.env`, `CHANGELOG.md`, `README.md`, `docker-compose.yml`, `variables.json`, `tests/cases.yml`
  validation: passed after rerunning sequentially; remote deploy and web reachability OK
  appstore sync: passed
  risks: automated check did not exercise first-login credential rotation flow
  owner E2E focus: verify default login, forced credential change, proxy host creation, and HTTPS listener

- app: `nifi`
  result: failed
  skip reason:
  current version: `latest` / broken legacy package shape before current worktree changes
  target version: `2.12.0`
  files changed: existing worktree changes in `apps/nifi/.env`, `CHANGELOG.md`, `Notes.md`, `README.md`, `docker-compose.yml`, `variables.json`, deletions under `src/`, `tests/check-https-login.sh`
  validation: deploy passed, but custom HTTPS validation still failed; first failure was bad script input, then after fix the script reached `curl: (35) Send failure: Broken pipe`
  appstore sync: not run
  risks: HTTPS readiness/self-signed bootstrap path is still not reliably covered by current test case
  owner E2E focus: after follow-up fix, confirm HTTPS UI load, self-signed warning handling, and single-user login

- app: `nodejs`
  result: updated
  skip reason:
  current version: `24`
  target version: `26`
  files changed: existing worktree changes in `apps/nodejs/.env`, `CHANGELOG.md`, `README.md`, `docker-compose.yml`, `src/cmd.sh`, `variables.json`, `tests/cases.yml`
  validation: passed `app-check`, remote deploy, and web reachability
  appstore sync: passed
  risks: package validates only the demo scaffold/runtime template
  owner E2E focus: confirm runtime starts from appstore and sample app responds as expected

- app: `nodered`
  result: updated
  skip reason:
  current version: `4.1`
  target version: `5.0`
  files changed: existing worktree changes in `apps/nodered/.env`, `CHANGELOG.md`, `README.md`, `docker-compose.yml`, `variables.json`, `tests/cases.yml`
  validation: passed after rerunning sequentially; remote deploy and web reachability OK
  appstore sync: passed
  risks: no auth configured; validation only checked open console reachability
  owner E2E focus: verify editor loads, flow persistence, and intended unauthenticated/default access behavior

- app: `nextjs`
  result: failed
  skip reason:
  current version: `16.3.5`
  target version: `16.4.0`
  files changed: existing worktree changes in `apps/nextjs/.env`, `CHANGELOG.md`, `README.md`, `variables.json`
  validation: deploy passed, but `container-healthy` never reached healthy; healthcheck stayed `starting`
  appstore sync: not run
  risks: first-run scaffold/install/build inside container is slow and likely needs healthcheck/readiness tuning
  owner E2E focus: after follow-up fix, confirm scaffold completes, app becomes healthy, and page loads on first boot

- app: `mariadb`
  result: needs owner decision
  skip reason:
  current version: `12.0` default with many additional tracks
  target version: `13.0`
  files changed:
  validation:
  appstore sync:
  risks: major DB track change plus stale version matrix; not a clean blind batch bump
  owner E2E focus: decide whether to do a dedicated version-matrix cleanup/update

- app: `matomo`
  result: needs owner decision
  skip reason:
  current version: `5.6.1`
  target version: `5.14`
  files changed:
  validation:
  appstore sync:
  risks: package is far behind and likely entangled with old bundled MySQL defaults
  owner E2E focus: decide whether to take a dedicated upgrade task instead of batch pass

- app: `mautic`
  result: needs owner decision
  skip reason: invalid current packaged version metadata (`6-apache`) blocks deterministic assessment
  current version: invalid package metadata
  target version: unclear stable target without metadata normalization
  files changed:
  validation:
  appstore sync:
  risks: metadata-blocked before safe implementation
  owner E2E focus: normalize current versioning model first

- app: `meilisearch`
  result: needs owner decision
  skip reason:
  current version: `1.16`
  target version: `v1.55`
  files changed:
  validation:
  appstore sync:
  risks: very large intra-major gap with likely breaking behavior changes
  owner E2E focus: assess compatibility and package shape before implementation

- app: `metabase`
  result: needs owner decision
  skip reason: wildcard packaged version (`v0.64.x`) blocks deterministic current-to-target comparison
  current version: wildcard metadata
  target version: likely latest `v0.64.1.x` patch line
  files changed:
  validation:
  appstore sync:
  risks: metadata normalization needed first
  owner E2E focus: decide whether to fix version declaration first, then update

- app: `milvus`
  result: needs owner decision
  skip reason:
  current version: `2.6.3`
  target version: `v2.6.25`
  files changed:
  validation:
  appstore sync:
  risks: bundle compatibility with pinned companion images should be reviewed
  owner E2E focus: assess full stack compatibility, not only main image bump

- app: `mlflow`
  result: needs owner decision
  skip reason:
  current version: `3.1.4`
  target version: provisional `v3.17.0`
  files changed:
  validation:
  appstore sync:
  risks: upstream source metadata appears ambiguous; target detection confidence is low
  owner E2E focus: verify target version source before implementation

- app: `mongodb`
  result: skipped
  skip reason: runtime/environment history indicates newer MongoDB lines were previously blocked on current Linux kernel behavior
  current version: `7.0` default, additional `8.0`, `8.3`
  target version: no safe batch target chosen
  files changed:
  validation:
  appstore sync:
  risks: environment/runtime block, not just packaging
  owner E2E focus: re-evaluate only when runtime constraint is intentionally revisited

- app: `moodle`
  result: needs owner decision
  skip reason:
  current version: `5.2.2`
  target version: `5.3`
  files changed:
  validation:
  appstore sync:
  risks: image/provider and DB compatibility should be reviewed together
  owner E2E focus: confirm upstream image and DB support before update

- app: `mysql`
  result: needs owner decision
  skip reason:
  current version: `9.5` default with many legacy tracks
  target version: `9.7`
  files changed:
  validation:
  appstore sync:
  risks: update is mixed with stale matrix cleanup and DB policy decisions
  owner E2E focus: decide whether to do dedicated matrix rationalization

- app: `nopcommerce`
  result: skipped
  skip reason: only newer prerelease candidate detected; no newer stable release than packaged version
  current version: `4.90.8`
  target version:
  files changed:
  validation:
  appstore sync:
  risks: prerelease-only candidate
  owner E2E focus: none until a stable upstream release appears

## Blockers And Exceptions

- shared-file conflicts: none added by this run; all implemented changes stayed app-local
- environment limits: remote validation must stay serial because all test deployments publish `9001`; early parallel attempts caused false port-allocation failures
- appstore sync handoff blocks: `nextjs` and `nifi` were not synced because automated validation did not pass
- stopped early because of failure policy: no

## Summary

- updated apps: `mattermost`, `n8n`, `neo4j`, `nextcloud`, `nginx`, `nginxproxymanager`, `nodejs`, `nodered`
- needs owner decision: `mariadb`, `matomo`, `mautic`, `meilisearch`, `metabase`, `milvus`, `mlflow`, `moodle`, `mysql`
- failed apps: `nifi`, `nextjs`
- skipped apps: `mongodb`, `nopcommerce`
