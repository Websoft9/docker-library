# Archive App Checklist

- [ ] Confirm archive scope and reason
- [ ] Move app from `apps/` to `archive/apps/`
- [ ] Update `metadata/maintenance.yaml` when active maintenance rules change
- [ ] Update `metadata/archive.yaml`
- [ ] Preview Contentful retirement flags: `make libs ARGS="contentful-update --app <app> --fields '{\"appStore\": false, \"production\": false}'"`
- [ ] Hand `contentful-update --apply` to the owner
- [ ] Produce a short archive report
