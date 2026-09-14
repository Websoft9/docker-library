# SonarQube on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **SonarQube**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the SonarQube admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [SonarQube Docker image](https://hub.docker.com/_/sonarqube) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 26.9.0.129388-community, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 9000 |


### Data Directory


- `sonarqube_data` → `/opt/sonarqube/data`
- `sonarqube_extensions` → `/opt/sonarqube/extensions`
- `sonarqube_logs` → `/opt/sonarqube/logs`
- `sonarqube_temp` → `/opt/sonarqube/temp`
- `postgresql_data` → `/var/lib/postgresql/data`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [SonarQube Administrator Guide](https://support.websoft9.com/docs/sonarqube) by Websoft9

- [Docker Hub image](https://hub.docker.com/_/sonarqube)

- [Releases](https://github.com/SonarSource/docker-sonarqube/releases)

- [Official compose](https://github.com/SonarSource/docker-sonarqube/blob/master/example-compose-files/sq-with-postgres/docker-compose.yml)

- [GitHub docs](https://github.com/SonarSource/docker-sonarqube)

- [Official docs](https://docs.sonarsource.com/sonarqube-server/server-installation/from-docker-image/)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
