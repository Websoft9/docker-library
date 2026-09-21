# CHANGELOG

## 2026-09-21

- Bump Teleport from `14.0` to `18.10` and switch the image to the production `public.ecr.aws/gravitational/teleport-distroless`; the old `public.ecr.aws/gravitational/teleport` image stops at `14.4.x`.
- Regenerate `src/config/teleport.yaml` for the v18 schema. Teleport 18 rejects `second_factor: off` unless `TELEPORT_ALLOW_NO_SECOND_FACTOR=true`; the package sets that escape hatch and disables MFA for local users.
- Auto-create the first administrator and a full-access `admin` role on first start from `src/config/bootstrap.yaml` (`--bootstrap`); generate the password setup link with `tctl users reset admin`.
- Add `restart: unless-stopped` and a `tctl status` healthcheck; remove the deprecated `version:` key and the unused `teleport_config` volume.
- Add `upstream` metadata and the web access entry to `variables.json`.
- Add `tests/cases.yml` with an HTTPS `/webapi/ping` check.
- Note: existing 14.x cluster data cannot be upgraded directly to 18.x; upstream requires one major version at a time (14→15→16→17→18). Fresh deployments are unaffected.
