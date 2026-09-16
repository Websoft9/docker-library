# Spring Boot on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Spring Boot**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the Access URL; the default demo returns `Spring Boot is running...`.
2. Try `GET /hello` for a JSON response and `GET /actuator/health` for the health endpoint.

### Develop In The Container

1. Exec into the container: `docker exec -it springboot bash`.
2. The demo project lives in `/workspace`; edit the Java code there.
3. Run the app with `mvn spring-boot:run`, tests with `mvn test`, or package with `mvn package`.
4. On first start the demo project is generated automatically; replace `/workspace` with your own Maven project to customize it.

### Optional PostgreSQL

1. No database runs by default. To enable the bundled PostgreSQL, uncomment `COMPOSE_PROFILES=postgres` in `.env` and rebuild.
2. That single switch starts the `postgres` service and activates the Spring `postgres` profile, which reads `SPRING_DATASOURCE_*`.
3. When working with the database from the shell, run Maven with `-Ppostgres` so the JDBC starter and driver are on the classpath.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Spring Boot Docker image](https://github.com/spring-projects/spring-boot) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 4.1.1, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 8080 |


### Data Directory


- `springboot_workspace` → `/workspace`
- `springboot_m2` → `/root/.m2`
- `postgres_data` → `/var/lib/postgresql/data`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


- `./src/entrypoint.sh` → `/entrypoint.sh`
- `./src/template` → `/opt/template`



## References

- [Spring Boot Administrator Guide](https://support.websoft9.com/docs/springboot) by Websoft9

- [Docker Hub image](https://github.com/spring-projects/spring-boot)

- [Releases](https://github.com/spring-projects/spring-boot/releases)

- [Official docs](https://docs.spring.io/spring-boot/installing.html)

- [Official docs](https://hub.docker.com/_/maven)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
