# ActiveMQ on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **ActiveMQ**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the ActiveMQ admin console.
2. On the **Send** page, send a message to a temporary queue.
3. On the **Browse** page, confirm the enqueue count increased, verifying the messaging path works.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the ActiveMQ app's **Compose** tab.
2. Update `W9_LOGIN_PASSWORD` in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [ActiveMQ Docker image](https://hub.docker.com/r/apache/activemq/tags) and makes some improvements below.

<!-- W9_NOTE_START -->
- To make the Web Console reachable through the published port, the package adds `src/entrypoint.sh`, which opens the console IP allow-list and fixes 5.19 auth/CSP quirks across versions.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 6.3.0, 6.2.8, 5.19.9, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 8161 |
| AMQP | 5672 |
| OpenWire | 61616 |
| STOMP | 61613 |


### Data Directory


Data is persisted in the `activemq_data` volume, mounted at `/opt/apache-activemq/data`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration is overridden by mounting `./src/entrypoint.sh` to `/opt/websoft9/entrypoint.sh`.


## References

- [ActiveMQ Administrator Guide](https://support.websoft9.com/docs/activemq) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/apache/activemq/tags)

- [Releases](https://github.com/apache/activemq/releases)

- [GitHub docs](https://github.com/apache/activemq/tree/main/assembly/src/docker)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App keeps restarting?**
- Check `docker compose logs` for a startup parameter or config file issue.

**Web Console returns 403?**
- Confirm `src/entrypoint.sh` took effect (the IP allow-list is opened automatically).
- If it returns 401, authentication failed; check the password in `.env`.

**Port not reachable?**
- Ensure the cloud security group / firewall allows the port.
<!-- W9_TROUBLESHOOT_END -->

