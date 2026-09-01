# Manual Runbook

Walk the cli + skill system by hand before CI. Use one real app, e.g. `wordpress`.

1. `make install`
2. `libs scan --app <app> --json` and `libs app-drift --app <app> --json`; read `metadata/db-lifecycle.json`; write the assessment report (update-assessment)
3. `libs app-new --name demo-app --trademark "Demo App" --dry-run --json`; optionally prefill `--upstream-releases`, `--upstream-compose`, and `--upstream-env`; check refused duplicates (app-new)
4. `libs app-archive --app <app> --dry-run --json` and `libs app-restore --app <app> --dry-run --json` (archive-app / restore-app)
5. `libs app-check --app <app>` and `libs app-gen-readme --app <app>` (deploy-validation / test-report)
6. Record every blocking point: fix the skill doc or the CLI, then rerun `make test`

Purpose: prove a human can follow the skills end-to-end. Machine tests cover logic; this runbook covers the manual loop.
