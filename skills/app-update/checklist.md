# App Update Checklist

- [ ] Confirm the update is approved for implementation
- [ ] Read app-local files under `apps/<app>/`
- [ ] Read upstream release notes and upgrade notes
- [ ] Choose `x.x` or `x.x.x` tag using repository policy
- [ ] Update only required files
- [ ] Fix minimum app-local conformance drift required by current gates or generation rules
- [ ] Keep changes app-local
- [ ] Register new translatable env keys in `i18n/translation.json` if needed
- [ ] Run structure, policy, deploy, and reachability checks when applicable
- [ ] Produce a short test report
