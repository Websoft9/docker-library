# RethinkDB on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **RethinkDB**.
2. In the **Access** tab, get the login URL and credentials.

3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the web admin console from the **Access** tab. The console does not have its own login screen; it always connects as the `admin` user.
2. Use **Data Explorer** to run ReQL commands, for example `r.dbList()`.
3. Connect application drivers to the database port with user `admin` and the password from `W9_LOGIN_PASSWORD`.

### Change Password

1. In the console's **Data Explorer**, run `r.db('rethinkdb').table('users').get('admin').update({password: 'new-password'})`.
2. Update `W9_LOGIN_PASSWORD` (or `W9_POWER_PASSWORD`) in `.env` and save so a future re-initialization uses the same password.
3. Restarting an existing deployment does not reset the password; the seed only applies when the data directory is created.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [RethinkDB Docker image](https://hub.docker.com/_/rethinkdb) and makes some improvements below.

<!-- W9_NOTE_START -->
### Admin Console Security

The RethinkDB web admin console has no login of its own and runs with full admin rights. Restrict access to it with a reverse proxy access list or firewall rule; anyone who can reach port 8080 can manage the database.

### Client Connections

Connect drivers such as the Python or JavaScript client to the published database port. User `admin`, the password from `W9_LOGIN_PASSWORD`, and authentication are required. Passwords are sent in plaintext unless TLS is configured for the driver port.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 2.4, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web admin console | 8080 |
| Database driver | 28015 |


### Data Directory


Data is persisted in the `rethinkdb_data` volume, mounted at `/data`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `W9_LOGIN_PASSWORD` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [RethinkDB Administrator Guide](https://support.websoft9.com/docs/rethinkdb) by Websoft9

- [Docker Hub image](https://hub.docker.com/_/rethinkdb)

- [Releases](https://github.com/rethinkdb/rethinkdb/releases)

- [GitHub docs](https://github.com/docker-library/docs/blob/master/rethinkdb/README.md)

- [Official docs](https://rethinkdb.com/docs/)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
