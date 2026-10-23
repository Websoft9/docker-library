# i18n

`translation.json` holds translatable env labels. Translatable keys are
`W9_*_SET` and `W9_LOGIN*`. Values are `["English label", "中文标签"]`.

## Commands

```bash
make i18n-check                    # check all apps; fails only on missing keys
make i18n-check ARGS="--strict"    # also fail when a used key has an empty translation
make i18n-check ARGS="--app drupal"
make i18n-check ARGS="--warn-only" # report missing/untranslated keys, exit 0
make i18n-update                   # add missing keys as ["", ""]
make i18n-update ARGS="--app drupal"
```

The PR check uses the same entrypoint, restricted to keys added by the PR. It
is warning-only and never blocks a PR:

```bash
make i18n-check ARGS="--base <base-sha> --head <head-sha> --github-annotations --warn-only"
```

`i18n/manage.py` is the single implementation. `create.py` is kept as a thin
`--update` wrapper for older local scripts.

## Rules for AI

- Register new translatable keys in the same PR that adds them.
- New keys may stay `["", ""]`; do not author final translations.
- Use `--strict` when you want to audit translation completeness.
