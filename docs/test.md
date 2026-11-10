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

- `app-check --gate secrets` validates random-template formats, comma-separated lists, closed-vocabulary secret rules (`base64`, `fernet`, `jwt:<SECRET_KEY>`), and variable references; it does not generate keys, connect to an app, or rotate credentials.
- Format/reference/rule tests live in `cli/tests/test_validate.py`, and repository-wide consistency assertions live in `cli/tests/test_consistency.py`.
- Validate the generation dictionary's typed options and documented JSON examples. Missing or invalid dictionaries and unknown options must fail, and template validation must consume the declared byte count, encoding, and JWT algorithm. Generic encoding checks do not prove application-specific length requirements; verify those against upstream references.
- Shared-dictionary delivery tests cover full packages, checksums, dictionary-only dataset version changes without rebuilding unchanged apps, rejection of corrupted artifacts, preflight failure before remote writes, and returned rollback commands for the prior or absent dictionary. These are local contract tests, not evidence of real remote publication or automatic transactional rollback.
- Consumer checks run only on copies in temporary directories. Verify initial generation, reference/prefix preservation, retry reuse, and two different instance identities; never print generated values or mutate downstream sources.
- Deploy only changed runtime inputs. Verify generated secrets against an authenticated action and retain the same keys/data across recreation. Old keys require explicit rotation; creating a new instance is not a rotation test.
