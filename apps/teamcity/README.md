# TeamCity on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **TeamCity**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### First-run setup

1. Open the app URL; TeamCity shows a maintenance page titled **Confirming TeamCity first start**.
2. Click **I'm a server administrator, show me the details**, then **Proceed**.
3. On **Setting up database connection**, choose **MySQL** and use the **Download** button to fetch the JDBC driver (the image does not bundle it). To install it manually, put `mysql-connector-j-*.jar` in the `teamcity_data` volume under `lib/jdbc`, then click **Refresh JDBC drivers**.
4. Enter the connection details: host `teamcity-mysql`, port `3306`, database `teamcity`, user `teamcity`, password from `W9_POWER_PASSWORD` in `.env`.
5. Accept the driver license, then create the first administrator account.

### Build agents

The bundled `teamcity-agent` connects to the server automatically but must be authorized: after signing in, open **Agents → Unauthorized** and click **Authorize** for the agent.

### Change Password

TeamCity accounts are managed inside the application. Change the administrator password from the account profile, or reset other users under **Administration → Users**.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [TeamCity Docker image](https://hub.docker.com/r/jetbrains/teamcity-server) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 2026.2, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 8111 |


### Data Directory


- `teamcity_data` → `/data/teamcity_server/datadir`
- `teamcity_logs` → `/opt/teamcity/logs`
- `teamcity_temp` → `/opt/teamcity/temp`
- `agent_conf` → `/data/teamcity_agent/conf`
- `/var/run/docker.sock` → `/var/run/docker.sock`
- `agent_work` → `/opt/buildagent/work`
- `agent_temp` → `/opt/buildagent/temp`
- `agent_tools` → `/opt/buildagent/tools`
- `agent_plugins` → `/opt/buildagent/plugins`
- `agent_system` → `/opt/buildagent/system`
- `agent_logs` → `/opt/buildagent/logs`
- `agent_docker` → `/var/lib/docker`
- `mysql_data` → `/var/lib/mysql`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [TeamCity Administrator Guide](https://support.websoft9.com/docs/teamcity) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/jetbrains/teamcity-server)

- [Releases](https://www.jetbrains.com/teamcity/download/)

- [Official docs](https://www.jetbrains.com/help/teamcity/teamcity-documentation.html)

- [GitHub docs](https://github.com/JetBrains/teamcity-docker-server)

- [GitHub docs](https://github.com/JetBrains/teamcity-docker-samples)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
