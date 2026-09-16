# CHANGELOG

## 2026-09-15

- Added the initial Next.js runtime package, based on the official Node image.
- Added a runtime scaffold entrypoint that creates a default Next.js 16.3.5 project when the source directory is empty.
- Added automatic package-manager detection (`npm` / `pnpm` / `yarn`), dependency install, production build, and `next start` execution for uploaded user source code.
- Split the deploy flow into ordered hooks under `src/entrypoint.d/` plus a `src/start.sh`, with a user hook directory at `${APP_DIR}/.w9/entrypoint.d/` and an optional `${APP_DIR}/.w9/start.sh` override.
- Added a main-container healthcheck and app-local metadata, tests, and catalog data for the runtime/scaffold workflow.
- Added a commented `DATABASE_URL` example in `.env` and documented how to connect an external database from server-side code.
