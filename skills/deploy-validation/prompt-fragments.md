# Prompt Fragments

## Remote Rule

Sync only the `apps/<app>` directory; it carries compose, .env, and src, including uncommitted changes. The SSH key lives at `.secrets/ssh/default.pem` under the repository root (git-ignored, chmod 600); never mix it with developer `~/.ssh` keys and never commit it. The server is assumed dedicated and ephemeral; record its IP openly in the report. Probe on the server via localhost by preference; no IP secrecy is required.

## Evidence Rule

Every result must carry evidence: gate JSON output, `docker compose` output, probe result, and the relevant log lines. Environment blocks (registry unreachable, no docker daemon) are stated as environment blocks, not app defects.

## Cleanup Rule

`docker compose down -v` runs in all outcomes, including failures. Server deletion stays manual.
