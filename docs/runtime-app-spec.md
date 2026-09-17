# Runtime App Spec

| Property | Value |
|---|---|
| Status | Adopted |
| Applies to | runtime/scaffold app packages |
| Purpose | Define the shared entrypoint hook convention and the optional `DATABASE_URL` override |

## Scope

Runtime apps run user-uploaded code instead of shipping a finished application. Current members: `nextjs`, `django`, `springboot`, `laravel`.

## Layout

```
src/
  entrypoint.sh        # orchestrator (container entrypoint)
  entrypoint.d/*.sh    # package hooks
  start.sh             # package start (exec)
```

## Hook Convention

The orchestrator runs hooks from two directories, in order:

1. `/opt/websoft9/entrypoint.d` (package hooks, read-only)
2. `${APP_DIR}/.w9/entrypoint.d` (user hooks, from the source volume)

Rules:

- Hooks are `*.sh`, sorted by filename; use numeric prefixes.
- Same basename: the user hook replaces the package hook.
- New basename: inserted in sort order.
- Hooks run on every start and must be idempotent.
- Hooks run as the container user with `APP_DIR` as the working directory.

Start:

- `${APP_DIR}/.w9/start.sh` if present, otherwise the package `start.sh`.
- The chosen start script must `exec` the server so it becomes PID 1 and receives signals.

Environment available to hooks: `APP_DIR`, `W9_HTTP_PORT`, `W9_VERSION` (plus any app-specific variables).

## DATABASE_URL

Default: **no database**. `django` and `laravel` fall back to SQLite; `nextjs` and `springboot` have none.

`.env` ships it commented:

```
# DATABASE_URL=postgres://user:pass@postgres_xxxx:5432/dbname
```

When set, the runtime overrides the app's database configuration; when unset, the native default is kept. Supported schemes: `postgres`/`postgresql`, `mysql`/`mariadb`.

| App | Mapping |
|---|---|
| nextjs | passed through as `process.env.DATABASE_URL` |
| django | parsed into `DATABASES["default"]` |
| springboot | `SPRING_DATASOURCE_URL` (JDBC) + `postgres`/`mysql` profile |
| laravel | `DB_CONNECTION` + `DB_URL` |

## Notes

- Base-image hooks that run in subshells (for example serversideup/php `/etc/entrypoint.d/`) cannot export to the main process; app env mapping must happen in our orchestrator before hand-off.
- Never bake database credentials into the image or commit them to the package.
