# Copilot Instructions

Read `AGENTS.md` first.

Authority order:
1. `AGENTS.md`
2. `docs/vision.md`
3. `docs/architecture.md`
4. `docs/ai-sdlc/README.md`
5. `docs/upstream-spec.md`
6. `docs/code_owner.md`

Repository model:
- `apps/<app>` is one deployable unit
- keep changes app-local unless the task is explicitly cross-cutting
- prefer official images or trusted upstream images

Required checks when changing an app:
- `docker-compose.yml` stays runnable
- `src/` files exist for every mounted local config file
- env variables follow repository rules
- translatable env keys are `W9_*_SET` and `W9_LOGIN*`; new ones must be registered in `i18n/translation.json`
- translation values stay human-authored; empty `["", ""]` entries are waiting for humans
- produce a short test report using `docs/ai-sdlc/06-test-report-format.md`

Maintenance model:
- issue is the work unit
- owner decides demand and final E2E only
- AI does research, implementation, automated validation, and reporting
- maintenance cadence and update policy live in `metadata/maintenance.yaml`
- archived app metadata lives in `metadata/archive.yaml`

For app updates:
- read upstream release notes first
- classify the candidate using `docs/ai-sdlc/02-maintenance-policy.md`
- follow `docs/ai-sdlc/03-update-pipeline.md`

For new apps:
- start from the template
- follow `docs/ai-sdlc/04-new-app-pipeline.md`
