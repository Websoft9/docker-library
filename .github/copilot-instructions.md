# Docker Compose Library

This repository contains 300+ Docker Compose examples for applications like WordPress, MySQL, Odoo, MongoDB, GitLab, and many others. Each application is a standalone, runnable Docker Compose project that can be deployed with `docker compose up`.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## 🎯 Core Configuration Rules (READ FIRST)

### Rule 1: Conditional Login Credentials (.env)
**W9_LOGIN_USER and W9_LOGIN_PASSWORD**
- ✅ **INCLUDE** only when the application has built-in administrator credentials that can be pre-configured via container environment variables
  - Key indicator: The application's official Docker image provides environment variables for setting initial admin credentials
- ❌ **EXCLUDE** when:
  - No built-in authentication (nginx, Apache, static sites)
  - Token/API key only authentication
  - No user management system

### Rule 2: Conditional URL Replacement (.env)
**W9_URL and W9_URL_REPLACE**
- **W9_URL**: Always keep this variable as `W9_URL=internet_ip:$W9_HTTP_PORT_SET` (standard pattern)
  - This provides a placeholder for the application's external URL
  - Will be replaced by actual IP/domain during deployment
  
- **W9_URL_REPLACE**: ✅ **INCLUDE** `W9_URL_REPLACE=true` ONLY when:
  - `W9_URL` is actually referenced/used in docker-compose.yml or application environment variables
  - Application needs external URL for proper operation (callbacks, webhooks, email links, trusted domains)
  - Examples: 
    - Nextcloud: `NEXTCLOUD_TRUSTED_DOMAINS=$W9_URL`
    - GitLab: `GITLAB_OMNIBUS_CONFIG` with `external_url`
    - Joomla: `JOOMLA_SITE_URL=$W9_URL`
    
- **W9_URL_REPLACE**: ❌ **EXCLUDE** when:
  - `W9_URL` variable exists but is NOT referenced anywhere in docker-compose.yml
  - Application doesn't use external URL in its configuration
  - The variable is defined "just in case" but never actually consumed

### Rule 3: Volume Mappings Require src/ Files (docker-compose.yml)
**src/ Directory Requirements**
- ✅ **ALWAYS CREATE** matching files/folders in `src/` when docker-compose.yml maps configuration files
  - If volumes contains: `./src/nginx.conf:/etc/nginx/nginx.conf`
  - Then MUST create: `apps/appname/src/nginx.conf`
- ✅ **INCLUDE** sensible defaults that work out-of-the-box
- ✅ **DOCUMENT** configuration files in `src/README.md`
- ❌ **NEVER** reference non-existent files in volume mappings

**Quick Validation Before Committing:**
```bash
# Check 1: Does app have user authentication? If NO, remove W9_LOGIN_*
grep -q "W9_LOGIN_USER" apps/myapp/.env && echo "Has login - verify if needed"

# Check 2: Is W9_URL actually used in config? If NO, remove W9_URL_REPLACE
grep "\$W9_URL" apps/myapp/docker-compose.yml || echo "W9_URL not used - remove W9_URL_REPLACE (keep W9_URL)"

# Check 3: Do all volume-mapped files exist?
for vol in $(grep "./src/" apps/myapp/docker-compose.yml | cut -d: -f1 | tr -d ' -'); do
  [ -f "apps/myapp/$vol" ] || echo "Missing: $vol"
done
```

## Working Effectively

### Prerequisites and Setup
- Install Docker and Docker Compose v2:
  ```bash
  curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh && sudo systemctl enable docker && sudo systemctl start docker
  ```
- Install Python dependencies:
  ```bash
  pip3 install jinja2-cli python-dotenv requests
  ```
- Create the required Docker network (CRITICAL - required for all apps):
  ```bash
  docker network create websoft9
  ```

### Build and Test Process
- Build README files for all apps (takes 2-3 minutes for 300+ apps):
  ```bash
  python3 build/update_readme.py "$(ls -d apps/*/ | cut -f2 -d'/' | tr '\n' ',' | sed 's/,$//')"
  ```
- Build README for specific app (completes in <1 second):
  ```bash
  python3 build/update_readme.py "wordpress"
  ```
