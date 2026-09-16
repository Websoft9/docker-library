# Django on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Django**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Django admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Django Docker image](https://github.com/django/django) and makes some improvements below.

<!-- W9_NOTE_START -->
### Change Database

Edit the connection in `.env`, then rebuild the app:

- `DB_HOST`: database host
- `DB_PORT`: database port (default `5432`)
- `DB_NAME`: database name
- `DB_USER`: database user
- `DB_PASSWORD`: database password

The app reads these on startup, so a rebuild applies the new connection.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 6.1.1, 5.2.17, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 8000 |


### Data Directory


- `django_app` → `/app`
- `postgres_data` → `/var/lib/postgresql/data`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration is overridden by mounting `./src/entrypoint.sh` to `/entrypoint.sh`.


## References

- [Django Administrator Guide](https://support.websoft9.com/docs/django) by Websoft9

- [Docker Hub image](https://github.com/django/django)

- [Releases](https://github.com/django/django/releases)

- [Official docs](https://docs.djangoproject.com/)

- [Official docs](https://docs.djangoproject.com/en/5.2/howto/deployment/)

- [Official docs](https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/gunicorn/)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
