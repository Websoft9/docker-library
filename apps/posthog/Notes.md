# PostHog

## Maintenance Notes

- This app was rebuilt from an accidental placeholder/template package.
- Upstream self-hosting is compose-based and tracks floating images rather than stable semver releases.
- `W9_VERSION` intentionally remains `latest` unless Websoft9 decides to pin a known-good tag later.
- The package keeps the app-local topology smaller than upstream hobby by using published images instead of upstream local builds.
