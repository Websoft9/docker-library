# Next.js on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Next.js**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. If the source directory is empty on first boot, Websoft9 scaffolds a default Next.js application automatically.
2. Upload your own Next.js project source into the mounted app directory and rebuild the app.
3. On startup, the container auto-detects `npm`, `pnpm`, or `yarn`, installs dependencies, runs `build`, and starts `next start`.
4. To customize the deploy steps, add hooks under `${APP_DIR}/.w9/entrypoint.d/` or override the start step with `${APP_DIR}/.w9/start.sh`.

### Change Password

1. This runtime package does not create a built-in administrator account.
2. Authentication and secrets depend on the Next.js project you upload.
3. Configure your own application secrets with environment variables or project files inside the mounted source directory.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Next.js Docker image](https://github.com/vercel/next.js) and makes some improvements below.

<!-- W9_NOTE_START -->
The package is a runtime environment for self-hosted Next.js projects, not a finished business application. It uses the official Node image as the runtime and the official `create-next-app` scaffold when the source directory is empty.

`W9_VERSION` tracks the default Next.js framework version used by the scaffold, while `NODE_IMAGE_TAG` controls the underlying Node runtime image tag. The mounted `nextjs_app` volume is the place where users can upload their own project source and keep build output plus the local Next.js filesystem cache.

The deploy steps are hook-based. The orchestrator runs `entrypoint.d/*.sh` from the package and then from `${APP_DIR}/.w9/entrypoint.d/`. A user hook with the same name replaces the package hook; a hook with a new name is inserted in filename order. Users can also override the start step with `${APP_DIR}/.w9/start.sh`. Hooks must be idempotent and run as root.

The package does not bundle a database. To connect your project to a database, uncomment and set `DATABASE_URL` in `.env`, then read it as `process.env.DATABASE_URL` in server-side code.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 16.3.5, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.

### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 3000 |

### Data Directory

Data is persisted in the `nextjs_app` volume, mounted at `/usr/src/app`.

### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.

Note: `NEXTJS_CREATE_FLAGS`, `NEXTJS_PACKAGE_MANAGER` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.

### Configuration Files

Configuration is overridden by mounting `./src/entrypoint.sh` to `/usr/local/bin/entrypoint.sh`.

## References

- [Next.js Administrator Guide](https://support.websoft9.com/docs/nextjs) by Websoft9
- [Docker Hub image](https://github.com/vercel/next.js)
- [Releases](https://github.com/vercel/next.js/releases)
- [Official docs](https://nextjs.org/docs/app/getting-started/installation)
- [Official docs](https://nextjs.org/docs/app/getting-started/deploying)
- [Official docs](https://nextjs.org/docs/app/guides/self-hosting)
- [Official docs](https://hub.docker.com/_/node)

<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.
- A user-uploaded project must provide valid `build` and `start` scripts in `package.json`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.

**Why did Websoft9 create a demo app for me?**
- When `/usr/src/app` is empty on first boot, the entrypoint scaffolds a default Next.js project.
- Replace that content with your own source code in the mounted app volume, then rebuild the container.
<!-- W9_TROUBLESHOOT_END -->
