# Supabase on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Supabase**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open Supabase from the published web port and sign in to Studio with the dashboard basic auth credentials.
2. The main entrypoint is the API gateway on port `8000`, exposed by `W9_HTTP_PORT_SET`; Studio, Auth, REST, Realtime, Storage, and Functions all sit behind that gateway.
3. Keep the bundled Postgres and Supavisor services internal unless you intentionally redesign the stack.

### Change Password

1. Change the Studio dashboard password by updating `W9_LOGIN_PASSWORD` / `DASHBOARD_PASSWORD` in `.env` and recreating the `api-gw` service.
2. Do not rely on changing `POSTGRES_PASSWORD` after the first startup; the upstream stack treats the database password as an initialized secret and changing it later requires a dedicated rotation procedure.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Supabase Docker image](https://github.com/supabase/supabase/releases/tag/self-hosted/v0.8.1) and makes some improvements below.

<!-- W9_NOTE_START -->
This package rebuilds Supabase against the official self-hosted Docker stack `self-hosted/v0.8.1`.

The base package keeps the upstream default Envoy gateway, Supavisor pooler, bundled Postgres 17, and the core Studio/Auth/Rest/Realtime/Storage/Functions services.

Optional upstream overrides such as Kong, PgBouncer, S3/MinIO, TLS proxies, and logs/analytics are intentionally not enabled in this base package.

The stack still accepts the legacy symmetric `JWT_SECRET`, `ANON_KEY`, and `SERVICE_ROLE_KEY` values from the upstream example configuration. Rotate all placeholder secrets before production use.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 0.8.1.


### Ports

| Purpose | Port |
| --- | --- |
| API Gateway / Studio | 8000 |


### Data Directory


- `supabase_snippets` → `/app/snippets`
- `supabase_storage` → `/var/lib/storage`
- `deno-cache` → `/root/.cache/deno`
- `supabase_db` → `/var/lib/postgresql/data`
- `db-config` → `/etc/postgresql-custom`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `POSTGRES_PASSWORD` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


- `./src/functions` → `/app/edge-functions`
- `./src/api/envoy/envoy.yaml` → `/etc/envoy/envoy.yaml`
- `./src/api/envoy/cds.yaml` → `/etc/envoy/cds.yaml`
- `./src/api/envoy/lds.template.yaml` → `/etc/envoy/lds.template.yaml`
- `./src/api/envoy/docker-entrypoint.sh` → `/docker-entrypoint.sh`
- `./src/functions` → `/home/deno/functions`
- `./src/db/realtime.sql` → `/docker-entrypoint-initdb.d/migrations/99-realtime.sql`
- `./src/db/webhooks.sql` → `/docker-entrypoint-initdb.d/init-scripts/98-webhooks.sql`
- `./src/db/roles.sql` → `/docker-entrypoint-initdb.d/init-scripts/99-roles.sql`
- `./src/db/jwt.sql` → `/docker-entrypoint-initdb.d/init-scripts/99-jwt.sql`
- `./src/db/_supabase.sql` → `/docker-entrypoint-initdb.d/migrations/97-_supabase.sql`
- `./src/db/logs.sql` → `/docker-entrypoint-initdb.d/migrations/99-logs.sql`
- `./src/db/pooler.sql` → `/docker-entrypoint-initdb.d/migrations/99-pooler.sql`
- `./src/pooler/pooler.exs` → `/etc/pooler/pooler.exs`



## References

- [Supabase Administrator Guide](https://support.websoft9.com/docs/supabase) by Websoft9

- [Docker Hub image](https://github.com/supabase/supabase/releases/tag/self-hosted/v0.8.1)

- [Releases](https://github.com/supabase/supabase/tags)

- [Official compose](https://raw.githubusercontent.com/supabase/supabase/self-hosted/v0.8.1/docker/docker-compose.yml)

- [Official env example](https://raw.githubusercontent.com/supabase/supabase/self-hosted/v0.8.1/docker/.env.example)

- [Official docs](https://supabase.com/docs/guides/self-hosting/docker)

- [GitHub docs](https://github.com/supabase/supabase/blob/master/docker/CHANGELOG.md)

- [GitHub docs](https://github.com/supabase/supabase/blob/master/docker/versions.md)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs` and verify the gateway, Studio, Auth, PostgREST, Storage, Realtime, Postgres, and Supavisor services all reach a healthy or running state. Supabase is a coordinated stack; one failed dependency can block the dashboard or API.

**Dashboard not reachable?**
- The user-facing entrypoint is the API gateway on `W9_HTTP_PORT_SET` (internal port `8000`), not the Studio container's internal `3000` port.

**Database password changed after first boot?**
- `POSTGRES_PASSWORD` is effectively first-startup-only for the initialized stack. If you need to rotate it later, follow the upstream self-hosted database password rotation procedure instead of only editing `.env`.

**Want Kong, PgBouncer, logs, S3/MinIO, or TLS proxy support?**
- Those upstream features require additional compose override files and extra configuration. They are intentionally omitted from this base package.
<!-- W9_TROUBLESHOOT_END -->
