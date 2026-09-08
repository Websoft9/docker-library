## 2026-09-08

- Updated Neo4j from `5.26.5` to the floating `2026.07` line and reduced the published version set to `2026.07`, `2026.07-enterprise`, `5.26`, and `5.26-enterprise`.
- Kept `2026.07.0` out of the package because upstream release notes mark it as unsafe; the `2026.07` line was validated against the current safe image state.
- Aligned `.env` and `docker-compose.yml` with current repository policy: braced variable references, compose port purpose comments, and the canonical image environment section.
- Switched the persistent volume mount to `/data` to match the current official Neo4j Docker documentation.
