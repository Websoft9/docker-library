# Jenkins on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Jenkins**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Jenkins admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Jenkins Docker image](https://hub.docker.com/r/jenkins/jenkins) and makes some improvements below.

<!-- W9_NOTE_START -->
Jenkins generates a one-time initial admin password at first startup. The value is stored in `/var/jenkins_home/secrets/initialAdminPassword` inside the container.

Appstore consumers that support `variables.json.credentials.password` can resolve and display this value automatically. If your consumer does not support that metadata yet, read the file manually from the Jenkins container.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 2.581, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 8080 |


### Data Directory


Data is persisted in the `jenkins` volume, mounted at `/var/jenkins_home`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Jenkins Administrator Guide](https://support.websoft9.com/docs/jenkins) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/jenkins/jenkins)

- [Releases](https://www.jenkins.io/changelog/)

- [GitHub docs](https://github.com/jenkinsci/docker)

- [Official docs](https://www.jenkins.io/doc/)

- [Official docs](https://www.jenkins.io/doc/book/installing/docker/)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
