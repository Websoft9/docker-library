# Catalog Authoring Checklist

- [ ] Confirm `apps/<app>/variables.json` exists
- [ ] Read `metadata/templates/catalog.json` and `metadata/catalog.schema.json`
- [ ] Read `metadata/catalog-taxonomy.json` when category bindings are needed
- [ ] Read `apps/<app>/variables.json` and upstream references
- [ ] Create or update `metadata/catalog/<app>.json`
- [ ] Keep `summary` to at most 8 words (prefer 5 or fewer)
- [ ] Keep `overview` to at most 30 words (prefer 20 or fewer)
- [ ] Keep `catalogBindings` valid against the taxonomy snapshot
- [ ] Preview with `.venv/bin/libs catalog-push --app <app> --json`
- [ ] Produce a short report
