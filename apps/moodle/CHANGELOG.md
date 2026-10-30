# CHANGELOG

## 2026-10-30

- Update Moodle to 5.3.

## 2026-09-17

- Switch to the upstream `elestio/moodle:v5.2.2` image and remove the local Dockerfile and entrypoint.
- Align environment variables with the image (`MOODLE_DATABASE_*`, `MOODLE_HOST`, `MOODLE_USERNAME`, ...).
- Keep PHP overrides by mounting `src/php.ini` to `/usr/local/etc/php/conf.d/zz-websoft9.ini`; document the image's PHP configuration locations and the `PHP_INI-*` mechanism.
- Add an app healthcheck, `tests/cases.yml`, and repository catalog data.
