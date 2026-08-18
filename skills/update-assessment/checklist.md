# Update Assessment Checklist

- [ ] Read `apps/<app>/variables.json`
- [ ] Read `apps/<app>/.env`
- [ ] Read `apps/<app>/docker-compose.yml`
- [ ] Read `metadata/maintenance.yaml`
- [ ] Read `docs/ai-sdlc/02-maintenance-policy.md`
- [ ] Detect newest upstream version
- [ ] Classify candidate: patch | minor | major | security
- [ ] Read release notes or changelog
- [ ] Check cadence and update policy
- [ ] Check deployment risk: compose, env, volumes, init flow, login flow, data path
- [ ] Apply `x.x` vs `x.x.x` tag policy
- [ ] Produce final decision: auto-update | review-first | defer | skip
