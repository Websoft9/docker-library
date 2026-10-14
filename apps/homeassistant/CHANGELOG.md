# CHANGELOG

## 2026-10-13

- Updated Home Assistant from `2025.7` to `2026.10`.
- The container now requires Docker 23 or newer and supports only 64-bit hosts.
- No environment variable or port changes are required.
- Regenerated `README.md` from the updated version metadata.
- Added `src/nginx-proxy.conf` so the Websoft9 Gateway clears the forwarded
  headers that make Home Assistant return HTTP 400 on a bound domain, and keeps
  the frontend WebSocket connection alive; direct port access was already fine.

## Release
### Fixes and Enhancements

