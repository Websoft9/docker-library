# SQL Server on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **SQL Server**.
2. In the **Access** tab, get the login URL and credentials.

3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the SQL Server admin console.
2. Try a core feature.

### Change Password

`MSSQL_SA_PASSWORD` is only applied when SQL Server initializes a new data directory. If you deploy with an existing `mssql_data` volume, changing `W9_LOGIN_PASSWORD` in `.env` does not rotate the `sa` password inside SQL Server.

To rotate the password on a running container, execute:

```bash
docker exec -it sqlserver /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P '<current-password>' \
  -Q "ALTER LOGIN sa WITH PASSWORD='<new-password>'"
```
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [SQL Server Docker image](https://mcr.microsoft.com/mssql/server) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 2025, 2022.


### Ports

| Purpose | Port |
| --- | --- |
| SQL Server | 1433 |


### Data Directory


Data is persisted in the `mssql_data` volume, mounted at `/var/opt/mssql`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `MSSQL_SA_PASSWORD` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [SQL Server Administrator Guide](https://support.websoft9.com/docs/sqlserver) by Websoft9

- [Docker Hub image](https://mcr.microsoft.com/mssql/server)

- [Official docs](https://learn.microsoft.com/en-us/sql/linux/install-upgrade/quickstart-install-docker?view=sql-server-ver17)

- [Official docs](https://learn.microsoft.com/en-us/sql/linux/quickstart-install-connect-docker?view=sql-server-ver16)

- [Official docs](https://mcr.microsoft.com/product/mssql/server/tags)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
