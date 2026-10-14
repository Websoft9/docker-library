# CouchDB on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **CouchDB**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the CouchDB admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [CouchDB Docker image](https://hub.docker.com/_/couchdb) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 3.5, 3.4, 3.3, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console and API | 5984 |


### Data Directory


- `couchdb_data` → `/opt/couchdb/data`
- `couchdb_config` → `/opt/couchdb/etc/local.d`
- `couchdb_log` → `/opt/couchdb/var/log`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration is overridden by mounting `./src/my.ini` to `/opt/couchdb/etc/local.d/my.ini`.


## References

- [CouchDB Administrator Guide](https://support.websoft9.com/docs/couchdb) by Websoft9

- [Docker Hub image](https://hub.docker.com/_/couchdb)

- [Releases](https://github.com/apache/couchdb)

- [Official docs](https://docs.couchdb.org/en/stable/install/docker.html)

- [GitHub docs](https://github.com/apache/couchdb-docker)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
