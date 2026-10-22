# Archive App Checklist

- [ ] Confirm whether this is archive or permanent delete
- [ ] For permanent delete, follow the Permanent delete section and skip the move/Contentful archive steps
- [ ] Confirm archive scope and reason
- [ ] Move app from `apps/` to `archive/apps/`
- [ ] Update `metadata/maintenance.yaml` when active maintenance rules change
- [ ] Update `metadata/archive.yaml`
- [ ] Preview Contentful retirement flags: `.venv/bin/libs catalog-update --app <app> --fields '{"appStore": false, "production": false}'`
- [ ] Include the exact `catalog-update --apply` command for the owner in the report
- [ ] Produce a short archive report
