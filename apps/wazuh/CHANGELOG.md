# CHANGELOG

## 2026-09-20

- Rebuild the package as the official Wazuh single-node stack (manager, indexer and dashboard at 4.14.7).
- Replace the placeholder WordPress package with Wazuh configs, ports, environment variables and tests.
- Generate the indexer TLS certificates at deploy time with `wazuh/wazuh-certs-generator`.
- Raise `vm.max_map_count` with a one-shot privileged `busybox` helper before the indexer starts.
- Publish only the required ports (dashboard 5601, agent 1514/1515); keep syslog 514/udp and manager API 55000 commented for optional use.
- Isolate the stack on a per-instance `${W9_ID}-internal` network so multiple Wazuh instances can share the host without hostname/TLS collisions.
