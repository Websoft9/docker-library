# App Lifecycle UX Spec

| Property | Value |
|---|---|
| Status | Draft |
| Applies to | platform app install and maintenance UX |
| Purpose | define minimal UX rules for dynamic app lifecycle problems |

## Core Rules

### 1. Entry First

- every app must expose one primary access entry
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
