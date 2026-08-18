# Prompt Fragments

## Restore Rule

Restore only moves an archived app back to active maintenance; it does not release a new version. A stale version must go through the app-update skill first.

## Routing Rule

If the app is active or missing instead of archived, do not restore. Route to `app-update` (active) or `new-app` (missing).

## Batch Rule

Batch restore is only valid when all apps share the same cadence and update policy.
