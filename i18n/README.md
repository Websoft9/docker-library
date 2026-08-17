# i18n

`translation.json` holds translatable env labels for downstream repos.

Mechanism:
- Translatable keys: `W9_*_SET` and `W9_LOGIN*`
- `create.py` scans `apps/*/.env` and registers missing keys as `["", ""]`
- Values are filled by humans: `["English label", "中文标签"]`
- `.github/workflows/i18n.yml` pushes updates to the plugin repos by PR

Rules for AI:
- register new translatable keys
- do not author final translations
