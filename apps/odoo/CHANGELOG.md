# CHANGELOG

## 2026-09-11
- Reduced the supported Odoo versions to `17.0`, `18.0`, and `19.0`.
- Removed the obsolete app-local ARM image files now that the package uses the official multi-arch `odoo` image directly.
- Preserved the external PostgreSQL installation override and normalized `.env`, `.env.external-db`, and `docker-compose.yml` to current repository policy rules.
- Regenerated the README.
