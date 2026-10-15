# CHANGELOG

## 2026-10-13

- Updated Couchbase Community packaging target to the current stable image tag `community-8.0.3` after verifying the floating `8.0` image tag is not published.
- Normalized `.env` and `docker-compose.yml` to current repository policy by using the official image repository, braced variable references, and inline published-port comments.
- Added app-specific validation coverage for the Couchbase setup screen.
## 2026-10-13

- switched the package from the non-existent `community-8.0.3` / `8.0` tags to the verified official `couchbase/server:8.0.3` image tag
- refreshed the setup-screen smoke check to match the current Couchbase 8.0 web shell content exposed before cluster initialization
