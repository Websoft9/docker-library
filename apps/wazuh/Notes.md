# Wazuh Notes

> Internal maintenance notes. Customer-facing documentation lives in `README.md`.

## Sources

- Official images: `wazuh/wazuh-manager`, `wazuh/wazuh-indexer`, `wazuh/wazuh-dashboard`
- Official deployment: https://github.com/wazuh/wazuh-docker (single-node, tag `v4.14.7`)
- Docs: https://documentation.wazuh.com/current/deployment-options/docker/wazuh-container.html

## Version coupling

The manager, indexer and dashboard images must always share the same version. `W9_VERSION` drives
all three images and the `CERT_TOOL_VERSION` used by the certificate generator (`4.14` for the
`4.14.x` line). Update them together.

Wazuh publishes full patch tags only (`4.14.7`), so the package intentionally pins `x.x.x` instead
of an `x.x` tag.

## Host prerequisite: vm.max_map_count

The indexer (OpenSearch based) needs `vm.max_map_count >= 262144`. The `busybox` service runs a
privileged one-shot `sysctl -w vm.max_map_count=262144` before the indexer starts. If the host
already reports a higher value, the command is a no-op. On hosts that block this, set it manually:

```bash
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf && sudo sysctl -p
```

## TLS certificates

The `wazuh-certs` service runs `wazuh/wazuh-certs-generator:0.0.4`, which downloads
`wazuh-certs-tool.sh` from `packages.wazuh.com` and writes the certificates into the bind-mounted
`src/wazuh_indexer_ssl_certs/` directory. Generation runs only when `wazuh.indexer.pem` is absent,
and the stale `/wazuh-certificates` work dir is removed first, so repeated `docker compose up` does
not rotate the certificates.

Do not switch this back to a named volume: `wazuh/wazuh-indexer` ships stock demo certificates at
`/usr/share/wazuh-indexer/config/certs/`, and Docker would copy them into a fresh named volume
before the generator runs, making the guard skip generation and leaving the indexer without the
`wazuh.indexer.pem` it expects.

- The generated directory is forced to `755` after generation so the `wazuh` (999) and
  `wazuh-indexer`/`wazuh-dashboard` (1000) users can traverse it.
- To rotate the certificates, delete `src/wazuh_indexer_ssl_certs/*` and recreate the stack:
  `docker compose down && docker compose up -d`.
- The container paths differ from upstream because the whole volume is mounted as a directory:
  the manager reads from `/etc/ssl/wazuh/`, the indexer from
  `/usr/share/wazuh-indexer/config/certs/`, the dashboard from
  `/usr/share/wazuh-dashboard/certs/`.

## Startup ordering

The dashboard must not start before the indexer can serve requests, otherwise its first saved
objects migration (`.kibana_1`) times out and the dashboard waits forever. The indexer therefore
defines a healthcheck (`_cluster/health` with the admin credentials) and the manager and dashboard
depend on `service_healthy`.

If a deployment is interrupted and the dashboard reports
`Another OpenSearch Dashboards instance appears to be migrating the index`, delete the broken index
and restart the dashboard:

```bash
docker exec ${W9_ID}-indexer curl -k -s -u admin:${W9_LOGIN_PASSWORD} -X DELETE https://localhost:9200/.kibana_1
docker restart ${W9_ID}
```

## Multi-instance isolation

The upstream single-node stack uses fixed hostnames (`wazuh.indexer`, `wazuh.manager`,
`wazuh.dashboard`) that are baked into the certificates and configs. On the shared `websoft9`
network these names collide with any other Wazuh instance, causing clients to reach the wrong
indexer/manager and fail with `SSLHandshakeException (unknown_ca)`.

To keep instances isolated, the manager, indexer and dashboard join a per-instance private bridge
network `${W9_ID}-internal`; only the dashboard is also attached to `websoft9` for platform access.
Keep it this way: dropping the private network reintroduces the collision. `hostname` alone cannot
fix it because Compose always registers the service name as a network alias.

## Credentials

- Dashboard login: `admin` / `SecretPassword` (`W9_LOGIN_USER` / `W9_LOGIN_PASSWORD`).
- The password is defined by the bcrypt hash in `src/internal_users.yml`, which the indexer loads
  only when it initializes a fresh security index. Changing `W9_LOGIN_PASSWORD` in `.env` does not
  rewrite an existing deployment.
- Internal service accounts keep the upstream defaults: `kibanaserver`/`kibanaserver` and
  `wazuh-wui`/`MyS3cr37P450r.*-`.
- Rotate credentials with the Wazuh `wazuh-passwords-tool.sh` inside the manager, or by recreating
  the stack with an updated `src/internal_users.yml` hash.

## Ports

| Purpose | Host variable | Container |
| --- | --- | --- |
| Web Console (HTTPS) | `W9_HTTPS_PORT_SET` | 5601 |
| Agent Connection | `W9_AGENT_PORT_SET` | 1514 |
| Agent Enrollment | `W9_ENROLLMENT_PORT_SET` | 1515 |
| Syslog Collection (optional) | `W9_SYSLOG_UDP_PORT_SET` | 514/udp |
| Manager API (optional) | `W9_API_PORT_SET` | 55000 |

The syslog and API ports are commented out in `docker-compose.yml` (and their `_SET` vars are commented
in `.env`). The dashboard reaches the manager API over the Docker network, so 55000 only needs to be
published for external automation; 514/udp only for external syslog sources.

## Known limits

- The dashboard is HTTPS-only, so the package has no `W9_HTTP_PORT_SET`; the deploy test uses the
  `tests/check.sh` HTTPS probe instead of the adaptive HTTP web-access check.
- First startup takes a few minutes while the indexer builds its security index.
