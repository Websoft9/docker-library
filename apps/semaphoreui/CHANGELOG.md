# CHANGELOG

## 2026-10-14

- Renamed the app package from `semaphore` to `semaphoreui`; the product name is now "Semaphore UI".
- Updated Semaphore UI from v2.16.31 to v2.19.16.
- Refreshed `.env` and `docker-compose.yml` to the current packaging policy (braced variable references, published-port purpose comment, `.env` layout contract).
- Replaced the removed `SEMAPHORE_PLAYBOOK_PATH` with `SEMAPHORE_TMP_PATH`; added the required `SEMAPHORE_ACCESS_KEY_ENCRYPTION` secret.
- Added an app-specific admin login check under `tests/`.
