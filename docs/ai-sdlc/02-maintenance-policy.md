# Maintenance Policy

Each app gets one maintenance cadence:
- `weekly`
- `monthly`
- `quarterly`

Each app also gets one lifecycle status:
- `active`
- `frozen`
- `archived`

Each app also gets one update policy:
- `patch-minor`: patch and minor can auto-enter update flow
- `minor-only`: patch can be skipped, minor is the main target
- `lts-only`: only stable long-term versions are tracked
- `security-first`: security updates can bypass normal cadence
- `manual-major`: major updates need owner review before development

Worth update decisions:
- `auto-update`: AI starts development now
- `review-first`: AI writes an analysis first, owner decides whether to continue
- `defer`: record and check again in the next cadence
- `skip`: do not process this candidate

Default rules:
- patch: prefer `auto-update`
- minor: `auto-update` if compatible, otherwise `review-first`
- major: default `review-first`
- prerelease, beta, rc: default `skip`
- security fix: may bypass cadence

Priority:
- P0: security or runtime breakage
- P1: compatible patch or high-value minor
- P2: optional feature update
- P3: low-value or risky candidate

Machine-readable source:
- `metadata/maintenance.yaml` stores repository-level maintenance metadata
- `metadata/archive.yaml` stores archived app metadata
- apps not listed in cadence, policy, or lifecycle buckets inherit the defaults
- archived apps are excluded from active update checks
- `libs check-maintenance` validates metadata against `apps/` and `archive/apps/`

Archive metadata shape:
- `defaults`: shared archive behavior
- `apps`: archived app names
- `overrides`: only for exceptional archive cases

Boundary:
- `metadata/maintenance.yaml` is metadata, not a work queue
- `metadata/archive.yaml` is archive metadata, not a work queue
- issues are the work queue
- app-local deploy files stay under `apps/<app>/`
- repository-level cadence and update policy stay in `metadata/maintenance.yaml`
- archived lifecycle and external handoff flags stay in `metadata/archive.yaml`

I18n:
- maintenance and archive metadata should remain language-neutral
- machine-readable files should use stable keys and booleans, not translated prose
- user-facing text stays in docs, README files, issue templates, and Contentful
