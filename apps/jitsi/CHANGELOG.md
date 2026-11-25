# CHANGELOG

## 2026-11-25

- Relaxed the web `access` group to `requireDomain: false`. The web container publishes an HTTPS port and upstream allows IP access with a self-signed certificate; mobile clients still require a trusted certificate, so a domain remains recommended for production.

## 2026-11-20

- Restored install-time configurability for the JVB media port. The UDP port is now declared as an `access` group (`jvb`, `protocol: "udp"`, `port: "${JVB_PORT}"`, `mappedPort: ["JVB_PORT"]`) instead of an `x-websoft9-unmanaged-ports` exemption, and `JVB_PORT` drives the host mapping, the container listener and the advertised SDP port so users can move it away from a contended `10000/udp`.

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
