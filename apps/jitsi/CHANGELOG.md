# CHANGELOG

## 2026-09-15

- Update Jitsi Meet to `stable-11248` for `web`, `prosody`, `jicofo`, and `jvb`.
- Switch the image source from Docker Hub (`jitsi/*`) to GHCR (`ghcr.io/jitsi/*`), where upstream publishes the current stable tags.
- Expose the new upstream environment options (ICE restart, audio translation, tracing, AV1/scalability settings) in `docker-compose.yml`.
- Add `upstream` metadata (releases, compose, env example, docs) and `access`.
- Remove source comments from `docker-compose.yml`, normalize references to `${VAR}`, and add port purpose comments.
- Add `tests/cases.yml` with an HTTPS smoke check and repository catalog data.