- Test specific applications:
  ```bash
  cd apps/nginx && docker compose up -d
  ```

### Application Deployment and Testing
- Deploy any application (example with nginx - takes ~5 seconds):
  ```bash
  cd apps/nginx
  docker compose up -d
  # Wait 10 seconds for startup
  curl http://localhost:9001
  docker compose down -v
  ```
- Deploy complex application with database (example with WordPress - takes ~15 seconds):
  ```bash
  cd apps/wordpress  
  docker compose up -d
  # Wait 30 seconds for database initialization
  curl -I http://localhost:9001  # Should return 302 redirect to installation
  docker compose down -v
  ```

## Validation

### Application Testing Requirements
- ALWAYS test applications after making changes by deploying them
- Simple apps (nginx, apache): Wait 10 seconds after startup before testing
- Complex apps with databases (WordPress, Drupal): Wait 30 seconds after startup before testing
- Apps should respond with HTTP 200 or appropriate redirects on their configured port
- Test connectivity: `curl http://localhost:$W9_HTTP_PORT_SET`
- ALWAYS clean up after testing: `docker compose down -v`

### Timing Expectations
- Simple containerized apps: 3-8 seconds startup time (nginx: ~0.3 seconds without image pull)
- Apps with databases: 10-20 seconds startup time (WordPress: ~0.5 seconds without image pull)
- Image pulls (first time): Add 5-15 seconds for most applications 
- Database initialization: Allow 30 seconds for complex apps like WordPress
- NEVER CANCEL: Allow full startup time. Set timeouts to 300+ seconds for initial deployments
- For debugging, containers may start faster on subsequent runs since images are cached

### Manual Validation Scenarios
- Test the complete deployment workflow: network creation → app deployment → connectivity test → cleanup
- Verify environment variable substitution works correctly
- Test that applications respond appropriately on their configured ports
- Validate database connectivity for multi-container applications

## Common Tasks

### Repository Structure
```
apps/                   # 300+ application directories
├── wordpress/         # Each app has these files:
│   ├── .env          # Environment variables
│   ├── docker-compose.yml  # Main deployment file
│   ├── README.md     # Generated from template
│   ├── variables.json # Template variables
│   └── src/          # Custom configuration files
build/                 # Python build scripts
template/             # Jinja2 templates for generated files
.github/workflows/    # CI/CD automation
```

#### CRITICAL: src/ Directory and Volume Mappings

