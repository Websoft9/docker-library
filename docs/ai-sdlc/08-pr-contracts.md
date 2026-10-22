# PR Contracts

Every PR should contain five short sections:

1. What changed
2. Why changed
3. Automated validation
4. Known risk
5. Owner E2E checklist

Rules:
- one app or one coherent task per PR
- use a Conventional Commits title such as `feat: add app`, `fix: repair login`, or `ci: update release workflow`
- no long narrative
- link the source issue
- link or paste the latest AI test report

PR titles are required because `main` uses squash merges: the PR title becomes the commit subject and the release changelog input.
