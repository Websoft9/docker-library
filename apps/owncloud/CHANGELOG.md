# CHANGELOG

## 2026-10-09
- replace the legacy ownCloud Server package with ownCloud Infinite Scale 8.2.1
- simplify the deployment from `server + mysql + redis` to the official single-container `owncloud/ocis` topology
- add a one-shot `ocis-init` service that runs the official `ocis init` once to generate `ocis.yaml`
- keep the main container on the official default `ocis server` command (no entrypoint override)
- add HTTPS smoke testing and record first-start-only admin password behavior
