# src/ — Custom Configuration Files

This directory contains configuration files that are bind-mounted into the Moodle container at startup.

## Files

### php.ini

Mounted to: `/usr/local/etc/php/conf.d/moodle.ini`

Overrides PHP defaults with Moodle-recommended values:

| Setting | Value | Purpose |
|---|---|---|
| `memory_limit` | 512M | Moodle minimum is 256M; 512M recommended |
| `upload_max_filesize` | 512M | Allows large file uploads in courses |
| `post_max_size` | 512M | Must be ≥ `upload_max_filesize` |
| `max_execution_time` | 600 | Prevents timeouts during upgrades/cron |
| `max_input_vars` | 5000 | Required for forms with many items |
| `max_input_time` | 600 | Time limit for parsing input data |

**To apply changes:** Edit `php.ini` and run `docker compose restart moodle`.

**Reference:** https://docs.moodle.org/en/PHP_settings
