# Architecture

This repository is a library of independent app packages, not one runtime service.

Core layout:
- `apps/`: one runnable Docker Compose app per directory
- `archive/apps/`: archived apps removed from active maintenance
- `metadata/maintenance.yaml`: repository-level maintenance metadata
- `metadata/archive.yaml`: archived app metadata and external handoff flags
- `template/`: canonical app template
- `build/`: generation and maintenance scripts
- `docs/`: product, process, and maintainer docs
- `.github/workflows/`: CI, release, and maintenance automation

App contract:
- `.env`: canonical configuration entry
- `docker-compose.yml`: runnable deployment spec
- `variables.json`: metadata for generation and publishing
- `README.md`: generated or maintained app docs
- `src/`: mounted config files referenced by volumes

Shared invariants:
- use the `websoft9` network
- prefer official images or trusted upstream images
- env naming follows repository conventions
- every referenced `src/` file must exist
- every change should be testable by deployment
- machine-readable metadata stays language-neutral; user-facing text belongs in docs, app READMEs, templates, or Contentful

Maintenance architecture:
- cadence decides when an app is checked
- update policy decides what kind of version change is allowed
- machine-readable maintenance metadata lives in `metadata/maintenance.yaml`
- machine-readable archive metadata lives in `metadata/archive.yaml`
- issue is the work unit
- AI report is the handoff to owner E2E

Authority:
- product direction: `docs/vision.md`
- app development rules: `docs/code_owner.md`
- AI delivery process: `docs/ai-sdlc/README.md`
- AI execution hints: `AGENTS.md` and `.github/copilot-instructions.md`
