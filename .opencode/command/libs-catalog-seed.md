---
description: Create or update one app's repo catalog commercial data file and preview its Contentful push
agent: build
argument-hint: [app name]
---

Use the `catalog-seed` skill to create or update the repo catalog commercial data for one app.

Usage: /libs-catalog-seed <app name>

If the task input is `help` or empty, echo the usage line, then ask the user for the app name.

If the task input is present, treat it as the workflow input.

The skill writes `metadata/catalog/<app>.json` (trademark, summary, overview, description, websiteurl, screenshots, catalogBindings), validates against `metadata/catalog.schema.json` and `metadata/catalog-taxonomy.json`, and previews with `libs catalog-push --app <app> --json`. It never applies writes to Contentful.

$ARGUMENTS
