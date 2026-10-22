# CHANGELOG

## 2026-10-22

- Confirmed the Drupal package stays on the stable `11.4-apache` line, which resolves to upstream `11.4.11`.
- Updated the bundled database from MySQL `8.0` (EOL 2026-04-30) to the supported MySQL `8.4` LTS line.

## 2026-10-13

- Confirmed the Drupal package stays on the stable `11.4-apache` image line while upstream Drupal 11 latest stable is `11.4.9`.
- Fixed version metadata drift so `variables.json` matches the shipped image tag and generated documentation.

## 2026-09-30

- Updated Drupal from `11.2.2-apache` to `11.4-apache`.
- Normalized `.env` and `docker-compose.yml` to current repository policy.
- Added app-specific validation coverage for the installer path.
