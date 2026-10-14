# Suspicious Active App Packages Report

Date: 2026-10-13

Scope:
- active apps under `apps/`
- goal: find packages that look unimplemented, barely adapted, or still mostly a template/scaffold copy

Method:
- repository-wide heuristic scan for placeholder text, demo scripts, generic bootstrap logic, cross-app copy/paste, mismatched image identity, and runtime/scaffold packages presented as finished apps
- manual review of the strongest candidates

## High-Confidence Suspects

These are the apps I consider the most suspicious because they look like they were not really implemented as app packages, or are still mostly template/demo scaffolds.

### 1. `apps/docusaurus`

Why it is suspicious:
- This looks like an old scaffold with very weak app-local adaptation.
- The README contains an obvious cross-app copy/paste error.
- The `.env` layout does not follow current repo packaging conventions at all.

Evidence:
- `apps/docusaurus/.env:1-13`
  The file is only 13 lines, uses `W9_NAME`, has no `W9_REPO`, no protected `W9_ID` block, and no current template structure.
- `apps/docusaurus/README.md:3`
  Still says: `This is an Docker Compose template`.
- `apps/docusaurus/README.md:11`
  System requirements link points to ONLYOFFICE docs: `https://github.com/onlyoffice/docker#recommended-system-requirements`.
- `apps/docusaurus/README.md:18-26`
  README remains generic marketplace/install copy with little app-specific operational detail.

Assessment:
- Strong candidate for “not really upgraded/implemented”.
- Should be reviewed as a stale active package.

### 2. `apps/nodejs`

Why it is suspicious:
- This is not an actual Node.js application package. It is a generic Node runtime that writes and runs a demo app on startup.
- The docs present it like a finished app with an admin console and password flow, which does not match the runtime.

Evidence:
- `apps/nodejs/src/cmd.sh:4`
  Literal placeholder text: `Add your CI code here, below is example`.
- `apps/nodejs/src/cmd.sh:6-21`
  Writes a throwaway Hello World HTTP server into `app.js` and runs it.
- `apps/nodejs/src/cmd.sh:23-52`
  Keeps commented sample sections for Express and Docusaurus.
- `apps/nodejs/.env:12`
  Comment says: `# replace this with your application's port`.
- `apps/nodejs/docker-compose.yml:10-11`
  The package mounts and executes the demo script directly.
- `apps/nodejs/README.md:14-21`
  Generic “sign in to the Node.js admin console” and “Change Password” wording that does not fit a plain Node runtime.

Assessment:
- High-confidence scaffold/runtime package rather than a real app package.
- If intentionally kept, it should likely be classified/documented as a runtime template, not a normal application package.

### 3. `apps/nginx`

Why it is suspicious:
- This package still bootstraps a demo page and tells users to replace it.
- It behaves like a generic hosting scaffold, not a real app implementation.

Evidence:
- `apps/nginx/src/cmd.sh:1`
  `### Default Demo which you can delete it`
- `apps/nginx/src/cmd.sh:3`
  `Add your CI code here, below is example`
- `apps/nginx/src/cmd.sh:4-6`
  Writes `Hello, Nginx!` into `/usr/share/nginx/html/index.html`.
- `apps/nginx/src/cmd.sh:13-16`
  Commented sample download/unzip demo instructions.
- `apps/nginx/docker-compose.yml`
  Mounts and runs that script as part of startup.

Assessment:
- High-confidence generic scaffold package, not a real app-specific packaging effort.

### 4. `apps/springboot`

Why it is suspicious:
- This is a development workspace/demo generator, not a finished Spring Boot application package.
- The public identity and README tone overstate how productized it is.

Evidence:
- `apps/springboot/README.md:14-22`
  Explicitly says the default demo returns `Spring Boot is running...`, `/hello`, `/actuator/health`, and that the project is generated into `/workspace` on first start.
- `apps/springboot/README.md:19-22`
  Tells users to exec into the container and edit Java code in `/workspace`.
- `apps/springboot/README.md:33`
  Claims it is packaged from the “official Spring Boot Docker image”.
- `apps/springboot/README.md:87`
  References `https://hub.docker.com/_/maven`, indicating the actual runtime is Maven-based rather than a Spring Boot app image.

Assessment:
- High-confidence runtime/scaffold package rather than a real application package.
- Similar to `nodejs`, probably intentional, but should not be mistaken for a properly adapted application package.

### 5. `apps/php`

