# Zulip on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Zulip**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Zulip admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Zulip Docker image](https://ghcr.io/zulip/zulip-server) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 12.2-0.


### Ports

| Purpose | Port |
| --- | --- |
| HTTPS | 443 |


### Data Directory


Data is kept inside the container; a named volume is recommended for persistence.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `W9_LOGIN_USER`, `W9_LOGIN_PASSWORD`, `W9_ZULIP_REALM_NAME`, `W9_ZULIP_REALM_STRING_ID`, `W9_ZULIP_ADMIN_FULL_NAME` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


Configuration is overridden by mounting `./src/create-default-realm.sh` to `/data/post-setup.d/10-create-default-realm.sh`.


## References

- [Zulip Administrator Guide](https://support.websoft9.com/docs/zulip) by Websoft9

- [GHCR image](https://ghcr.io/zulip/zulip-server)

- [Releases](https://github.com/zulip/docker-zulip/releases)

- [GitHub docs](https://github.com/zulip/docker-zulip/blob/main/README.md)

- [Official docs](https://zulip.readthedocs.io/projects/docker/en/latest/how-to/compose-upgrading-from-legacy.html)

- [Official docs](https://zulip.readthedocs.io/projects/docker/en/latest/reference/environment-vars.html)

- [Official docs](https://zulip.readthedocs.io/en/latest/production/management-commands.html)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
