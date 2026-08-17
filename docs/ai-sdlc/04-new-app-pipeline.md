# New App Pipeline

Trigger:
- owner opens a new app issue

Steps:
1. Issue provides official docs, image source, and deployment reference.
2. AI researches official install and compose patterns.
3. AI creates the app from the repository template.
4. AI fills `.env`, `docker-compose.yml`, `variables.json`, `README.md`, and `src/`.
5. AI registers any new translatable env key in `i18n/translation.json`.
6. AI runs automated validation.
7. AI publishes the test report.
8. Owner runs final E2E.
9. Owner decides merge and release.

After merge:
- assign a maintenance cadence
- assign an update policy
- ensure Contentful metadata is ready for publish

Rule:
- new app flow uses the same quality gates as update flow
