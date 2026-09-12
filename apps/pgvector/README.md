# pgvector on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **pgvector**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Connect with any PostgreSQL client to the host on port `5432` using user `postgres` and the password from `.env`.
2. The default database already has the `vector` extension enabled. For any other database run `CREATE EXTENSION vector;`.
3. Create a vector column, for example `CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3));`.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update `W9_POWER_PASSWORD` in `.env` and save.
3. Rebuild the app. `POSTGRES_PASSWORD` only applies on first startup, so for an existing database also run `ALTER USER postgres WITH PASSWORD '<new>';`.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [pgvector Docker image](https://hub.docker.com/r/pgvector/pgvector) and makes some improvements below.

<!-- W9_NOTE_START -->
The package mounts `src/init-vector.sql` into `/docker-entrypoint-initdb.d/`, so a fresh deployment enables the `vector` extension in the default database automatically. The image tag is pinned to `pg18-trixie` (PostgreSQL 18 on Debian trixie).
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: pg18-trixie.


### Ports

| Purpose | Port |
| --- | --- |
| PostgreSQL | 5432 |


### Data Directory


Data is persisted in the `pgvector` volume, mounted at `/var/lib/postgresql`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `POSTGRES_DB`, `POSTGRES_PASSWORD`, `POSTGRES_USER` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


Configuration is overridden by mounting `./src/init-vector.sql` to `/docker-entrypoint-initdb.d/init-vector.sql`.


## References

- [pgvector Administrator Guide](https://support.websoft9.com/docs/pgvector) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/pgvector/pgvector)

- [GitHub docs](https://github.com/pgvector/pgvector)

- [GitHub docs](https://github.com/pgvector/pgvector#docker)

- [GitHub docs](https://github.com/pgvector/pgvector#getting-started)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.

**`type "vector" does not exist`?**
- Run `CREATE EXTENSION vector;` in the database you are using. The init script only enables it in the default database on first startup.
<!-- W9_TROUBLESHOOT_END -->
