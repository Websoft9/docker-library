# App Lifecycle UX Spec

| Property | Value |
|---|---|
| Status | Draft |
| Applies to | platform app install and maintenance UX |
| Purpose | define minimal UX rules for dynamic app lifecycle problems |

## Core Rules

### 1. Entry First

- supported package model: `variables.json.access` is an ordered array of port groups keyed by service, container port and transport; each group carries `id`, `service`, `port`, `public`, optional `requireDomain`/`requireHttps`, optional `rootUrl`/`host`/`mappedPort` native variable lists, and `endpoints`. An empty array means confirmed no network entry, while missing `access` is unknown; see [App Access Spec](app-access-spec.md)
- package validation is implemented; this platform UX and instance resolution are separate downstream work
- missing access blocks package validation and publishing; an unknown legacy record is not a completed migration
- default UI should show the entry, not raw ports

### 2. Ports Are Secondary

- ports are advanced details, not the default interaction surface
- when an app has multiple exposed ports, label them by purpose: primary, admin, auxiliary, internal

### 3. Running Is Not Installed

- app state must distinguish between runtime health and setup completion
- minimum states: `not_ready`, `running_uninitialized`, `running_ready`

### 4. Account Mode Must Be Declared

- each app should declare how the first admin identity is obtained
- minimum modes: `package-managed`, `runtime-generated`, `first-login-created`, `external-auth`

### 5. Domain Change Is A Workflow

- changing domain must not be treated as a plain field edit
- the platform should handle it as an action with validation, rewrite, restart or rebuild, and verification

### 6. App-Specific Logic Belongs In Skills

- when correct install or maintenance depends on app-specific behavior, the platform should use an app-specific skill
- do not force all lifecycle operations into one generic form
