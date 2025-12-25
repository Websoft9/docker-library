# Apache Traffic Server on Docker  

This is an **[Docker Compose template](https://github.com/Websoft9/docker-library)** powered by [Websoft9](https://www.websoft9.com) based on Docker for Apache Traffic Server.

Apache Traffic Server is a high-performance HTTP proxy cache server that can be used as a reverse proxy, forward proxy, or cache server.

## Supported Versions

 - community: latest

## System Requirements

The following are the minimal [recommended requirements](https://trafficserver.apache.org):

* **RAM**: 4 GB or more
* **CPU**: 2 cores or higher
* **Disk**: at least 10 GB of free space
* **bandwidth**: more fluent experience over 100M  

## Install

You can install this Apache Traffic Server by [How to use it?](https://github.com/Websoft9/docker-library#how-to-use-it).   

If you want use Apache Traffic Server with **Websoft9 Business Support** free, you can [subscribe Apache Traffic Server](https://www.websoft9.com/apps) on Cloud platform

## Quick Start

1. After installation, access the web interface:
   - HTTP: `http://your-server-ip:8080`
   - HTTPS: `https://your-server-ip:8443`
   - Management: `http://your-server-ip:8088`

2. Configure reverse proxy by editing the `remap.config` file in the `src` directory
3. Restart the container to apply configuration changes

## Configuration

### Basic Configuration
- Edit `src/records.config` for server settings
- Edit `src/remap.config` for URL remapping rules

### Environment Variables
- `W9_HTTP_PORT_SET`: HTTP port (default: 8080)
- `W9_HTTPS_PORT_SET`: HTTPS port (default: 8443)
- `W9_POWER_PASSWORD`: Admin password

## Documentation

[Apache Traffic Server Administrator Guide](https://support.websoft9.com/docs/trafficserver) powered by Websoft9