# Airflow on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Airflow**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Airflow admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Airflow Docker image](https://hub.docker.com/r/apache/airflow) and makes some improvements below.

<!-- W9_NOTE_START -->
Upgrading this package from an older Airflow / PostgreSQL pair (for example PostgreSQL 13 to 18) is a data migration: back up the `postgres-db` volume first, then follow the Airflow upgrade and Postgres major-version migration docs.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 3.3.1, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 8080 |


### Data Directory


Data is kept inside the container; a named volume is recommended for persistence.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Airflow Administrator Guide](https://support.websoft9.com/docs/airflow) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/apache/airflow)

- [Releases](https://github.com/apache/airflow)

- [Official docs](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html)

- [GitHub docs](https://github.com/apache/airflow)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
