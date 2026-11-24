# Symfony on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Symfony**.
2. In the **Access** tab, get the login URL and credentials.

3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the Symfony URL from the Websoft9 console.
2. Replace the starter project with your application code when ready.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Symfony Docker image](https://github.com/symfony/symfony) and makes some improvements below.

<!-- W9_NOTE_START -->
### Database

No database is bundled and Symfony's skeleton has no database dependency by default. Install Doctrine ORM/DBAL in your application and set `DATABASE_URL` in `.env` to connect to an external database.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 8.1.11, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 8080 |


### Data Directory


Data is persisted in the `symfony_app` volume, mounted at `/var/www/html`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


- `./src/entrypoint.sh` → `/opt/websoft9/entrypoint.sh`
- `./src/entrypoint.d` → `/opt/websoft9/entrypoint.d`
- `./src/favicon.ico` → `/opt/websoft9/favicon.ico`



## References

- [Symfony Administrator Guide](https://support.websoft9.com/docs/symfony) by Websoft9

- [Docker Hub image](https://github.com/symfony/symfony)

- [Releases](https://github.com/symfony/symfony/releases)

- [GitHub docs](https://github.com/symfony/symfony)

- [Official docs](https://symfony.com/doc/current/setup.html)

- [Official docs](https://symfony.com/doc/current/setup/docker.html)

- [Official docs](https://serversideup.net/open-source/docker-php/docs/image-variations/frankenphp)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
