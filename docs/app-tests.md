# App Tests

`libs app-tests` validates an already deployed app.

Default required checks are adaptive:

- always: `compose-config`, `container-up`
- add `container-healthy` when the main service defines `healthcheck`
- add `web-access` when `.env` exposes `W9_HTTP_PORT_SET`

The default adaptive checks always run. App-specific checks live in `apps/<app>/tests/cases.yml` and are required when the defaults do not exercise the app's core path (for example an authenticated console or API, a dedicated health endpoint, or a startup wait). The `new-app` and `app-update` skills require authoring or refreshing this file; the `deploy-validation` step validates it.

Minimal shape:

```yaml
skip:
  - id: web-access

optional:
  - id: console-login
    type: http-basic
    path: /admin/
    expect_status: 200

custom:
  - id: smoke-script
    type: script
    script: smoke.sh
```

Supported `type` values:

- `compose-config`
- `container-up`
- `container-healthy`
- `web-access`
- `http-basic`
- `script`

Rules:

- `type` is the shared executor kind
- `id` is the app-specific check name
- prefer built-in adaptive checks before adding explicit cases
- do not declare `web-access` when the default root-path check is enough
- use `http-basic` only for real HTTP Basic Auth apps
- use `script` only when built-in checks are insufficient

Script execution target:

- `script` cases run on the deployment target by default: locally for a local deploy, and over SSH for a remote deploy.
- On remote, the script runs from the deployed app directory with the deployed `.env` sourced, and `BASE_URL` is rewritten to `http://localhost:<W9_HTTP_PORT_SET>`. This lets a script use the remote Docker CLI (for example `docker cp`/`docker exec`) to exercise paths the HTTP-only checks cannot reach.
- Set `target: local` on a case to force runner-side execution (for example a check that must run from the caller's network position). On a local deploy every script runs locally regardless.
- Scripts must be self-contained and idempotent; they receive `BASE_URL`, `APP_NAME`, `W9_TARGET` (`local` or `remote`), and the app `.env` variables. Because a script already runs on the deployment target, it normally does not need to branch on `W9_TARGET`; use it only when the check must behave differently on the runner.

Readiness behavior:

- readiness checks retry for `--wait-timeout` seconds
- retry interval is `--wait-interval`
- remote mode performs one SSH connectivity preflight before running cases
