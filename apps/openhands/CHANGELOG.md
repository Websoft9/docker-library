# CHANGELOG

## 2026-10-09
- migrate the package from legacy OpenHands 0.28 to Agent Canvas 1.26.0
- switch to the official `ghcr.io/openhands/agent-canvas` image and current Docker persistence layout
- add metadata for the generated API key and a `/canvas` smoke test
- set `LOCAL_BACKEND_API_KEY` and `OH_SECRET_KEY` from `W9_POWER_PASSWORD` so the UI API-key login and stored-secret encryption are fixed and known
- expose the login token as `LOCAL_BACKEND_API_KEY` and fix the credential source (was pointing at a non-existent state file path)
- provide plain-text `.env` defaults for `LOCAL_BACKEND_API_KEY` and `OH_SECRET_KEY` and declare them in `variables.json` `env.secrets` so the platform can regenerate same-shaped values
