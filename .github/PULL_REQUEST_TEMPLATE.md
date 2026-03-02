## Description

<!-- Briefly describe what this PR does and why. -->

## App(s) affected

<!-- List app names, e.g. wordpress, nginx -->

- 

## Type of change

- [ ] 🆕 New app
- [ ] 🔄 Version update
- [ ] 🛠 Config / compose fix
- [ ] 🐛 Bug fix
- [ ] 📄 Documentation
- [ ] 🔧 CI / build tooling

## Checklist

- [ ] `.env` — `W9_VERSION` is set to a specific tag (not `latest`)
- [ ] `.env` — `W9_LOGIN_USER` / `W9_LOGIN_PASSWORD` included only when app has built-in auth
- [ ] `.env` — `W9_URL_REPLACE=true` included only when `$W9_URL` is referenced in `docker-compose.yml`
- [ ] `docker-compose.yml` — all volume-mapped `./src/*` files exist in the `src/` directory
- [ ] `docker-compose.yml` — all services have `restart: unless-stopped`
- [ ] `apps/{name}/CHANGELOG.md` updated (required for version updates and compose changes)
- [ ] Tested locally with `docker compose up -d` (app started successfully)
- [ ] Cleaned up test environment with `docker compose down -v`

## Notes

<!-- Any additional context, screenshots, or caveats. -->
