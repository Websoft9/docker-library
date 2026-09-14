# ERPNext on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **ERPNext**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the ERPNext admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [ERPNext Docker image](https://hub.docker.com/r/frappe/erpnext) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: v16, v16.34.2.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 8080 |


### Data Directory


- `apps` → `/home/frappe/frappe-bench/apps`
- `env` → `/home/frappe/frappe-bench/env`
- `sites` → `/home/frappe/frappe-bench/sites`
- `logs` → `/home/frappe/frappe-bench/logs`
- `db-data` → `/var/lib/mysql`
- `redis-queue-data` → `/data`
- `redis-cache-data` → `/data`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `W9_LOGIN_PASSWORD`, `W9_POWER_PASSWORD` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


- `./src/create-site.sh` → `/usr/local/bin/create-site.sh`
- `./src/hrms` → `/opt/hrms-src`



## References

- [ERPNext Administrator Guide](https://support.websoft9.com/docs/erpnext) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/frappe/erpnext)

- [GitHub docs](https://github.com/frappe/frappe_docker)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
