# Prompt Fragments

## Exists Check Rule

Before anything else, load the CLI venv (`make install` if `.venv/` missing) and run `make --no-print-directory libs ARGS="list --include-archived --json"` (one-shot equivalent of `make cli` + `libs list`). If `<app>` is in the full list (active, archived, or internal), stop and report its key attributes (status, scope, cadence, update_policy), then ask the user to re-input a different name or terminate; existing apps go through the app-update skill.

## Template Rule

Start from repository conventions and only add the minimum app-specific fields required by upstream.

## Validation Rule

Prove the app can be deployed, not just generated.
