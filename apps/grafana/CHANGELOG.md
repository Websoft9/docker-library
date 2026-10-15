# CHANGELOG

## 2026-10-13

- Upgraded Grafana to `13.2`.
- Migrated the deprecated `GF_INSTALL_PLUGINS` to `GF_PLUGINS_PREINSTALL`; Grafana 13.x silently ignores `GF_INSTALL_PLUGINS` unless `GF_INSTALL_PLUGINS_FORCE=true`.
- Standardized the main image reference to `${W9_REPO}:${W9_VERSION}` and removed the leading docs/dockerfile/dockerhub source comments.
- Note: upstream removed the `grafana-server` and `grafana-cli` binaries, and the unified-storage migration caveat applies when upgrading an existing instance.

## Release 
### Fixes and Enhancements
