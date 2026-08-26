# Prompt Fragments

## Remote Rule

`libs app-deploy` is the deployment primitive: it owns local vs remote target resolution, syncs only the `apps/<app>` directory, deploys into the isolated host path `<deploy_root>/<app>` (default `/opt/websoft9-test/apps/<app>`), creates the shared network, runs `config`, `up -d`, and collects `ps`. `appstore-sync` is a different command for platform JSON/directory sync and is not part of generic deploy-validation.

The remote execution defaults come from `.secrets/remote.env` when the file exists; otherwise the workflow falls back to local execution. The SSH secret lives at `.secrets/ssh/default.pem` under the repository root (git-ignored, chmod 600) unless `--ssh-secret-path` overrides it. Detect the file type before connecting:
- private key file -> use `ssh -i <path>`
- password file -> use a password-capable SSH invocation from the environment

Always pass the dedicated-ephemeral-server connection options: `-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=15`. The test server's public IP may be reimaged, so a stale `~/.ssh/known_hosts` entry must never block automation; never read or write the shared known_hosts.

Never mix test-server secrets with developer `~/.ssh` keys and never commit them. The server is assumed dedicated and ephemeral; record its IP openly in the report. Probe on the server via localhost by preference; no IP secrecy is required.

## Evidence Rule

Every result must carry evidence: gate JSON output, `docker compose` output, probe result, and the relevant log lines. Environment blocks (registry unreachable, no docker daemon) are stated as environment blocks, not app defects.

## Cleanup Rule

`libs app-deploy --down` runs in all outcomes, including failures. Server deletion stays manual.
