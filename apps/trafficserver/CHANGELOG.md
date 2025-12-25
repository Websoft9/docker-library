# CHANGELOG

## 2025-12-25
### Initial Release
- Complete docker-compose orchestration for Apache Traffic Server
- Basic reverse proxy configuration with records.config and remap.config
- Health checks and proper resource limits
- Persistent volumes for configuration, logs, and cache
- Management interface on port 8088
- Support for both HTTP (8080) and HTTPS (8443) protocols
- Comprehensive documentation and troubleshooting guide

### Configuration
- Default cache: 10GB disk, 256MB RAM
- Resource limits: 4GB memory, 2 CPU cores
- Reverse proxy mode enabled by default
- Logging enabled with rotation

