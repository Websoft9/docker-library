# Langfuse

## Notes

- Langfuse v4 requires six services: `langfuse-web`, `langfuse-worker`, PostgreSQL 17, ClickHouse, Redis 7 and MinIO. The official docs recommend at least 4 vCPU and 16 GiB RAM.
- `ENCRYPTION_KEY` must be a 64-character hex string (`openssl rand -hex 32`); it encrypts stored secrets and must stay stable across restarts.
- `NEXTAUTH_URL` must exactly match the public URL used in the browser, otherwise authentication callbacks and UI links break.
- The bundled MinIO is internal to the app network. Browser-side media uploads that use presigned URLs may require exposing MinIO separately.
- Back up the `postgres_data`, `clickhouse_data`, `minio_data` and `redis_data` volumes before upgrades.
