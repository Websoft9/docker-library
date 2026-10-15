# CHANGELOG

## 2026-10-13

- Confirmed the Drupal package stays on the stable `11.4-apache` image line while upstream Drupal 11 latest stable is `11.4.9`.
- Fixed version metadata drift so `variables.json` matches the shipped image tag and generated documentation.

## 2026-09-30

- Updated Drupal from `11.2.2-apache` to `11.4-apache`.
- Normalized `.env` and `docker-compose.yml` to current repository policy.
- Added app-specific validation coverage for the installer path.
