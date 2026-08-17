---
name: Archive app
about: Retire one app or a small set of apps from active maintenance
title: 'Archive [appname-or-group]'
labels: 'update'
assignees: ''
---

## Scope

- [ ] single app
- [ ] small batch with the same archive reason

## Apps

- app name or app list:

## Reason

- archive reason:
- runtime or maintenance evidence:

## Required Handoffs

- [ ] move app from `apps/` to `archive/apps/`
- [ ] update `metadata/maintenance.yaml`
- [ ] update `metadata/archive.yaml`
- [ ] retire Contentful metadata
- [ ] remove from active maintenance scope
