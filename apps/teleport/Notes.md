# Teleport

- Teleport Community Edition 18 runs from the production `public.ecr.aws/gravitational/teleport-distroless` image (no shell). Use `docker exec <container> /usr/local/bin/tctl ...` for in-container commands.
- On first start the container creates the `admin` user and a full-access `admin` role from `src/config/bootstrap.yaml` (applied with `--bootstrap`, ignored on later starts).
- The admin has no password yet. Generate the setup link with `docker exec <container> /usr/local/bin/tctl users reset admin` and open it to set the password. MFA is disabled.
- MFA is disabled for local users with `authentication.second_factor: off` plus `TELEPORT_ALLOW_NO_SECOND_FACTOR=true`. Remove both to require MFA.
- The config file `src/config/teleport.yaml` is mounted at `/etc/teleport/teleport.yaml`. Set `W9_URL`, `teleport.nodename`, `auth_service.cluster_name`, and `proxy_service.public_addr` to the domain that resolves to this host. Keep the `:443` port in `proxy_service.public_addr` so generated URLs omit the internal `3080` port.
- The Web UI and API are HTTPS-only on port `3080` with a self-signed certificate. Check them with:
  `curl -k https://<host>:<port>/webapi/ping`
- Regenerate a starter config with:
  `docker run --rm --entrypoint /usr/local/bin/teleport public.ecr.aws/gravitational/teleport-distroless:18.10 configure --roles=proxy,auth,ssh`
