# CHANGELOG

## 2026-11-04

- Declared internal CouchDB, authenticated Redis, and the separate LiteLLM PostgreSQL dependency; excluded MinIO and helper services.
- Kept all three stores internal-only and removed external providers and connection mappings.
- Restored the original app/worker/proxy and LiteLLM connection expressions and datastore initialization sources; removed inputs added solely for external databases.
- Preserved default credentials, images, volumes, commands, and dependencies; passed static configuration and regression checks without deployment or live database verification.

## 2026-10-13

- Updated Budibase from `3.13.28` to the current official self-hosted `latest` image line.
- Aligned the compose stack with the current official self-hosted topology, including LiteLLM and its PostgreSQL dependency.
- Brought `.env`, `docker-compose.yml`, and metadata into current repository policy shape and added app-specific validation cases.
