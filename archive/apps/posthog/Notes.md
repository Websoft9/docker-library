# PostHog

## Maintenance Notes

- This app was rebuilt from an accidental placeholder/template package.
- Upstream self-hosting is compose-based and tracks floating images rather than stable semver releases.
- `W9_VERSION` intentionally remains `latest` unless Websoft9 decides to pin a known-good tag later.
- The package keeps the app-local topology smaller than upstream hobby by using published images instead of upstream local builds.
- This package intentionally does not assign `container_name` values so multi-instance isolation can rely on the Compose project name instead.
- Only the `proxy` service joins `${W9_NETWORK}`; the rest of the stack stays on the default Compose network.
- `ENCRYPTION_SALT_KEYS` must be exactly 32 characters for current PostHog builds; generate a replacement with `openssl rand -hex 16`.
