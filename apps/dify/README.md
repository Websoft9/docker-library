# Dify on Docker  

This is an **[Docker Compose template](https://github.com/Websoft9/docker-library)** powered by [Websoft9](https://www.websoft9.com) based on Docker for Dify:


 - community:  1.4.3, latest


## System Requirements

The following are the minimal [recommended requirements](https://dify.ai):

* **RAM**: 4 GB or more
* **CPU**: 2 cores or higher
* **Disk**: at least 8 GB of free space
* **bandwidth**: more fluent experience over 100M  

## Install

You can install this Dify by [How to use it?](https://github.com/Websoft9/docker-library#how-to-use-it).   

If you want use Dify with **Websoft9 Business Support** free, you can [subscribe Dify](https://www.websoft9.com/apps) on Cloud platform

## Database Information

This package does not offer external databases. Metadata describes the bundled PostgreSQL main and plugin databases, authenticated Redis, and Weaviate using existing configuration sources. PostgreSQL uses its default `postgres` account; vector-store API keys are not database passwords.

Declarations do not rewrite connection settings, migrate data, or rotate credentials. Existing native connection wiring and normalized references are preserved, as is the Redis environment isolation fix; initialization follows the original application values instead of being separated solely for external databases. Known metadata does not prove complete storage information or live credential validity.

## Documentation

[Dify Administrator Guide](https://support.websoft9.com/docs/dify) powered by Websoft9