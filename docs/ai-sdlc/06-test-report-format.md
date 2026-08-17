# Test Report Format

Every AI delivery must include:

```md
## Summary
- app:
- task type: update | new-app
- current version:
- target version:
- decision: ready-for-e2e | blocked | defer

## Changes
- files changed:
- upstream references:

## Automated Checks
- structure:
- policy:
- deploy:
- reachability:
- logs:

## Risks
- breaking risk:
- migration risk:
- manual attention points:

## Owner E2E Focus
- check 1:
- check 2:
- check 3:
```

Rules:
- keep it short
- include only the latest result
- blocked tasks must state the first blocking error
