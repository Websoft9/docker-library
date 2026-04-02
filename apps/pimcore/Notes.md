# Pimcore

## Architecture

This stack uses 3 long-running containers + 1 initialization container:

- **nginx**: Web server (nginx:stable-alpine), handles HTTP requests and proxies PHP to the `php` service
- **php**: PHP-FPM + background workers (`pimcore/pimcore:php8.2-supervisord-latest`)
- **mariadb**: MariaDB 10.11 database
- **init**: One-time setup container (`pimcore/pimcore:php8.2-latest`) that runs on first startup to install Pimcore via Composer and configure the database

## First Startup

On first `docker compose up -d`, the `init` container will:
1. Run `composer create-project pimcore/skeleton` to download Pimcore
2. Run `vendor/bin/pimcore-install` to initialize the database and create the admin user

This step can take **5–15 minutes** depending on network speed. The `php` and `nginx` containers will return errors until initialization completes. Monitor progress with:

```bash
docker logs -f pimcore-init
```

## References

- Official image: https://hub.docker.com/r/pimcore/pimcore
- Docker setup docs: https://github.com/pimcore/docker
- Pimcore skeleton: https://github.com/pimcore/skeleton