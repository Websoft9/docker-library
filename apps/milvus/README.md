# Milvus on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Milvus**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Milvus admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Milvus Docker image](https://hub.docker.com/r/milvusdb/milvus) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: v3.0.3, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Milvus WebUI | 9091 |
| Milvus SDK/gRPC endpoint | 19530 |


### Data Directory


- `milvus_data` → `/var/lib/milvus`
- `etcd_data` → `/etcd`
- `minio_data` → `/minio_data`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Milvus Administrator Guide](https://support.websoft9.com/docs/milvus) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/milvusdb/milvus)

- [Releases](https://github.com/milvus-io/milvus/releases)

- [Official compose](https://raw.githubusercontent.com/milvus-io/milvus/v3.0.3/deployments/docker/standalone/docker-compose.yml)

- [Official docs](https://milvus.io/docs/install_standalone-docker-compose.md)

- [Official docs](https://milvus.io/docs/milvus-webui.md)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
