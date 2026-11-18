# CHANGELOG

## 2026-11-18

- Explicitly exempted JVB media UDP `10000` from access management while preserving its default published binding.

## 2026-11-17

- Migrated `access` to the V2 port-group array (`web:8443` HTTPS with `requireDomain: true` and `rootUrl: ["PUBLIC_URL"]`).
- Fixed the legacy HTTPS target to match the container listener on `8443` (#2310); the V2 declaration now carries the same target without the deprecated port and URL aliases. The default HTTPS mapping remains `9443:8443`.
- Documented that `PUBLIC_URL` must be `https://<your-domain>` when reached through a bound domain.

## 2026-09-15

- Update Jitsi Meet to `stable-11248` for `web`, `prosody`, `jicofo`, and `jvb`.
- Switch the image source from Docker Hub (`jitsi/*`) to GHCR (`ghcr.io/jitsi/*`), where upstream publishes the current stable tags.
- Expose the new upstream environment options (ICE restart, audio translation, tracing, AV1/scalability settings) in `docker-compose.yml`.
- Add `upstream` metadata (releases, compose, env example, docs) and `access`.
- Remove source comments from `docker-compose.yml`, normalize references to `${VAR}`, and add port purpose comments.
- Add `tests/cases.yml` with an HTTPS smoke check and repository catalog data.
