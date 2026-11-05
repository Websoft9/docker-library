## 2026-11-04

- Declared the current base stack's single internal PostgreSQL instance with the main and _supabase databases.
- Recorded seven known account sources from active consumers and mounted SQL, without inventing a usage for the unconfirmed supabase_functions_admin consumer.
- Excluded API, metadata, pooler, gateway, and other helper services as database instances.
- Kept the complex bundled stack internal-only; removed the external provider and connection mapping.
- Restored the original PostgreSQL initialization references and POSTGRES_PASSWORD first-startup marker rather than separating inputs solely for external databases.
- Preserved role-specific consumers, shared-password SQL, and pooler configuration; metadata does not rotate roles, migrate data, or update existing Supavisor tenants.
- Passed static configuration and regression checks without deployment or live database verification; SQL scripts, images, volumes, and startup dependencies are unchanged.

## 2026-09-12

- Rebuilt the Supabase package against the official self-hosted Docker stack `self-hosted/v0.8.1`.
- Replaced the 2023-era Kong-based compose with the current Envoy + Supavisor + Postgres 17 upstream base stack.
- Fixed broken bind mounts by aligning the package to the upstream `docker/volumes` file set under `src/`.
- Normalized the package to current repository conventions for `W9_*` variables, metadata, README generation, and policy gates.
