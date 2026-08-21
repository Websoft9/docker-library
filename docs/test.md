# Test Contract

This repository uses five test layers:

1. Unit tests: `cli/libs` pure logic.
2. CLI contract tests: command input, JSON output, and exit code.
3. Metadata and template consistency tests: `metadata/`, templates, `build/` pipeline smoke, and repository facts.
4. App deploy validation: changed apps only, high cost, not the default local loop.
5. Owner E2E: final human verification.

Rules:

- Layers 1-3 must be runnable locally with `make test`.
- Layer 4 is selective, not full-library by default.
- Layer 5 decides ship or reject.

Manual counterpart: `docs/runbook.md`.
