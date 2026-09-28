# Wazuh on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Wazuh**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the dashboard at `https://<host>:${W9_HTTPS_PORT_SET}` and accept the self-signed certificate.
2. Sign in with `admin` / `SecretPassword`.
3. Deploy agents and point them at the manager: agent connection on port `1514`, enrollment on `1515`, syslog on `514/udp`.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update `W9_LOGIN_PASSWORD` in `.env` and the matching bcrypt hash in `src/internal_users.yml`.
3. Recreate the stack so the indexer rebuilds its security index (`docker compose down -v && docker compose up -d`).
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Wazuh Docker image](https://hub.docker.com/r/wazuh/wazuh-dashboard) and makes some improvements below.

<!-- W9_NOTE_START -->
- The manager, indexer and dashboard must run the same version; `W9_VERSION` drives all three images.
- TLS certificates are generated on first start by `wazuh/wazuh-certs-generator` and stored in the `wazuh-certs` volume.
- The indexer requires `vm.max_map_count=262144`; the `busybox` helper service sets it before startup.
- `W9_LOGIN_PASSWORD` takes effect only when the indexer initializes a fresh security index.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 4.14.7.


### Ports

| Purpose | Port |
| --- | --- |
| Agent Connection | 1514 |
| Agent Enrollment | 1515 |
| Web Console | 5601 |


### Data Directory


- `wazuh-indexer-data` → `/var/lib/wazuh-indexer`
- `wazuh_api_configuration` → `/var/ossec/api/configuration`
- `wazuh_etc` → `/var/ossec/etc`
- `wazuh_logs` → `/var/ossec/logs`
- `wazuh_queue` → `/var/ossec/queue`
- `wazuh_var_multigroups` → `/var/ossec/var/multigroups`
- `wazuh_integrations` → `/var/ossec/integrations`
- `wazuh_active_response` → `/var/ossec/active-response/bin`
- `wazuh_agentless` → `/var/ossec/agentless`
- `wazuh_wodles` → `/var/ossec/wodles`
- `filebeat_etc` → `/etc/filebeat`
- `filebeat_var` → `/var/lib/filebeat`
- `wazuh-dashboard-config` → `/usr/share/wazuh-dashboard/data/wazuh/config`
- `wazuh-dashboard-custom` → `/usr/share/wazuh-dashboard/plugins/wazuh/public/assets/custom`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


- `./src/wazuh_indexer_ssl_certs` → `/certificates`
- `./src/certs.yml` → `/config/certs.yml`
- `./src/wazuh_indexer_ssl_certs` → `/usr/share/wazuh-indexer/config/certs`
- `./src/wazuh.indexer.yml` → `/usr/share/wazuh-indexer/config/opensearch.yml`
- `./src/internal_users.yml` → `/usr/share/wazuh-indexer/config/opensearch-security/internal_users.yml`
- `./src/wazuh_indexer_ssl_certs` → `/etc/ssl/wazuh`
- `./src/wazuh_manager.conf` → `/wazuh-config-mount/etc/ossec.conf`
- `./src/wazuh_indexer_ssl_certs` → `/usr/share/wazuh-dashboard/certs`
- `./src/opensearch_dashboards.yml` → `/usr/share/wazuh-dashboard/config/opensearch_dashboards.yml`
- `./src/wazuh.yml` → `/usr/share/wazuh-dashboard/data/wazuh/config/wazuh.yml`



## References

- [Wazuh Administrator Guide](https://support.websoft9.com/docs/wazuh) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/wazuh/wazuh-dashboard)

- [Releases](https://github.com/wazuh/wazuh/releases)

- [Official compose](https://raw.githubusercontent.com/wazuh/wazuh-docker/v4.14.7/single-node/docker-compose.yml)

- [Official docs](https://documentation.wazuh.com/current/deployment-options/docker/wazuh-container.html)

- [GitHub docs](https://github.com/wazuh/wazuh-docker)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**Indexer exits because `vm.max_map_count` is too low?**
- Run `sudo sysctl -w vm.max_map_count=262144` on the host, then restart the stack.

**Dashboard unreachable or certificate error?**
- The dashboard is HTTPS-only. Use `https://<host>:${W9_HTTPS_PORT_SET}` and accept the self-signed certificate.

**App fails to start?**
- Check `docker compose logs wazuh.indexer wazuh.manager wazuh.dashboard`.
<!-- W9_TROUBLESHOOT_END -->
