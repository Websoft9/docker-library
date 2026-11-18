# AFFiNE

- Official 0.27.4 self-host: `docker compose up`, then open `http://<host>:3010` and create the first admin account.
- Since 0.27, runtime configuration is read from `config/config.json`. The init service renders `server.externalUrl` from `AFFINE_SERVER_EXTERNAL_URL`; recreate the containers after changing that URL.
- `affine-migration` runs database migration once on startup; it must complete before the app starts.
- Postgres uses password authentication (`${W9_POWER_PASSWORD}`). Maintain the database with:
  ```
  docker exec ${W9_ID}-postgresql psql -U affine -d affine
  ```
- Upgrade from a legacy `.env`-based 0.26 deployment requires carrying forward the old Postgres data and connection settings per https://docs.affine.pro/self-host-affine/install/upgrade. The Postgres image applies authentication settings only when initializing a new, empty data directory; changing auth does not rewrite an existing data directory.
