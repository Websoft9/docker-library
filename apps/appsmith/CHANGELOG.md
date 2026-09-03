# CHANGELOG

## 2026-09-03
- Upgraded Appsmith to v2.3.
- Added the image environment variables reference section in `.env` pointing to the official `.env.example`, with commented examples for external MongoDB/Redis connection strings and custom domain.
- Added the official compose and env example URLs to `variables.json` upstream (`compose.compose`, `compose.env`), enabling upstream drift reporting.
- Clarified in Notes.md that Appsmith has no ROOT_URL and that public access is set via APPSMITH_CUSTOM_DOMAIN / Admin Settings.
- Regenerated the README via the app generator.
