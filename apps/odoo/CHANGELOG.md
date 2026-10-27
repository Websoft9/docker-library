# CHANGELOG

## 2026-10-27
- Updated the default Odoo image to 20.0 while retaining the supported older versions.
- Updated the bundled PostgreSQL version to 16, the minimum supported by Odoo 20.
- Refreshed Odoo 20 release references and regenerated the README.

## 2026-09-11
- Reduced the supported Odoo versions to `17.0`, `18.0`, and `19.0`, and added `latest` back so users can test the newest release line.
- Removed the obsolete app-local ARM image files now that the package uses the official multi-arch `odoo` image directly.
- Removed the unused `src/extra-addons` placeholder; custom addons live in the `odoo_addons` volume mounted at `/mnt/extra-addons`.
- Enriched `upstream` with `releases` and official documentation sources.
- Preserved the external PostgreSQL installation override and normalized `.env`, `.env.external-db`, and `docker-compose.yml` to current repository policy rules.
- Regenerated the README.
