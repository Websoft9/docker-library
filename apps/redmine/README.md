# Redmine on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Redmine**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Redmine admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Redmine Docker image](https://hub.docker.com/_/redmine) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 7.0, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Redmine web console | 3000 |


### Data Directory


- `redmine_files` → `/usr/src/redmine/files`
- `mysql` → `/var/lib/mysql`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration is overridden by mounting `./src/configuration.yml` to `/usr/src/redmine/config/configuration.yml`.


## References

- [Redmine Administrator Guide](https://support.websoft9.com/docs/redmine) by Websoft9

- [Docker Hub image](https://hub.docker.com/_/redmine)

- [Releases](https://www.redmine.org/projects/redmine/wiki/Download)

- [GitHub docs](https://github.com/docker-library/docs/blob/master/redmine/README.md)

- [Official docs](https://www.redmine.org/projects/redmine/wiki/RedmineInstall)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
