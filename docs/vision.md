# Vision

`docker-library` is a curated library of runnable Docker Compose applications for Websoft9.

Goals:
- make app deployment fast
- keep app structure consistent
- reduce per-app configuration drift
- keep upgrades repeatable
- let AI handle routine maintenance work

Product shape:
- each app is an independent project under `apps/<app>`
- each app should run with `docker compose up`
- each app should follow the same env, network, and file conventions

Operating model:
- owner decides demand and final E2E result
- AI handles research, implementation, routine validation, and reporting
- CI enforces repeatable quality gates

Non-goals:
- custom application development
- Kubernetes orchestration
- long-lived backward compatibility for invalid app structure
