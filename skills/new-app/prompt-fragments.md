# Prompt Fragments

## Exists Check Rule

Before anything else, load the CLI venv (`make install` if `.venv/` missing) and run `make --no-print-directory libs ARGS="list --include-archived --json"`. If `<app>` is in the full list (active, archived, or internal), stop and report its key attributes (status, scope, cadence, update_policy), then ask the user to re-input a different name or terminate; existing apps go through the app-update or restore-app skill.

## Issue To Flags Rule

The issue is prose. AI reads it, extracts name, trademark, and official reference URLs, researches the image and version, then calls `libs app-new` with flags. The CLI never reads GitHub or an issue body; it only validates flags and scaffolds.

## Template Rule

The machine scaffold source is `metadata/templates/new-app/`. `template/` stays as a human reference only. Start from repository conventions and only add the minimum app-specific fields required by upstream.

## TODO Placeholder Rule

Omitted version/repo become explicit `TODO` placeholders in the generated files. Never pass fake values such as `latest` or the app name as the image repo.

## Validation Rule

Prove the app can be deployed, not just generated.
