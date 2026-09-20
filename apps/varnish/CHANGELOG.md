# CHANGELOG

## 2026-09-20
- Updated Varnish to `9.0` (official `varnish` image, currently 9.0.4).
- Replaced the stale `src/default.vcl` (VCL 4.0 with an unresolvable backend that prevented the container from starting) with the upstream 9.0 default VCL; the backend is now configured through `VARNISH_BACKEND_HOST`.
- Exposed the Varnish image variables in `.env` (`VARNISH_SIZE` plus optional `VARNISH_BACKEND_HOST`, `VARNISH_FILESERVER`, `VARNISH_VCL_FILE`, `VARNISH_HTTP_PORT`, `VARNISH_PROXY_PORT`).
- Normalized `.env` and `docker-compose.yml` to current repository policy rules (braced `${VAR}` references, port purpose comment, removal of the source comment).
- Added `tests/cases.yml` with a Varnish smoke check.
- Updated `Notes.md` and regenerated the README.
