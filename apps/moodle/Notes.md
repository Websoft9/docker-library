## About

Moodle Docker deployment with MariaDB support.

## URL Configuration

### Changing from IP to Domain

When you need to change from IP access to domain access, you need to update both the config file and database:

1. **Update config.php** (in container `/var/www/html/config.php`):
```bash
docker exec -it moodle sed -i "s|http://.*';|http://your-domain.com';|g" /var/www/html/config.php
```

2. **Update database**:
```bash
docker exec -it moodle-mariadb mariadb -umoodle -p moodle -e "UPDATE mdl_config SET value = 'http://your-domain.com' WHERE name = 'wwwroot';"
```

3. **Clear Moodle cache**:
```bash
docker exec -it moodle php /var/www/html/admin/cli/purge_caches.php
```

### HTTPS Configuration with Reverse Proxy

If you encounter **infinite redirect loop** after configuring HTTPS certificate (via Nginx Proxy Manager), you need to configure Moodle to work behind a reverse proxy.

**Problem**: 
- config.php has `$CFG->wwwroot = 'http://domain.com';`
- User accesses via HTTPS
- Moodle detects protocol mismatch and redirects infinitely

**Solution**: Add reverse proxy configuration to `/var/www/html/config.php`:

```bash
# Enter the container
docker exec -it moodle bash

# Edit config.php and add these lines BEFORE require_once():
vi /var/www/html/config.php
```

Add the following configuration **BEFORE** the `require_once(__DIR__ . '/lib/setup.php');` line:

```php
// HTTPS Reverse Proxy Configuration
$CFG->wwwroot   = 'https://safeline.websoft9.cn';  // Change to HTTPS

// Force HTTPS when behind reverse proxy
if (isset($_SERVER['HTTP_X_FORWARDED_PROTO']) && $_SERVER['HTTP_X_FORWARDED_PROTO'] === 'https') {
    $_SERVER['HTTPS'] = 'on';
    $_SERVER['SERVER_PORT'] = 443;
}

// Alternative: Force HTTPS for all requests
// $CFG->reverseproxy = true;
// $_SERVER['HTTPS'] = 'on';
```

**Complete config.php example**:

```php
<?php  // Moodle configuration file

unset($CFG);
global $CFG;
$CFG = new stdClass();

$CFG->dbtype    = 'mariadb';
$CFG->dblibrary = 'native';
$CFG->dbhost    = 'moodle_edf5j-mariadb';
$CFG->dbname    = 'moodle';
$CFG->dbuser    = 'moodle';
$CFG->dbpass    = 'qB!5Glu37szh1bUd';
$CFG->prefix    = 'mdl_';
$CFG->dboptions = array(
    'dbpersist' => 0,
    'dbport' => '3306',
    'dbsocket' => '',
    'dbcollation' => 'utf8mb4_unicode_ci',
);

// IMPORTANT: Change to HTTPS
$CFG->wwwroot   = 'https://safeline.websoft9.cn';
$CFG->dataroot  = '/var/moodledata';
$CFG->admin     = 'admin';

$CFG->directorypermissions = 0777;

// HTTPS Reverse Proxy Support
if (isset($_SERVER['HTTP_X_FORWARDED_PROTO']) && $_SERVER['HTTP_X_FORWARDED_PROTO'] === 'https') {
    $_SERVER['HTTPS'] = 'on';
    $_SERVER['SERVER_PORT'] = 443;
}

require_once(__DIR__ . '/lib/setup.php');

// There is no php closing tag in this file,
// it is intentional because it prevents trailing whitespace problems!
```

**Quick Fix Command**:

```bash
# Method 1: Edit manually
docker exec -it moodle vi /var/www/html/config.php

# Method 2: Use sed to update URL to HTTPS
docker exec -it moodle sed -i "s|http://safeline.websoft9.cn|https://safeline.websoft9.cn|g" /var/www/html/config.php

# Then add reverse proxy config (manual edit required)
docker exec -it moodle vi /var/www/html/config.php
# Add the HTTP_X_FORWARDED_PROTO check before require_once()
```

**Update database** (also change to HTTPS):

```bash
docker exec -it moodle_edf5j-mariadb mariadb -umoodle -pqB\!5Glu37szh1bUd moodle -e "UPDATE mdl_config SET value = 'https://safeline.websoft9.cn' WHERE name = 'wwwroot';"
```

**Clear cache**:

```bash
docker exec -it moodle php /var/www/html/admin/cli/purge_caches.php
```

### Verify Nginx Proxy Manager Configuration

Ensure your Nginx Proxy Manager has these settings:

1. **SSL Certificate**: Valid and properly configured
2. **Force SSL**: Enabled
3. **Custom Nginx Configuration** (Advanced tab):

```nginx
# Ensure these headers are passed to backend
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header Host $host;
```

## Troubleshooting

### Issue: Infinite Redirect Loop
- **Cause**: Protocol mismatch between config.php (http) and actual access (https)
- **Solution**: Change `$CFG->wwwroot` to HTTPS and add reverse proxy support

### Issue: "Site not secure" warning
- **Cause**: Mixed content (HTTP resources on HTTPS page)
- **Solution**: Ensure `$CFG->wwwroot` uses HTTPS

### Issue: Session errors
- **Cause**: Cookie domain mismatch
- **Solution**: Clear browser cookies and cache after changing URL
