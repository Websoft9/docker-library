# CHANGELOG

## 2026-11-03
- Declared the MySQL dependency and existing native connection inputs, inheriting standard database and account sources.
- Kept the MySQL image variant, runtime configuration, and image versions unchanged.

## 2026-09-20

- Update XWiki to 18.7 (latest stable) and the bundled MySQL to 8.4 LTS.
- Connect as the dedicated `xwiki` database user instead of `root`.
- Add `init: true` and a main-container healthcheck; default the web port to 9004.
- Refresh `variables.json`, README and Notes, and add a webapp smoke test.
