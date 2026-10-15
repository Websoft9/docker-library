# Ckan on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Ckan**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Ckan admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Ckan Docker image](https://hub.docker.com/r/ckan/ckan-base) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 2.12.0.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 5000 |


### Data Directory


- `ckan_storage` → `/var/lib/ckan`
- `pip_cache` → `/root/.cache/pip`
- `site_packages` → `/usr/lib/python3.10/site-packages`
- `vscode_server` → `/root/.vscode-server`
- `pg_data` → `/var/lib/postgresql/data`
- `solr_data` → `/var/solr`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration is overridden by mounting `./src/postgresql/docker-entrypoint-initdb.d` to `/docker-entrypoint-initdb.d`.


## References

- [Ckan Administrator Guide](https://support.websoft9.com/docs/ckan) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/ckan/ckan-base)

- [Releases](https://github.com/ckan/ckan/releases)

- [Official compose](https://raw.githubusercontent.com/ckan/ckan-docker/master/docker-compose.yml)

- [Official env example](https://raw.githubusercontent.com/ckan/ckan-docker/master/.env.example)

- [GitHub docs](https://github.com/ckan/ckan-docker)

- [Official docs](https://docs.ckan.org/en/2.12/changelog.html#v-2-12-0-2026-08-26)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
