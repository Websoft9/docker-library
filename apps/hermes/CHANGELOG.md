# CHANGELOG

## 2026-09-17

- Initial package for Hermes Agent v2026.9.14 (image `nousresearch/hermes-agent`).
- Gateway service with supervised web dashboard (port 9119) and OpenAI-compatible API server (port 8642).
- Persistent named volume `hermes_agent_data` mounted at `/opt/data`.
- Dashboard basic-auth and API bearer key seeded from `W9_POWER_PASSWORD`.
