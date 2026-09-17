# src/ — Custom Configuration Files

This directory contains configuration files that are bind-mounted into the Moodle container.

## Files

### php.ini

Mounted to: `/usr/local/etc/php/conf.d/zz-websoft9.ini`

The image already ships `/usr/local/etc/php/conf.d/zz-moodle.ini`. Because PHP
loads `conf.d` files in alphabetical order, `zz-websoft9.ini` is applied last and
overrides the image defaults.

Current values:

| Setting | Value | Purpose |
|---|---|---|
| `memory_limit` | 512M | Moodle minimum is 256M; 512M recommended |
| `upload_max_filesize` | 512M | Allows large file uploads in courses |
| `post_max_size` | 512M | Must be ≥ `upload_max_filesize` |
| `max_execution_time` | 600 | Prevents timeouts during upgrades/cron |
| `max_input_vars` | 5000 | Required for forms with many items |
| `max_input_time` | 600 | Time limit for parsing input data |

**To apply changes:** edit `php.ini` and run `docker compose restart moodle`.

## Where PHP configuration lives in this image

- PHP scan dir: `/usr/local/etc/php/conf.d/`
- Moodle defaults: `/usr/local/etc/php/conf.d/zz-moodle.ini`
- Environment overrides: `/usr/local/etc/php/conf.d/20-local.ini` (generated)

There are three supported ways to add custom PHP parameters:

1. **Edit `src/php.ini`** (this file) — the recommended way for a readable set of
   values. It is mounted to `zz-websoft9.ini`.
2. **Environment variables** named `PHP_INI-<name>=<value>`, for example
   `PHP_INI-memory_limit=1024M`. The image writes them to
   `/usr/local/etc/php/conf.d/20-local.ini` on start. Note the hyphen in
   `PHP_INI-`, not an underscore.
3. **Any `*.ini` file mounted into `/docker-entrypoint.d/`** — the image's
   entrypoint copies it into `/usr/local/etc/php/conf.d/` at start.

You can also enable extra PHP extensions with `PHP_EXTENSION_<name>=1` when the
extension is already installed in the image.

**Reference:** https://docs.moodle.org/en/PHP_settings
