# Consul on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Consul**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Consul admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Consul Docker image](https://hub.docker.com/r/hashicorp/consul) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 2.0.4, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web UI and HTTP API | 8500 |


### Data Directory


Data is persisted in the `consul-data` volume, mounted at `/consul/data`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration is overridden by mounting `./src/consul-config` to `/consul/config`.


## References

- [Consul Administrator Guide](https://support.websoft9.com/docs/consul) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/hashicorp/consul)

- [Releases](https://github.com/hashicorp/consul/releases)

- [Official docs](https://developer.hashicorp.com/consul/docs/release-notes)

- [Official docs](https://developer.hashicorp.com/consul/docs/install/docker)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
