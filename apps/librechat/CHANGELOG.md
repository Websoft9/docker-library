# CHANGELOG

## 2026-09-13

- Pinned the main image from the floating `latest` to `librechat/librechat:v0.8.7`.
- Switched the main image from `ghcr.io/danny-avila/librechat-dev` to the official `librechat/librechat` repository.
- Aligned the package with the current upstream deployment: added the `admin-panel` service, moved the vector database to `pgvector/pgvector`, and bumped MongoDB to `mongo:7.0` and Meilisearch to `v1.35`.
- Pinned the RAG API image to `ghcr.io/danny-avila/librechat-rag-api-dev-lite:v0.6.0` and restored `OPENAI_API_KEY=user_provided` so the RAG API starts.
- Wired `DOMAIN_CLIENT` and `DOMAIN_SERVER` to `${W9_URL}` and set `W9_URL_REPLACE=true`, fixing the URL replacement policy gate.
- Fixed the RAG API URL from `http://${W9_ID}-8000` to `http://${W9_ID}-rag:8000`.
- Added a main-container healthcheck against `/health`, converted all variable references to the braced form, and added the port purpose comments.
- Updated `src/librechat.yaml` to configuration version `1.3.16`.
