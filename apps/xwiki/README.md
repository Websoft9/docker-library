# XWiki on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **XWiki**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the XWiki console; the first visit shows the **Distribution Wizard**.
2. Complete the wizard to create the wiki and the first administrator account.
3. After installation, sign in and start creating pages.

### Change Password

1. Sign in to XWiki and open your user profile.
2. Change your own password there, or use **Administration → Users** to reset other accounts.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [XWiki Docker image](https://hub.docker.com/_/xwiki) and makes some improvements below.

<!-- W9_NOTE_START -->
- The first visit runs the XWiki Distribution Wizard; it downloads the standard flavor, so the first install takes several minutes and needs outbound network access.
- `DB_USER` / `DB_PASSWORD` / `DB_DATABASE` / `DB_HOST` configure the bundled MySQL service `${W9_ID}-mysql`.
- XWiki data is persisted in the `xwiki` volume (`/usr/local/xwiki`).
- The administrator account is created interactively in the wizard and is not controlled by `.env`.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 18.7, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 8080 |


### Data Directory


- `xwiki` → `/usr/local/xwiki`
- `mysql` → `/var/lib/mysql`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration is overridden by mounting `./src/mysql_init.sql` to `/docker-entrypoint-initdb.d/init.sql`.


## References

- [XWiki Administrator Guide](https://support.websoft9.com/docs/xwiki) by Websoft9

- [Docker Hub image](https://hub.docker.com/_/xwiki)

- [Releases](https://github.com/xwiki/xwiki-platform/releases)

- [Official compose](https://raw.githubusercontent.com/xwiki/xwiki-docker/master/18/mysql-tomcat/docker-compose.yml)

- [Official env example](https://raw.githubusercontent.com/xwiki/xwiki-docker/master/18/mysql-tomcat/.env)

- [Official docs](https://www.xwiki.org/xwiki/bin/view/Documentation/AdminGuide/Installation/)

- [GitHub docs](https://github.com/xwiki/xwiki-docker)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**The first page keeps showing the Distribution Wizard?**
- Complete the wizard and let it download the standard flavor; it needs outbound network access.

**Container stays unhealthy?**
- XWiki can take a couple of minutes to start; check `docker compose logs ${W9_ID}`.

**Database connection error?**
- Confirm `${W9_ID}-mysql` is running and that `DB_USER` / `DB_PASSWORD` / `DB_DATABASE` match the MySQL service.
<!-- W9_TROUBLESHOOT_END -->
