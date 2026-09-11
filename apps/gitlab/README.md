# Gitlab on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Gitlab**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open GitLab from the published web port and sign in as `root`.
2. Before first startup, set `W9_URL` to the exact host or host:port users will open in their browser, so GitLab generates the correct web links and clone URLs.
3. Use the published SSH port for Git over SSH; the package maps `${W9_SSH_PORT_SET}` on the host to port `22` inside the container.
4. This package does not start GitLab Runner by default. Start it only when needed with `docker compose --profile runner up -d`, then register it against your GitLab instance.

### Change Password

1. Sign in to GitLab as an administrator and change the password in the web UI, or run `docker exec -it gitlab gitlab-rake "gitlab:password:reset[root]"`.
2. Do not rely on changing `.env` after deployment; the initial root password only applies on first startup with an empty data volume.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Gitlab Docker image](https://hub.docker.com/r/gitlab/gitlab-ce) and makes some improvements below.

<!-- W9_NOTE_START -->
This package uses the official single-container GitLab Docker deployment and keeps PostgreSQL inside the GitLab Omnibus container.

GitLab official upgrade guidance requires stepped upgrade stops across `18.2`, `18.5`, `18.8`, `18.11`, and `19.2` before later `19.x` versions. This package update to `19.3.2-ce.0` was applied by explicit owner direction and should be treated as a high-risk data upgrade for existing installations.

For browser access and generated clone URLs to stay correct, set `W9_URL` to the real externally used host or host:port before the first container startup.

GitLab Runner requires its own registration and `config.toml`; starting an unconfigured runner causes repeated log errors without helping the base GitLab deployment, so it is kept behind an optional compose profile. The profile seeds a minimal `config.toml` with no deployment-specific parameters, so the runner starts cleanly and can then be registered.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 19.3.2-ce.0, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |


### Data Directory


- `gitlab_config` → `/etc/gitlab`
- `gitlab_logs` → `/var/log/gitlab`
- `gitlab_data` → `/var/opt/gitlab`
- `gitlab_runner` → `/etc/gitlab-runner`
- `/var/run/docker.sock` → `/var/run/docker.sock`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `W9_LOGIN_PASSWORD` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


Configuration is overridden by mounting `./src/runner-config.toml` to `/seed/config.toml`.


## References

- [Gitlab Administrator Guide](https://support.websoft9.com/docs/gitlab) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/gitlab/gitlab-ce)

- [Official docs](https://docs.gitlab.com/install/docker/installation/)

- [Official docs](https://docs.gitlab.com/update/upgrade_paths/)

- [Official docs](https://docs.gitlab.com/update/versions/gitlab_19_changes/)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs` and wait for the Omnibus initialization to finish; GitLab can take several minutes on first boot, and the web port can briefly return `502` before Rails is fully ready.

**Git clone URLs show the wrong host or port?**
- Make sure `W9_URL` matches the actual browser entry address and `W9_SSH_PORT_SET` matches the published host SSH port before first startup.

**Forgot the root password?**
- Reset it from inside the container with `gitlab-rake "gitlab:password:reset[root]"`; changing `W9_LOGIN_PASSWORD` in `.env` does not reset an existing installation.
<!-- W9_TROUBLESHOOT_END -->
