# Deploy Validation Checklist

- [ ] Run `libs check --app <app> --json` locally; stop on the first blocking error
- [ ] Remote: sync `apps/<app>` to the server via tar+ssh and record the server IP
- [ ] Ensure the `websoft9` network exists on the execution target
- [ ] Run `docker compose config --quiet`; stop on failure
- [ ] Run `docker compose up -d` and wait for running or healthy state
- [ ] Web port declared: probe reachability (localhost preferred, public IP acceptable); otherwise verify expected command behavior
- [ ] Check logs for blocking errors
- [ ] Cleanup app resources with `down -v` in all outcomes; server deletion stays manual
- [ ] Return evidence with the first blocking error when failed
