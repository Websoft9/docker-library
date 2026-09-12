# RabbitMQ on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **RabbitMQ**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the management UI at `http://<host>:15672` and sign in with `admin` and the password from `.env`.
2. Connect AMQP clients to port `5672` with the same credentials.
3. Manage users, virtual hosts, queues, and exchanges from the management UI.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update `W9_POWER_PASSWORD` in `.env` and save.
3. Rebuild the app. `RABBITMQ_DEFAULT_USER` / `RABBITMQ_DEFAULT_PASS` only apply on first startup, so for an existing broker also change the password in the management UI or with `rabbitmqctl change_password`.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [RabbitMQ Docker image](https://hub.docker.com/_/rabbitmq) and makes some improvements below.

<!-- W9_NOTE_START -->
The image tag is pinned to `4.3-management`, which ships the management plugin. The `rabbitmq_data` volume persists broker state under `/var/lib/rabbitmq`, the only volume the official image declares.

Custom configuration lives in `src/rabbitmq.conf`, mounted read-only to `/etc/rabbitmq/conf.d/99-websoft9.conf`. It is merged after the image defaults in `/etc/rabbitmq/conf.d/10-defaults.conf`, so the `99-` prefix lets you override defaults; set only the keys you need.

Upgrading from `4.1.x` to `4.3.x` is not a direct in-place upgrade: the official upgrade path goes through `4.2.x` first. Enable all required feature flags before upgrading, and note that deprecated features are disabled by default and classic queue v1 storage is removed in `4.3.0`.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 4.3-management.


### Ports

| Purpose | Port |
| --- | --- |
| Erlang distribution (epmd) | 4369 |
| AMQP 0-9-1 | 5672 |
| Management UI | 15672 |


### Data Directory


Data is persisted in the `rabbitmq_data` volume, mounted at `/var/lib/rabbitmq`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `RABBITMQ_DEFAULT_USER`, `RABBITMQ_DEFAULT_PASS` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


Configuration is overridden by mounting `./src/rabbitmq.conf` to `/etc/rabbitmq/conf.d/99-websoft9.conf`.


## References

- [RabbitMQ Administrator Guide](https://support.websoft9.com/docs/rabbitmq) by Websoft9

- [Docker Hub image](https://hub.docker.com/_/rabbitmq)

- [Releases](https://github.com/rabbitmq/rabbitmq-server/releases)

- [GitHub docs](https://github.com/docker-library/rabbitmq)

- [Official docs](https://www.rabbitmq.com/docs)

- [Official docs](https://www.rabbitmq.com/docs/upgrade)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.

**Upgrading from RabbitMQ 4.1 or 3.13?**
- `4.3.0` only upgrades in place from `4.2.x`. Go through `4.2` first, enable all required feature flags, and review the `4.3.0` breaking changes before switching the image tag.
<!-- W9_TROUBLESHOOT_END -->
