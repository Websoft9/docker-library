# Varnish on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Varnish**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

Varnish is an HTTP cache and reverse proxy; it has no built-in login. Until a backend is configured it serves a local placeholder page.

1. Set `VARNISH_BACKEND_HOST` in `.env` to your origin, for example `http://wordpress_shlez:80/`.
2. Rebuild the app. Requests to the Varnish URL are now cached and served from your origin.

To customize caching rules, edit `./src/default.vcl` and rebuild.

### Configuration

- Cache size: `VARNISH_SIZE` in `.env`.
- Backend origin: `VARNISH_BACKEND_HOST` in `.env`.
- Static file mode: `VARNISH_FILESERVER=true` in `.env`.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Varnish Docker image](https://hub.docker.com/_/varnish) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 9.0, stable, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web | 80 |


### Data Directory


Data is kept inside the container; a named volume is recommended for persistence.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration is overridden by mounting `./src/default.vcl` to `/etc/varnish/default.vcl`.


## References

- [Varnish Administrator Guide](https://support.websoft9.com/docs/varnish) by Websoft9

- [Docker Hub image](https://hub.docker.com/_/varnish)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
