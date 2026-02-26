# Configuration Files

This directory is intentionally empty.

## Why No Configuration Files?

Langfuse is configured 100% through environment variables (defined in `.env` file). No configuration files need to be mounted into containers.

All application behavior, database connections, S3 storage settings, and authentication parameters are managed via environment variables, which simplifies deployment and updates.

## Configuration Management

To modify Langfuse configuration:
1. Edit the `.env` file in the parent directory
2. Restart the containers: `docker compose restart`

Refer to the official documentation for available environment variables:
https://langfuse.com/self-hosting/configuration
