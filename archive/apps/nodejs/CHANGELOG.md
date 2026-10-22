# CHANGELOG

## 2026-10-12

- Updated the default Node.js runtime image tag to `26` and added the `26-alpine` and `26-slim` variants to the published version list.
- Aligned `.env`, `docker-compose.yml`, and upstream metadata with current repository policy.
- Simplified the startup command so the container exits with the demo process instead of idling on a fallback tail.