Why it is suspicious:
- This package is largely a generic PHP runtime scaffold with sample bootstrap behavior.
- It still carries “for your reference” demo logic instead of app-specific implementation.

Evidence:
- `apps/php/src/cmd.sh:4`
  `## Sample for you`
- `apps/php/src/cmd.sh:6-12`
  Creates a default `phpinfo()` page when the web root is empty.
- `apps/php/src/cmd.sh:15-21`
  Keeps commented “Install WordPress for your reference” sample steps.
- `apps/php/README.md:3`
  Still uses older wording: `This is an Docker Compose template`.

Assessment:
- High-confidence scaffold/runtime package, not a real app package.

## Medium-Confidence Suspects

These are likely intentional runtime/scaffold packages or partially adapted packages, but they still look misleading or under-implemented.

### 6. `apps/nextjs`

Why it is suspicious:
- Uses a generic Node runtime image and scaffolds a default Next.js app.
- This is closer to a runtime/template than a finished application package.

Evidence:
- `apps/nextjs/.env:1`
  Uses `W9_REPO=node`.
- `apps/nextjs/docker-compose.yml:3`
  Uses `image: ${W9_REPO}:${NODE_IMAGE_TAG}`.
- Existing package behavior and docs indicate first-start scaffold/build workflow rather than a finished application.

Assessment:
- Probably intentional as a runtime package.
- Still suspicious if evaluated as a normal “active app” because it is not really an app package in the usual sense.

### 7. `apps/laravel`

Why it is suspicious:
- Similar pattern to `nextjs` and `springboot`: runtime/scaffold behavior presented like a finished app.

Evidence:
- Uses a PHP runtime stack rather than a Laravel image.
- Repo docs/changelog describe first-start scaffolding of a default Laravel project.
- README language reportedly still uses generic “admin console” and password wording.

Assessment:
- Likely intentional runtime package, but not a true application package.

### 8. `apps/django`

Why it is suspicious:
- Similar runtime/scaffold identity drift.

Evidence:
- Uses `W9_REPO=python` and Python base-image behavior rather than a Django app image.
- Package behavior reportedly scaffolds a default Django project on first start.

Assessment:
- Likely intentional runtime package, but suspicious if counted as a fully implemented application package.

### 9. `apps/openhands`

Why it is suspicious:
- The package identity says `OpenHands`, but the actual image and docs point to Agent Canvas backend setup.

Evidence:
- `apps/openhands/.env:1`
  `W9_REPO=ghcr.io/openhands/agent-canvas`
- `apps/openhands/.env:20`
  Docs URL points to `openhands/usage/agent-canvas/backend-setup/docker`
- `apps/openhands/.env:31-34`
  Uses backend/API-key and secret settings tied to Agent Canvas.

Assessment:
- Could be valid if the app is intentionally this specific OpenHands subproduct.
- Still suspicious because package identity and actual runtime/docs are not cleanly aligned.

## Lower-Severity Template Residue

These apps appear implemented, but still contain clear template leftovers and should be cleaned up.

### `apps/dify`
- `apps/dify/Notes.md:1` is still `# Appname`
- `apps/dify/Notes.md:2` is only `## FAQ`

### `apps/nginxproxymanager`
- `apps/nginxproxymanager/Notes.md:1` is still `# Appname`

### `apps/openhands`
- `apps/openhands/Notes.md:1` is still `# Appname`

### `apps/openclaw`
- `apps/openclaw/Notes.md:1` is still `# Appname`

### `apps/consul`
- `apps/consul/Notes.md:1` is still `# Appname`

Assessment:
- These are not proof of broken packaging by themselves.
- They are good indicators that some active packages never received a full cleanup pass.

## Shortlist

If only a small set should be inspected first, the strongest candidates are:

1. `docusaurus`
2. `nodejs`
3. `nginx`
4. `springboot`
5. `php`

These five most strongly look like one of the following:
- stale old template copies
- generic runtime scaffolds presented as app packages
- packages that were never really adapted into a proper app-specific implementation

## Conclusion

The active app set appears to contain two distinct kinds of suspicious entries:

1. Truly stale or badly adapted packages
- strongest example: `docusaurus`

2. Intentional runtime/scaffold packages that are still misleading when treated as normal application packages
- `nodejs`, `nginx`, `springboot`, `php`, `nextjs`, `laravel`, `django`

If the repository wants every active app to be a real end-user application package rather than a language/framework workspace, the second group should probably be reclassified, documented differently, or removed from the main active app surface.
