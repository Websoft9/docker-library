# CHANGELOG

## 2026-09-17

- Split the Spring Boot startup into ordered hooks under `src/entrypoint.d/` plus a `src/start.sh`, with a user hook directory at `/workspace/.w9/entrypoint.d/` and an optional `/workspace/.w9/start.sh` override.
- Removed the bundled PostgreSQL service and the `COMPOSE_PROFILES` switch; the default project needs no database.
- Added an optional `DATABASE_URL` in `.env`; when set, the runtime maps it to the Spring datasource properties and enables the matching profile (`postgres://` → `postgres`, `mysql://` → `mysql`).

## 2026-09-16

- Initial package: Spring Boot starter workspace based on the official `maven:3.9-eclipse-temurin-21` image, without a custom Dockerfile.
- Bootstrap a default Spring Boot demo project into the `/workspace` named volume on first start, then run it with `mvn spring-boot:run`.
- Add Maven dependency cache volume, `/actuator/health` healthcheck, and `tests/cases.yml`.
- Add an optional bundled PostgreSQL, disabled by default and enabled with the single `COMPOSE_PROFILES=postgres` switch; the container then activates the Spring `postgres` profile and the `postgres` Maven profile.
- Add `upstream` metadata and repository catalog data.