**When to Create Files in src/**
- **ALWAYS** create matching files/folders in `src/` when docker-compose.yml references configuration files in volumes
- The `src/` directory contains custom configuration files that get mounted into containers
- Common examples:
  - `src/nginx.conf` → mapped to `/etc/nginx/nginx.conf`
  - `src/php.ini` → mapped to `/usr/local/etc/php/conf.d/php.ini`
  - `src/config.yaml` → mapped to `/app/config.yaml`
  - `src/templates/` → mapped to `/app/templates/`

**Volume Mapping Requirements**
- If docker-compose.yml has: `./src/myconfig.conf:/etc/app/myconfig.conf`
- Then you MUST create: `apps/appname/src/myconfig.conf`
- The file should contain appropriate default configuration
- Document any required customization in Notes.md

**Examples of Required src/ Files**
```yaml
# If docker-compose.yml contains:
volumes:
  - ./src/nginx.conf:/etc/nginx/nginx.conf
  - ./src/php.ini:/usr/local/etc/php/conf.d/php.ini
  - ./src/settings.json:/app/config/settings.json

# Then you MUST create:
apps/appname/src/nginx.conf
apps/appname/src/php.ini
apps/appname/src/settings.json
```

**src/ Directory Best Practices**
- Include a `src/README.md` explaining the purpose of each configuration file
- Provide sensible defaults that work out-of-the-box
- Comment configuration files to guide users
- Test that the application starts successfully with the provided config files

### Environment Variables Pattern
All applications use standardized environment variables:
- `W9_HTTP_PORT_SET`: External port mapping (default: 9001)
- `W9_POWER_PASSWORD`: Default password for all services
- `W9_ID`: Application instance identifier  
- `W9_NETWORK`: Docker network name (always: websoft9)
- `W9_URL`: External URL for application (always included as `internet_ip:$W9_HTTP_PORT_SET`)

#### IMPORTANT: Conditional Environment Variables

**Login Credentials (W9_LOGIN_USER and W9_LOGIN_PASSWORD)**
- **ONLY** include `W9_LOGIN_USER=admin` and `W9_LOGIN_PASSWORD=$W9_POWER_PASSWORD` when:
  - The application has explicit built-in authentication with username/password
  - The application requires initial admin credentials during setup
  - Examples: WordPress, GitLab, Odoo, Joomla, Drupal, Coze Studio
- **DO NOT** include these variables for:
  - Applications without built-in authentication (nginx, Apache, static sites)
  - Database-only services (MySQL, PostgreSQL, MongoDB)
  - Applications that use token/API key authentication only (HuggingChat)
  - Services that don't have user management

**URL Replacement Flag (W9_URL_REPLACE)**
- **W9_URL is ALWAYS included** in .env as: `W9_URL=internet_ip:$W9_HTTP_PORT_SET`
  - This provides a standard placeholder for external URL
  - Will be replaced with actual IP/domain during deployment
  
- **W9_URL_REPLACE=true is ONLY included when:**
  - The `W9_URL` variable is actually referenced/used in docker-compose.yml
  - Application passes W9_URL to container environment variables
  - Examples with W9_URL_REPLACE=true:
    - Nextcloud: `NEXTCLOUD_TRUSTED_DOMAINS=$W9_URL`
    - GitLab: `GITLAB_OMNIBUS_CONFIG` includes `external_url '$W9_URL'`
    - Joomla: `JOOMLA_SITE_URL=$W9_URL`
    
- **W9_URL_REPLACE is EXCLUDED when:**
  - W9_URL exists in .env but is NOT used in docker-compose.yml
  - Application doesn't reference external URL in configuration
  - Examples without W9_URL_REPLACE: HuggingChat, Coze Studio, basic containers

### Working with Applications
- Browse available apps: `ls apps/`
- Check app configuration: `cat apps/appname/.env`
- Validate app structure: `ls apps/appname/`
- Test app variables: `cd apps/appname && grep W9_ .env`

### Development Workflow
1. Always create the websoft9 network first: `docker network create websoft9`
2. Navigate to app directory: `cd apps/appname`
3. Review and modify .env if needed
4. Deploy: `docker compose up -d`
5. Wait appropriate startup time (10-30 seconds)
6. Test connectivity: `curl http://localhost:$W9_HTTP_PORT_SET`
7. Clean up: `docker compose down -v`

## Build System Details

### README Generation
- READMEs are generated from `template/README.jinja2` using variables from each app's `variables.json`
- NEVER edit README.md files manually - they will be overwritten
- To update README content, edit the template or variables.json file
- Regenerate after changes: `python3 build/update_readme.py "appname"`

### Testing Infrastructure  
The repository includes automated testing but has some issues:
- Test script `build/test_apps.py` needs manual fixes for docker compose v2
- Tests verify HTTP connectivity on configured ports
- Apps must respond within 5 minutes to pass automated tests
- Manual testing is more reliable than the automated test script

### CI/CD Workflows
Key GitHub Actions workflows:
- `build_files.yml`: Regenerates READMEs when templates change
- `pull_quest_test.yml`: Tests changed applications in PRs (currently disabled)
- Various other workflows for version management and syncing

## Common Gotchas

### Configuration Validation Checklist

Before finalizing any application configuration, verify:

**✅ .env File Validation**
- [ ] `W9_LOGIN_USER` and `W9_LOGIN_PASSWORD` are ONLY included if the app has built-in user authentication
- [ ] `W9_URL_REPLACE=true` is ONLY included if `W9_URL` is actually used in docker-compose.yml or app config
- [ ] All required passwords use `$W9_POWER_PASSWORD` for consistency
- [ ] Port settings (`W9_HTTP_PORT_SET`) don't conflict with common ports

**✅ docker-compose.yml Validation**
- [ ] All volume mappings to `./src/*` have corresponding files created in the `src/` directory
- [ ] Container names use `$W9_ID` or `$W9_ID-servicename` pattern
- [ ] All services use `restart: unless-stopped`
- [ ] Network configuration includes `external: true` for websoft9 network
- [ ] Health checks are configured for critical services (databases, etc.)

**✅ src/ Directory Validation**
- [ ] All configuration files referenced in volumes exist
- [ ] Configuration files have sensible defaults
- [ ] A `src/README.md` explains the purpose of each file
- [ ] Files are properly commented for user guidance

### Docker Compose Version
- This repository requires Docker Compose v2 (`docker compose` not `docker-compose`)
- Many scripts reference the old `docker-compose` command and may need manual correction
- Always use: `docker compose up -d` and `docker compose down -v`

### Network Requirements
- The `websoft9` network MUST exist before running any application
- All applications are configured to use this external network
- If network doesn't exist, applications will fail to start

### Port Conflicts
- Default port is 9001 for most applications
- Change `W9_HTTP_PORT_SET` in .env to avoid conflicts
- Check running containers: `docker ps` to see port usage

### Application Dependencies
- Some applications require external databases or services
- Multi-container apps (like WordPress) need time for database initialization
- Always check `docker compose ps` to verify all containers are running

## Key Files Reference

### Frequently Used Commands Output
```bash
# Repository root structure
ls -la
.github/          # GitHub workflows and issues
CONTRIBUTING.md   # Development guidelines  
README.md         # Main project documentation
apps/            # All application directories
build/           # Build and test scripts
template/        # File generation templates

# Example app structure (WordPress)
ls apps/wordpress/
.env                 # Environment configuration
CHANGELOG.md         # Version history
Notes.md            # Development notes
README.md           # Generated documentation
docker-compose.yml   # Main deployment file
src/                # Custom configuration files
variables.json      # Template variables
```

### Environment File Example
```bash
cat apps/wordpress/.env
W9_REPO=wordpress
W9_VERSION=6.8
W9_HTTP_PORT_SET=9001
W9_POWER_PASSWORD=secure_password_here
W9_ID=wordpress
W9_NETWORK=websoft9
WORDPRESS_DB_HOST=wordpress-mariadb
WORDPRESS_DB_PASSWORD=$W9_POWER_PASSWORD
```

Follow these instructions precisely to work effectively with this Docker Compose library. The key to success is understanding the standardized patterns and always following the proper setup, testing, and cleanup procedures.

## Quick Reference - Most Common Tasks

### Test Any Application
```bash
# Setup (one time)
docker network create websoft9

# Deploy and test (example: nginx)
cd apps/nginx
docker compose up -d
sleep 10  # Wait for startup
curl http://localhost:9001  # Test connectivity
docker compose down -v  # Clean up
```

### Add New Application  
```bash
# 1. Create app directory structure
mkdir apps/newapp
cp template/.env apps/newapp/
cp template/docker-compose.yml apps/newapp/
cp template/variables.json apps/newapp/

# 2. Edit configuration files following these rules:
# .env file:
#   - Set W9_REPO and W9_VERSION to correct image
#   - ONLY add W9_LOGIN_USER/PASSWORD if app has built-in auth
#   - ONLY add W9_URL_REPLACE=true if W9_URL is actually used
#   - Add app-specific environment variables below the separator line

# docker-compose.yml:
#   - Configure services with appropriate images
#   - Use $W9_ID for container names
#   - Add volume mappings for configuration files
#   - Ensure network: websoft9 is external

# 3. Create src/ files for any volume mappings
mkdir -p apps/newapp/src
# Create each file referenced in docker-compose.yml volumes
# Example: if volumes has ./src/config.ini:/app/config.ini
# Then create: apps/newapp/src/config.ini

# 4. Update variables.json with app metadata
# 5. Test deployment
cd apps/newapp && docker compose up -d
# Wait appropriate time, test connectivity, check logs
docker compose logs
curl http://localhost:9001
docker compose down -v

# 6. Validate configuration
# - Check .env for unnecessary variables
# - Verify all src/ files exist
# - Confirm app authentication requirements

# 7. Generate README
cd ../..
python3 build/update_readme.py "newapp"
```

### Update Documentation
```bash
# Edit variables.json (not README.md directly)
nano apps/appname/variables.json
# Regenerate README
python3 build/update_readme.py "appname"
```