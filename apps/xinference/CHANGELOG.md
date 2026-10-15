# CHANGELOG

## 2026-10-13

- Restore the `xinference` app from archive and rebuild the package from the official `xprobe/xinference` image instead of the mis-scaffolded WordPress copy.
- Add the upstream Docker Compose topology: Web UI/API on port `9997`, `/status` healthcheck, and named volumes for `.xinference`, Hugging Face, and ModelScope caches.
- Default to the CPU image variant `v4.0.0-cpu` for initial deployment validation; the GPU variant `v4.0.0` requires an NVIDIA host with CUDA 13.0 and driver 580+.
- After the CPU deployment passed, switch the package to the GPU image variant `v4.0.0` and add the NVIDIA GPU reservation to the compose service.
- Document that authentication is enabled by default since v3.0, so the first Web UI visit creates the initial administrator account.
- Add `tests/cases.yml` with an app-specific `/status` reachability check.
