# Kafka on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Kafka**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Kafka admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Kafka Docker image](https://hub.docker.com/r/apache/kafka) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 4.3.1, 4.2.0, 4.1.0, 4.0.1.


### Ports

| Purpose | Port |
| --- | --- |
| Kafka broker | 9092 |


### Data Directory


Data is persisted in the `kafka_data` volume, mounted at `/var/lib/kafka/data`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Kafka Administrator Guide](https://support.websoft9.com/docs/kafka) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/apache/kafka)

- [Releases](https://github.com/apache/kafka/releases)

- [Official compose](https://raw.githubusercontent.com/apache/kafka/trunk/docker/examples/docker-compose-files/single-node/plaintext/docker-compose.yml)

- [Official docs](https://kafka.apache.org/documentation/)

- [GitHub docs](https://github.com/apache/kafka/tree/trunk/docker/examples)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
