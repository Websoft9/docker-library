# CHANGELOG

## 2026-09-16

- Initial package: Spring Boot starter workspace based on the official `maven:3.9-eclipse-temurin-21` image, without a custom Dockerfile.
- Bootstrap a default Spring Boot demo project into the `/workspace` named volume on first start, then run it with `mvn spring-boot:run`.
- Add Maven dependency cache volume, `/actuator/health` healthcheck, and `tests/cases.yml`.
- Add an optional bundled PostgreSQL, disabled by default and enabled with the single `COMPOSE_PROFILES=postgres` switch; the container then activates the Spring `postgres` profile and the `postgres` Maven profile.
- Add `upstream` metadata and repository catalog data.
