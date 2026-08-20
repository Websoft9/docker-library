# Update Assessment Workflow

Trigger:
- owner opens an update assessment issue
- AI or CI may also start this flow before implementation when a new upstream version is detected

Purpose:
- decide whether an app is worth updating now
- classify the candidate before any code change starts

Required inputs:
- app name
- current version
- upstream source
- candidate version when available
- maintenance metadata from `metadata/maintenance.yaml`

Steps:
1. Run `libs scan --app <app> --json`.
2. Run `libs drift --app <app> --json`.
3. Read repository facts from `apps/<app>/`, `metadata/maintenance.yaml`, and the app README or notes only when scan or drift outputs are incomplete.
4. Classify the candidate as `patch`, `minor`, `major`, or `security`.
5. Assess the database dependency when `libs drift` lists a DB engine image:
   - read `W9_DB_VERSION` from `apps/<app>/.env` as the authoritative current version
   - read `metadata/db-lifecycle.json`; refresh with `libs db-refresh` when stale
   - read the vendor-tested minimum from official docs, not from `externalDB`
   - compare the current version against alive tracks and vendor-tested bounds
   - report a DB finding when the current engine is EOL or a better LTS candidate exists
6. Read upstream release notes, changelog, or upgrade guide.
7. Check whether the candidate fits the app's update policy and cadence.
8. Assess breaking risk for compose, env keys, volumes, init flow, login flow, and data path.
9. Decide one result: `auto-update`, `review-first`, `defer`, or `skip`.
10. Publish a short assessment report in the issue.

Output:
- candidate version
- candidate class
- decision: `auto-update` | `review-first` | `defer` | `skip`
- database finding: current, minimum, recommendation + reason, or `no change`
- short rationale
- upstream references
- owner attention points

Rules:
- this workflow does not change code
- `auto-update` means AI may open or continue an implementation issue now
- `review-first` means stop after assessment and wait for owner approval
- `defer` means record the candidate and check again in the next cadence
- `skip` means no update work should start for this candidate
- when recommending a target image tag, prefer `x.x` over `x.x.x` unless upstream does not provide the `x.x` tag or exact patch pinning is required
- if `libs drift` returns `not-declared` or `source-error`, AI may research missing upstream sources, but should not repeat local dependency inventory already produced by CLI

Decision hints:
- patch: prefer `auto-update`
- minor: `auto-update` if compatible, otherwise `review-first`
- major: default `review-first`
- prerelease, beta, rc: default `skip`
- security update: may bypass normal cadence

Relation to other docs:
- `03-update-pipeline.md` defines the full implementation flow after a candidate is accepted
- `02-maintenance-policy.md` defines the decision vocabulary and defaults
- `07-issue-contracts.md` defines required issue inputs
