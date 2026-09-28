# Vespa on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Vespa**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

Vespa has no web UI or built-in login; use the Vespa CLI or the REST API.

1. Deploy an application package to the config server on port 19071, for example `vespa deploy --target http://<host>:19071 ./app`.
2. After the application is deployed, the query and document API becomes available on port 8080.
3. Query it with `curl 'http://<host>:8080/search/?yql=select * from sources * where true'`.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Vespa Docker image](https://hub.docker.com/r/vespaengine/vespa) and makes some improvements below.

<!-- W9_NOTE_START -->
Vespa has no built-in authentication. The HTTP API on port 8080 is open by default and only starts after an application package is deployed. The config server on port 19071 is an unauthenticated deployment endpoint; expose it only to trusted networks. Secure access with TLS, client certificates (mTLS), or HTTP filter chains in the application package.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 8.751.13, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| HTTP API (query/document) | 8080 |
| Config server (deployment API) | 19071 |


### Data Directory


- `vespa-var` → `/opt/vespa/var`
- `vespa-logs` → `/opt/vespa/logs`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Vespa Administrator Guide](https://support.websoft9.com/docs/vespa) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/vespaengine/vespa)

- [Releases](https://github.com/vespa-engine/vespa/releases)

- [Official docs](https://docs.vespa.ai/en/operations/self-managed/docker-containers.html)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
