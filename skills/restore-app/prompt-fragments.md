# Prompt Fragments

## Restore Rule

Restore only moves an archived app back to active maintenance; it does not release a new version. A stale version must go through the app-update skill first.

Inspect the restore preview's `database_metadata` and `todo`. Follow `docs/app-database-connection-spec.md` to migrate legacy database objects from verified sources before publishing, then run `libs app-check --app <app> --gate database-metadata`. Never infer a new declaration from legacy names alone.

## Routing Rule

If the app is active or missing instead of archived, do not restore. Route to `app-update` (active) or `new-app` (missing).

## Batch Rule

Batch restore is only valid when all apps share the same cadence and update policy.
