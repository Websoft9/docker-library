# Configuration Files

This directory contains custom configuration files mounted into the Concrete CMS container.

## Files

| File | Mounted To | Purpose |
|------|-----------|---------|
| install.sh | /docker-entrypoint-init.d/install.sh | Automatic CLI installation script for Concrete CMS |
| php_extra.ini | /usr/local/etc/php/conf.d/php_extra.ini | PHP configuration tuning (memory, upload limits, OPcache) |

## Notes

### install.sh
- Waits for MySQL to be ready (max 30 attempts)
- Executes `c5:install` command with environment variables
- Sets proper file permissions for application/files and application/config
- Only runs if Concrete CMS is not already installed

### php_extra.ini
- Increases upload limit to 128MB (suitable for media-rich sites)
- Increases memory_limit to 256MB for complex operations
- Enables OPcache for better performance
- Adjust values based on your server capacity

## Making Changes

After modifying configuration files:
```bash
docker compose restart concrete
```

For install.sh modifications, you need to reinstall:
```bash
docker compose down -v
docker compose up -d
```

⚠️ **Warning**: `docker compose down -v` will delete all data!
