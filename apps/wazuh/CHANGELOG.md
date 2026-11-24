# CHANGELOG

## 2026-11-20

- Set the `agent` (`1514`) and `enrollment` (`1515`) port groups to `public: false` per `docs/app-access-spec.md` section 4.2, so agent ports are enabled on demand once agents are ready to enroll. The upstream compose port mappings are left unchanged.

## 2026-11-17

- Migrated `access` to the V2 port-group array and removed deprecated `W9_*` port/URL aliases in `.env` and `docker-compose.yml`.

## 2026-11-04

- Declared the internal OpenSearch-compatible Wazuh Indexer, with HTTPS confirmed by its mounted configuration.
- Recorded existing INDEXER_* and DASHBOARD_* account sources, excluding password hashes and Wazuh API credentials from database password metadata.
- Excluded certificate generation, sysctl helpers, manager, and dashboard as database instances; runtime configuration and image versions are unchanged.

## 2026-09-20

- Rebuild the package as the official Wazuh single-node stack (manager, indexer and dashboard at 4.14.7).
- Replace the placeholder WordPress package with Wazuh configs, ports, environment variables and tests.
- Generate the indexer TLS certificates at deploy time with `wazuh/wazuh-certs-generator`.
- Raise `vm.max_map_count` with a one-shot privileged `busybox` helper before the indexer starts.
- Publish only the required ports (dashboard 5601, agent 1514/1515); keep syslog 514/udp and manager API 55000 commented for optional use.
- Isolate the stack on a per-instance `${W9_ID}-internal` network so multiple Wazuh instances can share the host without hostname/TLS collisions.
