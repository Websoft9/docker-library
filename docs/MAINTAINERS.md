# Maintainers

This repository uses a simple operating model.

Roles:
- Owner: demand, priority, final E2E, release decision
- Maintainer: issue triage, PR review, merge, release execution
- AI Worker: research, implementation, automated validation, test report

Maintainer duties:
- keep issues aligned to `docs/ai-sdlc/07-issue-contracts.md`
- keep PRs aligned to `docs/ai-sdlc/08-pr-contracts.md`
- enforce `docs/ai-sdlc/05-quality-gates.md`
- treat `metadata/maintenance.yaml` and `metadata/archive.yaml` as repository metadata, not as work queues
- ensure archived apps are removed from active maintenance and handed off to Contentful metadata updates

Release rule:
- only owner-approved E2E results may ship

Authority:
- product direction: `docs/vision.md`
- repository structure: `docs/architecture.md`
- delivery process: `docs/ai-sdlc/README.md`
