# About

This folder includes files mount to container and used by Websoft9

## Configuration Files

- `records.config`: Traditional configuration file for Apache Traffic Server
- `records.yaml`: Modern YAML configuration file (preferred by newer versions)
- `remap.config`: URL remapping rules for reverse proxy configuration
- `hosting.config`: Origin server configuration

## Usage

1. Edit `remap.config` to configure your reverse proxy mappings
2. Modify `records.config` for performance and caching settings
3. Restart the container to apply changes

## Default Configuration

- HTTP Port: 8080
- HTTPS Port: 8443
- Management Port: 8088
- Cache Size: 10GB disk, 256MB RAM

Refer to [Apache Traffic Server Documentation](https://docs.trafficserver.apache.org/) for more configuration options.