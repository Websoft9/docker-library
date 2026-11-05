# Test Contract

This repository uses five test layers:

1. Unit tests: `cli/libs` pure logic.
2. CLI contract tests: command input, JSON output, and exit code.
3. Metadata and template consistency tests: `metadata/`, templates, publish pipeline smoke, and repository facts.
4. App deploy validation: changed apps only, high cost, not the default local loop.
5. Owner E2E: final human verification.

Rules:

- Layers 1-3 must be runnable locally with `make test`.
- Layer 4 is selective, not full-library by default.
- Layer 5 decides ship or reject.

Manual counterpart: `docs/runbook.md`.

## Installation Secrets

- `app-check --gate secrets` validates the current consumer's random-template formats and references; it does not generate keys, connect to an app, or rotate credentials. It is a separate migration gate, not included in `all`/`policy` yet.
- Format/reference tests live in `cli/tests/test_validate.py`. Coverage drift and CKAN shared-key assertions prevent incomplete inventory updates and independent signing/verification keys.
- Rebuild the value-free inventory with `PYTHONPATH="$PWD/cli" .venv/bin/python -m libs.secret_audit --output metadata/secret-coverage.json` after changing app inputs, declarations or Compose environment wiring.
- Consumer checks run only on copies in temporary directories. Verify initial generation, reference/prefix preservation, retry reuse, and two different instance identities; never print generated values or mutate downstream sources.
- Deploy only changed runtime inputs. For CKAN, verify a generated API token against an authenticated action and retain the same keys/data across recreation. Old keys require explicit rotation; creating a new instance is not a rotation test.
- Current known Semaphore UI base64 incompatibility and Supabase JWT-group generation remain explicit follow-up work, not hidden exceptions in the validator or successful E2E claims.
