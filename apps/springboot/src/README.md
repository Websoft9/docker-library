# About

Files mounted into the container and used by Websoft9.

## Where to put your code

- Put your Spring Boot (Maven) project in `/workspace` (the `springboot_workspace` volume). It must contain `pom.xml`.
- Restart the app from the Websoft9 console after changing code.

## Default behavior

- If `/workspace` is empty, a default Spring Boot project is created from `src/template`.
- No database is required by default.
- `DATABASE_URL` is optional. Uncomment it in `.env` to connect an external database; `postgres://` enables the `postgres` profile and `mysql://` enables the `mysql` profile. The runtime maps it to the Spring datasource.

## Customize the deploy steps

Add hooks under `/workspace/.w9/entrypoint.d/`:

- same filename replaces the package hook
- new filename is inserted in filename order
- override the start step with `/workspace/.w9/start.sh`

Available variables: `APP_DIR`, `W9_HTTP_PORT`, `W9_VERSION`.
