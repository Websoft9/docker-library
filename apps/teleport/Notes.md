# Teleport

- Teleport Community Edition 18 runs from the production `public.ecr.aws/gravitational/teleport-distroless` image (no shell). Use `docker exec <container> /usr/local/bin/tctl ...` for in-container commands.
- On first start the `teleport-init` one-shot service renders `src/config/bootstrap.yaml` from `src/config/bootstrap.yaml.tmpl`, hashing the current `W9_LOGIN_PASSWORD` value from `.env`, then Teleport creates the `admin` user and full-access `admin` role with `--bootstrap`.
- MFA is disabled for local users with `authentication.second_factor: off` plus `TELEPORT_ALLOW_NO_SECOND_FACTOR=true`. Remove both to require MFA.
- To change the password: change it in the Teleport Web UI (kept across restarts), or update `W9_LOGIN_PASSWORD` before the first start and redeploy so `teleport-init` regenerates the bootstrap hash.
- `teleport-init` renders `src/config/teleport.yaml` from `TELEPORT_PUBLIC_HOST`. Do not manually edit `teleport.nodename`, `auth_service.cluster_name`, or `proxy_service.public_addr` in the generated file.
- The Web UI and API are HTTPS-only on port `3080` with a self-signed certificate. Check them with:
  `curl -k https://<host>:<port>/webapi/ping`
- Regenerate a starter config with:
  `docker run --rm --entrypoint /usr/local/bin/teleport public.ecr.aws/gravitational/teleport-distroless:18.10 configure --roles=proxy,auth,ssh`
