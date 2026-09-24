# SQL Server on Docker  

This is an **[Docker Compose template](https://github.com/Websoft9/docker-library)** powered by [Websoft9](https://www.websoft9.com) based on Docker for SQL Server:


 - community: 2025, 2022


## System Requirements

The following are the minimal recommended requirements for SQL Server containers:

* **RAM**: 4 GB or more
* **CPU**: 2 cores or higher
* **Disk**: at least 2 GB of free space
* **bandwidth**: more fluent experience over 100M  

## Install

You can install this SQL Server by [How to use it?](https://github.com/Websoft9/docker-library#how-to-use-it).   

If you want use SQL Server with **Websoft9 Business Support** free, you can [subscribe SQL Server](https://www.websoft9.com/apps) on Cloud platform

## Change Password

`MSSQL_SA_PASSWORD` is only applied when SQL Server initializes a new data directory. If you deploy with an existing `mssql_data` volume, changing `W9_LOGIN_PASSWORD` in `.env` does not rotate the `sa` password inside SQL Server.

To rotate the password on a running container, execute:

```bash
docker exec -it sqlserver /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P '<current-password>' \
  -Q "ALTER LOGIN sa WITH PASSWORD='<new-password>'"
```

## Documentation

[SQL Server Administrator Guide](https://support.websoft9.com/docs/sqlserver) powered by Websoft9
