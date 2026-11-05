# CHANGELOG

## 2026-11-05

- Remote fresh install and retained-data recreation passed using the published `websoft9dev/canvas:2026-05-20.143` image after removing unused completed-test images.
- Verified web/jobs service state, PostgreSQL health, the login page and database marker retention; no source rebuild was required for the Compose-only change.
- Independent baseline image migration, account login and external database connections were not tested.

## 2026-11-04

- Declared internal PostgreSQL and unauthenticated Redis dependencies using the existing web/jobs inputs confirmed by the ERB templates.
- Separated bundled PostgreSQL initialization from the application's password input and stopped injecting the full application env file into the database service.
- Declared external PostgreSQL inputs without changing templates, bootstrap scripts, default connections or image versions; no Redis database name or PostgreSQL port input was invented.
- Static configuration checks passed; deployment and live connection validation were not performed.

## 2026-10-13
- Verified `release/2026-05-20.143` is still the newest stable upstream Canvas tag available for this package.
- Added `tests/cases.yml` so deploy validation checks the Canvas login entry path instead of relying only on default root reachability.
- Disabled Git auto-maintenance during the image build to avoid Bundler git dependency clone failures on `maintenance.lock`.

## 2026-08-31
- Created the initial Canvas app package.
- Added a custom source-based Canvas image build using the official upstream Dockerfile pattern.
- Added web, jobs, PostgreSQL, and Redis services.
- Added first-start bootstrap for database setup and administrator creation.
- Switched the Canvas source target from an old `v5.14.2` tag to the current official `release/2026-05-20.143` line.
- Aligned the Dockerfile more closely with the official production build flow to fix asset compile incompatibilities.
