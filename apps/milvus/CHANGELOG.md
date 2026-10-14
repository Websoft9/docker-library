# CHANGELOG

## 2026-10-14

- Updated Milvus from `v2.6.3` to `v3.0.3`, the latest stable upstream release.
- Followed the upstream `v3.0` standalone compose changes: added the `milvus-volume-init` one-shot volume ownership step, bumped etcd to `v3.5.25`, switched MinIO to the upstream `milvusdb/minio` image, and used the `mc ready local` MinIO healthcheck.
- Aligned `.env` with the current repository layout and documented the Milvus image environment section.
- Added inline purpose comments to the published ports and braced `${VAR}` references in `docker-compose.yml`.
- Added `tests/cases.yml` with `/healthz` and `/webui/` reachability checks.
- Added upstream releases, compose, and docs references to `variables.json`.
- Regenerated `README.md` from `variables.json`.
