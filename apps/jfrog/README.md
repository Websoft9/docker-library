# JFrog Artifactory on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **JFrog Artifactory**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the JFrog Platform URL from the **Access** tab. The first sign-in uses `admin` / `password`.
2. When prompted, set a new administrator password.
3. Create repositories and users from the Platform administration UI.

### Change Password

1. Sign in to the JFrog Platform with the administrator account.
2. Open the account menu → **Edit Profile → Change Password**, or reset it from **Administration → User Management**.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [JFrog Artifactory Docker image](releases-docker.jfrog.io/jfrog/artifactory-oss) and makes some improvements below.

<!-- W9_NOTE_START -->
- This package runs the official JFrog Artifactory OSS image and uses the bundled embedded Derby database, so no external database service is required. Artifactory OSS is open source and requires no license.
- The Platform web console listens on port `8082` inside the container and is published through `W9_HTTP_PORT_SET`.
- The first sign-in uses the built-in `admin` / `password`; Artifactory forces a new administrator password on first sign-in, so changing that default here does not change the running instance.
- Set the external base URL inside the UI (**Administration → General → JFrog URL / Base URL**) because the package does not configure it through environment variables.
- Artifactory can take several minutes to start on the first boot.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 7.161.26.


### Ports

| Purpose | Port |
| --- | --- |
| JFrog Platform web console | 8082 |


### Data Directory


Data is persisted in the `jfrog_data` volume, mounted at `/var/opt/jfrog/artifactory`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [JFrog Artifactory Administrator Guide](https://support.websoft9.com/docs/jfrog) by Websoft9

- [Docker Hub image](releases-docker.jfrog.io/jfrog/artifactory-oss)

- [Official docs](https://www.jfrogchina.com/docs/docker-install-artifactory-1)

- [GitHub docs](https://github.com/jfrog/artifactory-docker-examples)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App takes long to start?**
- Artifactory bootstraps its database and keys on first start; allow a few minutes and check `docker compose logs`.

**Login rejected?**
- Use the initial `admin` / `password`, or the password you set on first sign-in.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
