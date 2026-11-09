# Symfony on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Symfony**.
2. Open the app's Access URL and confirm the starter page loads.

<!-- W9_GUIDE_START -->
### Usage

1. Open the Symfony URL from the Websoft9 console.
2. Replace the starter project with your application code when ready.
<!-- W9_GUIDE_END -->

## Configuration Reference

This package runs the Symfony framework from its [official source repository](https://github.com/symfony/symfony) on the [Server Side Up PHP 8.5 FrankenPHP image](https://hub.docker.com/r/serversideup/php).

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



## References

- [Symfony framework repository](https://github.com/symfony/symfony)
- [Server Side Up PHP image](https://hub.docker.com/r/serversideup/php)
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
