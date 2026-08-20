# Facts To Collect

Repository facts:

- current `W9_VERSION`
- current upstream source from `version_from`
- current compose image references
- current database and runtime requirements
- current cadence and update policy

Upstream facts:

- latest stable release
- latest patch in the current tracked branch
- security fix notes
- upgrade notes or compatibility notes

Database facts (when the app depends on a database):

- current `W9_DB_VERSION` from `libs drift` dependency images
- app's verified DB min requirement from `variables.json` externalDB
- engine lifecycle tracks and EOL from `metadata/db-lifecycle.json`
- vendor-tested DB upper bound from release notes or official docs (prose, AI-only)

Assessment focus:

- whether the repo already floats on `x.x`
- whether a patch release requires any repo change at all
- whether a major update should stop at `review-first`
- whether the current DB version is EOL'd or below the best LTS candidate
