# Umami on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Umami**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the Umami console and sign in with `admin` / `umami`.
2. Add a website, then copy the tracking script into your site.
3. Open the website report to confirm data is being collected.

### Change Password

1. Sign in to Umami and open **Settings → Profile**.
2. Change the password there; the default `admin` / `umami` account is not controlled by `.env`.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Umami Docker image](https://ghcr.io/umami-software/umami) and makes some improvements below.

<!-- W9_NOTE_START -->
- The admin account is seeded on first start as `admin` / `umami`; change it after the first login.
- `DATABASE_URL` points at the bundled PostgreSQL service `${W9_ID}-postgresql`.
- `TWO_FACTOR_ENCRYPTION_KEY` (64 hex characters) must be set to use two-factor authentication.
- Database migrations run automatically on container start.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 3.4, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 3000 |


### Data Directory


Data is persisted in the `postgresql` volume, mounted at `/var/lib/postgresql/data`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration is overridden by mounting `./src/postgresql_init.sh` to `/docker-entrypoint-initdb.d/postgresql_init.sh`.


## References

- [Umami Administrator Guide](https://support.websoft9.com/docs/umami) by Websoft9

- [GHCR image](https://ghcr.io/umami-software/umami)

- [Releases](https://github.com/umami-software/umami/releases)

- [Official compose](https://raw.githubusercontent.com/umami-software/umami/v3.4.0/docker-compose.yml)

- [Official docs](https://umami.is/docs/install)

- [Official docs](https://umami.is/docs/environment-variables)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**Container stays unhealthy?**
- The first start runs database migrations; wait a minute and check `docker compose logs ${W9_ID}`.

**Login fails with the default credentials?**
- The `admin` / `umami` account exists only on a fresh database. If it was changed, reset it from the database or recreate the stack.

**Database connection error?**
- Confirm `${W9_ID}-postgresql` is healthy and that `DATABASE_URL` matches the bundled database.
<!-- W9_TROUBLESHOOT_END -->
