# CHANGELOG

## 2026-10-13

- Updated the default ActiveMQ image tag from `6.3.0` to `6.3.2`.
- Refreshed the documented supported image tags to `6.3.2`, `6.2.10`, `5.19.11`, and `latest`.

## 2026-08-25

- Removed Artemis, Classic only; official `apache/activemq` image, versions 6.3.0 / 6.2.8 / 5.19.9 / latest.
- Added `src/entrypoint.sh` compatible with 5.19 / 6.2 / 6.3; fixed Web Console 403, 5.19 auth and CSP quirks, and restart loop.
