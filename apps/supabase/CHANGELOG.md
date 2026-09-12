## 2026-09-12

- Rebuilt the Supabase package against the official self-hosted Docker stack `self-hosted/v0.8.1`.
- Replaced the 2023-era Kong-based compose with the current Envoy + Supavisor + Postgres 17 upstream base stack.
- Fixed broken bind mounts by aligning the package to the upstream `docker/volumes` file set under `src/`.
- Normalized the package to current repository conventions for `W9_*` variables, metadata, README generation, and policy gates.
