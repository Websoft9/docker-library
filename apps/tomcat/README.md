# Tomcat on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Tomcat**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

Tomcat serves the default webapps (ROOT, docs, examples) on port `8080`; this package has no separate admin console.

1. In the Websoft9 console, open **My Apps → Tomcat → Access** to get the URL (`http://<host>:8080`).
2. Open it in a browser; you should see the Apache Tomcat welcome page.

### Deploy a WAR

1. Copy your WAR into the container's `webapps` directory:
   `docker cp app.war ${W9_ID}:/usr/local/tomcat/webapps/`
2. Tomcat auto-deploys it; open `http://<host>:8080/app/`.
3. To deploy at the root, name the file `ROOT.war` (it replaces the default welcome page).

### Customize Startup

Startup runs through `src/entrypoint.sh`, which executes hooks in filename order on every start. Package hooks live in `src/entrypoint.d/`. To add your own without rebuilding, put scripts in the `tomcat` volume at `/usr/local/tomcat/.w9/entrypoint.d/`; a `/usr/local/tomcat/.w9/start.sh` replaces the default start command.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Tomcat Docker image](https://hub.docker.com/_/tomcat) and makes some improvements below.

<!-- W9_NOTE_START -->
- Tomcat data (including `webapps` and `conf`) is persisted in the `tomcat` volume mounted at `/usr/local/tomcat`.
- Startup runs through `src/entrypoint.sh`, which executes hooks from `/opt/websoft9/entrypoint.d` (package) and `/usr/local/tomcat/.w9/entrypoint.d` (user) before starting Tomcat. Hooks run on every start and must be idempotent.
- The default `10-webapps.sh` hook restores the bundled default webapps (`webapps.dist/*` → `webapps`).
- The default `W9_VERSION=11.0-jdk21-temurin` pins Tomcat 11 on JDK 21 LTS; pick another supported tag to change the Tomcat/JDK combination.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 11.0-jdk21-temurin, 11.0-jdk25-temurin, 11.0-jdk17-temurin, 10.1-jdk25-temurin, 10.1-jdk21-temurin, 10.1-jdk17-temurin, 10.1-jdk11-temurin, 9.0-jdk25-temurin, 9.0-jdk21-temurin, 9.0-jdk17-temurin, 9.0-jdk11-temurin, 9.0-jdk8-temurin.


### Ports

| Purpose | Port |
| --- | --- |
| Tomcat HTTP | 8080 |


### Data Directory


Data is persisted in the `tomcat` volume, mounted at `/usr/local/tomcat`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


- `./src/entrypoint.sh` → `/opt/websoft9/entrypoint.sh`
- `./src/entrypoint.d` → `/opt/websoft9/entrypoint.d`
- `./src/start.sh` → `/opt/websoft9/start.sh`



## References

- [Tomcat Administrator Guide](https://support.websoft9.com/docs/tomcat) by Websoft9

- [Docker Hub image](https://hub.docker.com/_/tomcat)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**Root URL returns 404?**
- The default webapps may not have been restored; confirm the `10-webapps.sh` hook ran and `/usr/local/tomcat/webapps/ROOT` exists in the container.

**Container stays unhealthy?**
- Tomcat can take about 30 seconds to start; check `docker compose logs ${W9_ID}`.

**Port not reachable?**
- Confirm `W9_HTTP_PORT_SET` is free and allowed by the firewall / security group.
<!-- W9_TROUBLESHOOT_END -->
