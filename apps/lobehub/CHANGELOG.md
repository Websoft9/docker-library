# CHANGELOG

## 2026-09-12

- Renamed the app from `lobechat` to `lobehub` to follow the upstream rebrand, including the directory, trademark, `W9_ID`, and container names.
- Updated the main image from `lobehub/lobe-chat:1.143.2` to `lobehub/lobehub:2.2.17`.
- Reworked the package from the single-container client-database model to the upstream server deployment model with bundled PostgreSQL (`paradedb`), Redis, and RustFS S3-compatible storage.
- Replaced the `ACCESS_CODE` login pair with LobeHub 2.x auth (`AUTH_SECRET`, `KEY_VAULTS_SECRET`) and URL replacement via `APP_URL`.
- Added `src/bucket.config.json` for the RustFS bucket policy and removed the obsolete single-container compose.
- Switched the RustFS init image to `quay.io/minio/mc` because the `minio/mc` Docker Hub repository no longer exists.
- Fixed the main healthcheck to not follow the sign-in redirect, and preloaded `pg_cron` in the bundled PostgreSQL.
- Added `tests/cases.yml` to check the reachable `/signin` page instead of the redirecting `/`.
- Documented in the README troubleshooting section that an online community loading failure is caused by missing domain and HTTPS configuration.
