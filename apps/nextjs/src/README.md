# Next.js Runtime

This package runs **your own** Next.js project on a managed Node runtime. It is not a finished application: you upload your project source, and the container installs dependencies, builds, and serves it.

## Where to put your code

- Upload your Next.js project into the app source directory: `/usr/src/app` (the `nextjs_app` volume).
- The directory must contain `package.json`.
- Keep your lockfile (`package-lock.json`, `pnpm-lock.yaml`, or `yarn.lock`) so the runtime picks the right package manager.
- After uploading or changing code, restart or rebuild the app from the Websoft9 console.

If the source directory is empty on first startup, the runtime creates a default Next.js app so the service can start. Replace it with your own project when you are ready.

## What happens on startup

1. Create a default Next.js app when the source directory is empty.
2. Install dependencies with `npm`, `pnpm`, or `yarn` (auto-detected from the lockfile).
3. Build the app for production.
4. Start it with `next start` on port `3000`.

## Connect a database

The runtime does not bundle a database. Connect your project to any database by enabling `DATABASE_URL` in the app `.env`:

1. Install a database app from the Websoft9 appstore (for example PostgreSQL), or prepare an external database such as an RDS instance.
2. In the app `.env`, uncomment and set the connection string:

   ```
   DATABASE_URL=postgres://user:pass@postgres_xxxx:5432/dbname
   ```

3. Restart the app. The variable is passed to the container and is available to your project as `process.env.DATABASE_URL` on the server side.
4. Read it in your code, for example:

   ```ts
   const databaseUrl = process.env.DATABASE_URL
   ```

If you use an ORM such as Prisma or Drizzle, run its migration step from a hook:

```sh
#!/bin/bash
set -euo pipefail
cd "$APP_DIR"
npx prisma migrate deploy
```

`DATABASE_URL` is server-only. Only variables prefixed with `NEXT_PUBLIC_` are exposed to the browser, so never put credentials in `NEXT_PUBLIC_*`.

## Customize the deploy steps

Add your own shell hooks inside your project:

```
.w9/
  entrypoint.d/
    15-migrate.sh     # new step, inserted between scaffold and install
    30-build.sh       # same name, replaces the default build step
  start.sh            # replaces the default start step
```

Rules:

- Hooks are `*.sh` files, executed in filename order. Use number prefixes to control the order.
- The same filename **replaces** the package hook. A new filename is **inserted** in order.
- Hooks run on every startup, so they must be safe to run more than once (idempotent).
- Hooks run as root, with the working directory set to `/usr/src/app`.

### Example: run a database migration before build

```sh
#!/bin/bash
set -euo pipefail
cd "$APP_DIR"
npm run db:migrate
```

### Example: custom start command

```sh
#!/bin/bash
set -euo pipefail
cd "$APP_DIR"
exec npm run start -- --hostname 0.0.0.0 --port "$W9_HTTP_PORT"
```

The start script must `exec` the server so it keeps receiving stop signals.

## Environment available to hooks

| Variable | Meaning |
| --- | --- |
| `APP_DIR` | Project directory (`/usr/src/app`) |
| `W9_HTTP_PORT` | Internal HTTP port the app must listen on (`3000`) |
| `W9_VERSION` | Next.js version used by the default scaffold |
| `NODE_IMAGE_TAG` | Node runtime image tag |
| `PACKAGE_MANAGER` | Detected package manager (`npm`, `pnpm`, `yarn`) |

## Troubleshooting

- **The container does not start**: a hook failed. Check the container logs; the failing hook name is printed before the error.
- **Your code is ignored**: make sure `package.json` is directly in `/usr/src/app`.
- **Custom start does not stop cleanly**: make sure `.w9/start.sh` uses `exec`.
- **A demo project keeps being created**: the source directory is empty or has no `package.json`.

## Maintainer reference

Files mounted into the container:

| Container path | Source | Purpose |
| --- | --- | --- |
| `/opt/websoft9/entrypoint.sh` | `src/entrypoint.sh` | Orchestrator (container entrypoint) |
| `/opt/websoft9/entrypoint.d/*.sh` | `src/entrypoint.d/` | Package prepare hooks |
| `/opt/websoft9/start.sh` | `src/start.sh` | Package default start (exec) |

Default prepare hooks:

- `10-scaffold.sh` creates a default Next.js app when the source directory is empty.
- `20-install.sh` installs dependencies with the detected package manager.
- `30-build.sh` runs the production build.

Start resolution:

- If `${APP_DIR}/.w9/start.sh` exists, it is used.
- Otherwise `/opt/websoft9/start.sh` is used.
- The chosen start script is `exec`'d so the server becomes PID 1 and receives signals.
