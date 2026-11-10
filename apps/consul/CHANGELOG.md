# CHANGELOG

## 2026-11-10
- Update Consul to 2.1. The official image now uses `nftables` rather than `iptables` for transparent-proxy traffic redirection.

## 2026-10-13
- Update Consul from `1.22` to `2.0.4` based on the latest stable upstream release line.
- Align `.env` and `docker-compose.yml` with current repository policy for braced variables, protected port layout, and inline published-port purpose comments.
- Simplify the package to expose the Consul HTTP UI/API port only and add app-specific deploy validation coverage.
