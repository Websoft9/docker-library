# App Tests

`libs app-tests` validates an already deployed app.

Default required checks are adaptive:

- always: `compose-config`, `container-up`
- add `container-healthy` when the main service defines `healthcheck`
- add `web-access` when `.env` exposes `W9_HTTP_PORT_SET`

Optional app-specific checks live in `apps/<app>/tests/cases.yml`.

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

Readiness behavior:

- readiness checks retry for `--wait-timeout` seconds
- retry interval is `--wait-interval`
- remote mode performs one SSH connectivity preflight before running cases
