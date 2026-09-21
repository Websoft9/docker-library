# CHANGELOG

## 2026-09-20
- Rebuild the Umbraco package from the official Umbraco Docker guidance as a self-contained app.
- Build the Umbraco CMS 18.2.0 image from `Umbraco.Templates` on `mcr.microsoft.com/dotnet/aspnet:10.0` via `Dockerfile`.
- Use SQLite for storage (`/app/umbraco/Data/Umbraco.sqlite.db`) with a persisted data volume; no external database service.
- Create the administrator account on first start through Umbraco unattended install using `W9_LOGIN_USER` / `W9_LOGIN_PASSWORD`.
- Add `tests/cases.yml` with a backoffice reachability check.
