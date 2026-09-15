# Jihu GitLab on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Jihu GitLab**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Sign in at `/users/sign_in` as `root` with the initial root password.
2. Create a project and push a test commit to confirm Git access.
3. If you clone over SSH, use the Git SSH clone URL on port `${W9_SSH_PORT_SET}`.

### Change Password

1. Sign in to JiHu GitLab and change the password from the user profile.
2. If you cannot sign in, reset it inside the container with `gitlab-rake "gitlab:password:reset[root]"`.
3. `W9_LOGIN_PASSWORD` is the initial root password and only applies on first startup; changing `.env` does not change an existing password.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Jihu GitLab Docker image](https://registry.gitlab.cn/omnibus/gitlab-jh) and makes some improvements below.

<!-- W9_NOTE_START -->
The package sets GitLab `external_url` to `http://${W9_URL}` and the SSH clone port to `${W9_SSH_PORT_SET}`, so clone URLs match the published ports. `W9_LOGIN_PASSWORD` seeds the initial root password on first startup only.

The omnibus container bundles PostgreSQL, Redis, Gitaly, and other services; only the web port and the Git SSH port are published. The package does not ship a JiHu license; upload a valid license from the GitLab admin area when enterprise features are required.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 19.3.2, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 80 |
| Git SSH | 22 |


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


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Jihu GitLab Administrator Guide](https://support.websoft9.com/docs/jihu) by Websoft9

- [Docker Hub image](https://registry.gitlab.cn/omnibus/gitlab-jh)

- [Official docs](https://docs.gitlab.cn/jh/install/docker.html)

- [Official docs](https://gitlab.cn/)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
