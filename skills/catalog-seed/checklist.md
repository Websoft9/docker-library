# Catalog Authoring Checklist

- [ ] Confirm `apps/<app>/variables.json` exists
- [ ] Read `metadata/templates/catalog.json` and `metadata/catalog.schema.json`
- [ ] Read `metadata/catalog-taxonomy.json` when category bindings are needed
- [ ] Read `apps/<app>/variables.json` and upstream references
- [ ] Create or update `metadata/catalog/<app>.json`
- [ ] Keep `catalogBindings` valid against the taxonomy snapshot
- [ ] Preview with `libs catalog-push --app <app> --json`
- [ ] Produce a short report
