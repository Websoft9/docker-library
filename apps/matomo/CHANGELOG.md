# CHANGELOG

## 2026-11-04
- Wired native database connection inputs through `.env`, preserving the adapter, table prefix and independent bundled initialization defaults.
- Declared internal MySQL and external MySQL/MariaDB inputs; image versions are unchanged.
- Deployment and live connection validation were not performed.
- The pre-existing variable-target-port policy failure was later resolved in the shared validator while processing Dify/Mautic; Matomo's port mapping and runtime files required no further changes.

## Release
### Fixes and Enhancements

