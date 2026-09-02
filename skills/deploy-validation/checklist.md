# Deploy Validation Checklist

- [ ] Run `.venv/bin/libs app-check --app <app> --json` locally; stop on the first blocking error
- [ ] Run `.venv/bin/libs app-deploy --app <app> ... --json`; it resolves local/remote, syncs when needed, creates the network, runs `config`, `up -d`, and collects `ps`
- [ ] Run `.venv/bin/libs app-tests --app <app> ... --json`; it derives localhost vs remote base URL and runs default/custom checks
- [ ] Check logs for blocking errors
- [ ] Cleanup with `.venv/bin/libs app-deploy --app <app> ... --down --json` in all outcomes; server deletion stays manual
- [ ] Return evidence with the first blocking error when failed
