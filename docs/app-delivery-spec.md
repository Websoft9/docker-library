# App Delivery Spec

| Property | Value |
|---|---|
| Status | Draft |
| Applies to | all app packages |
| Purpose | classify apps by delivery and maintenance model |

## Models

### 1. Compose-First

Use when the upstream app is naturally expressed as `docker-compose.yml` and routine lifecycle work stays simple.

Primary artifact:
- app package

Primary operations:
- install with `docker compose up`
- maintain by editing package files and redeploying

### 2. Compose + Skill

Use when the app can run from Compose, but correct install or maintenance also needs app-specific operational knowledge.

Primary artifacts:
- app package
- app-specific skill

Primary operations:
- install from Compose
- maintain through guided skill actions such as upgrade, repair, migration, or recovery

### 3. Skill-First

Use when the official upstream delivery model is not fundamentally Compose-first, or when correctness depends on upstream-specific bootstrap and rebuild workflows.

Primary artifact:
- app-specific skill

Secondary artifact:
- optional package or derived Compose files when useful

Primary operations:
- install through the skill
- maintain through the skill

## Decision Rule

- choose `Compose-First` when Compose is the upstream-native and maintainable path
- choose `Compose + Skill` when Compose is viable but incomplete for lifecycle operations
- choose `Skill-First` when forcing a plain Compose model would lose important upstream behavior
