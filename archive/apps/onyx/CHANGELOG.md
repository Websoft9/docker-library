# CHANGELOG

## Release v2.0.0 (2026-01-14)

### Major Updates

- Upgraded to latest Onyx docker-compose configuration (prod-no-letsencrypt)
- Updated from Danswer to Onyx branding and architecture
- Added MinIO service for object storage (S3-compatible)
- Added Code Interpreter service (beta feature)
- Updated PostgreSQL max_connections from 150 to 250
- Updated shared memory size to 1GB for better performance
- Fixed Vespa container naming to use dynamic container name
- Updated Nginx image from 1.23.4 to 1.25.5-alpine
- Upgraded Vespa image to specific version 8.609.39
- Updated inference_model_server to use onyxdotapp/onyx-model-server
- Changed model cache paths from /root/.cache to /app/.cache
- Added persistent log volumes for all services
- Changed restart policy from 'always' to 'unless-stopped'

### New Features

- MinIO integration for file storage with automatic bucket creation
- Code interpreter support with docker-out-of-docker execution
- Enhanced environment variable configuration
- Support for lightweight background worker mode
- Improved S3/MinIO configuration options
- Added health checks for MinIO service

### Environment Variables

- Changed AUTH_TYPE default from 'basic' to 'google_oauth'
- Updated POSTGRES_USER from 'danswer' to 'postgres'
- Added MinIO configuration variables
- Added Code Interpreter configuration
- Added model server configuration options
- Added nginx proxy timeout settings
- Removed deprecated Danswer-specific variables

### Breaking Changes

- Service names updated to use service discovery instead of container names
- POSTGRES_HOST changed from container-specific to 'relational_db'
- VESPA_HOST changed from dynamic naming to 'index'
- REDIS_HOST changed from container-specific to 'cache'
- MODEL_SERVER_HOST now uses service name instead of container name
- Requires MinIO configuration for file storage

### Configuration Updates

- Updated .env template with new Onyx-specific variables
- Added comprehensive MinIO S3 configuration
- Added code interpreter beta settings
- Enhanced authentication options
- Updated documentation references from Danswer to Onyx

