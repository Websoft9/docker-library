# CHANGELOG

## 2026-10-15

- Restored the archived `langfuse` package to active maintenance and rebuilt it into a real Langfuse v4 self-hosted package based on the official docker-compose deployment.
- Replaced the leftover WordPress template content in `.env` and `docker-compose.yml` with the Langfuse service topology: `langfuse-web`, `langfuse-worker`, PostgreSQL 17, ClickHouse, Redis 7 and MinIO.
- Wired the shared secrets (`NEXTAUTH_SECRET`, `SALT`, `ENCRYPTION_KEY`), PostgreSQL, ClickHouse, Redis and S3/MinIO settings, and declared the shared password seed `W9_POWER_PASSWORD`.
- Published only the web console; all databases and object storage stay internal to the app network. Added a main-container healthcheck on `/api/public/health` and an app-specific validation check.
- Fixed single-node startup: set `CLICKHOUSE_CLUSTER_ENABLED=false` so ClickHouse migrations use non-replicated tables (the default cluster mode needs ClickHouse Keeper), and completed the `LANGFUSE_S3_EVENT_UPLOAD_*` / `LANGFUSE_S3_MEDIA_UPLOAD_*` bucket, region and prefix variables required by the worker.
