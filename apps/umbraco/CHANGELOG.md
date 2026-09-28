# CHANGELOG

## 2026-09-20
- Rebuild the Umbraco package from the official Umbraco Docker guidance as a self-contained app.
- Build the Umbraco CMS 18.2.0 image from `Umbraco.Templates` on `mcr.microsoft.com/dotnet/aspnet:10.0` via `Dockerfile`.
- Use SQLite for storage (`/app/umbraco/Data/Umbraco.sqlite.db`) with a persisted data volume; no external database service.
- Create the administrator account on first start through Umbraco unattended install using `W9_LOGIN_USER` / `W9_LOGIN_PASSWORD`.
- Add `tests/cases.yml` with a backoffice reachability check.

## 2026-09-22
- Disable OpenIddict's HTTPS transport requirement in the generated Umbraco app so backoffice login can work on HTTP-only deployments.
- Keep ASP.NET Core forwarded headers enabled for reverse-proxy deployments while restoring the package application URL to `http://${W9_URL}`.
- Remove local image build instructions from `docker-compose.yml` so runtime deploys use the published `${W9_REPO}:${W9_VERSION}` image directly.
- Bump the package/image version to `18.2.0-hotfix.1` and strip the hotfix suffix inside `Dockerfile` so image tags can change without breaking the upstream Umbraco template install version.

## 2026-09-23
- Switch the package to HTTPS-by-default using a self-signed certificate generated at container start and persisted under `/app/umbraco/certs`.
- Restore Umbraco's HTTPS enforcement for backoffice authentication while keeping the stable package/image tag at `18.2.0`.
- Add Serilog console output so application logs appear in `docker logs` while preserving the existing Umbraco file sink.
- Simplify the Dockerfile by removing the temporary hotfix tag parsing and the unnecessary `apt-get install openssl` layer.
- Switch `dotnet new install` to the modern `@` version syntax and add standard OCI image labels.
- Declare `access.defaultScheme` as `https` for machine-readable HTTPS metadata.
