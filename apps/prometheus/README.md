# Prometheus on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Prometheus**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the Prometheus web console from the **Access** tab.
2. Use **Status → Targets** to confirm the `prometheus` job is up, then query metrics with PromQL on the **Graph** page.

### Add Scrape Targets

1. Edit `apps/prometheus/src/prometheus.yml` and add a job under `scrape_configs`.
2. Rebuild the app so the updated config is mounted.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Prometheus Docker image](https://hub.docker.com/r/prom/prometheus) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: v3.14.0, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 9090 |


### Data Directory


- `prometheus` → `/prometheus`
- `alertmanager` → `/alertmanager`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration is overridden by mounting `./src/prometheus.yml` to `/etc/prometheus/prometheus.yml`.


## References

- [Prometheus Administrator Guide](https://support.websoft9.com/docs/prometheus) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/prom/prometheus)

- [Releases](https://github.com/prometheus/prometheus/releases)

- [Official docs](https://prometheus.io/docs/prometheus/latest/installation/)

- [GitHub docs](https://github.com/prometheus/prometheus)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
