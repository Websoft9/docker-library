# LobeHub on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **LobeHub**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the LobeHub admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [LobeHub Docker image](https://hub.docker.com/r/lobehub/lobehub) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 2.2.17, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 3210 |


### Data Directory


- `postgresql_data` → `/var/lib/postgresql/data`
- `redis_data` → `/data`
- `rustfs_data` → `/data`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration is overridden by mounting `./src/bucket.config.json` to `/bucket.config.json`.


## References

- [LobeHub Administrator Guide](https://support.websoft9.com/docs/lobehub) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/lobehub/lobehub)

- [Releases](https://github.com/lobehub/lobehub/releases)

- [Official compose](https://raw.githubusercontent.com/lobehub/lobehub/canary/docker-compose/deploy/docker-compose.yml)

- [Official env example](https://raw.githubusercontent.com/lobehub/lobehub/canary/docker-compose/deploy/.env.example)

- [Official docs](https://lobehub.com/docs/self-hosting/platform/docker-compose)

- [GitHub docs](https://github.com/lobehub/lobehub)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.

**Online community fails to load?**
- The online community requires access through a configured domain with HTTPS. Set the app domain and enable HTTPS, then reload.
<!-- W9_TROUBLESHOOT_END -->
