# Quality Gates

Gate 0: Structure
- required files exist
- `src/` files match volume mounts

Gate 1: Policy
- env keys follow project rules
- URL and login variables are used correctly
- new `W9_*_SET` or `W9_LOGIN*` keys are registered in `i18n/translation.json`
- yaml and json are valid
- new or changed secret declarations/inputs pass `app-check --gate secrets`
- secret generation profile changes pass dictionary Schema, documented-example consistency, parameter-validation, and shared-metadata delivery tests; application-specific lengths/formats require upstream evidence, not inference from examples alone

Gate 2: Deploy
- `docker compose config` passes
- `docker compose up -d` succeeds
- required containers reach running or healthy state

Gate 3: AI Verification
- homepage or main port is reachable
- initialization path is checked when possible
- logs show no blocking error
- AI writes a report with evidence and risk
- secret runtime changes verify generated values against an authenticated app path and retain matching keys/data on recreation; template-only validation is not authentication or rotation proof
- verify the Websoft9 consumer supports object declarations and selected generators before delivery; syncing a dictionary does not install algorithm implementations

Gate 4: Owner E2E
- owner checks install result
- owner checks access result
- owner checks one core user path
- owner decides ship or reject

Ownership:
- Gates 0-3: AI and CI
- Gate 4: Owner only
