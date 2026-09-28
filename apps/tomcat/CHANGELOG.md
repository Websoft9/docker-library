# CHANGELOG

## 2026-09-21

- Update Tomcat from the floating `10` major tag to `11.0-jdk21-temurin` (Tomcat 11 stable line with JDK21 LTS).
- Refresh the `variables.json` supported tags to the current upstream temurin variants (`11.0` / `10.1` / `9.0` with jdk25/21/17/11/8); drop the `corretto` tags that upstream no longer publishes.
- Align `.env` and `docker-compose.yml` with current repository policy: braced variable references, inline published-port comment, image-env section banner, removal of the `# image:` source comment and obsolete `version`, and a main-container healthcheck.
- Add `apps/tomcat/tests/cases.yml` with a welcome-page smoke test and a WAR auto-deploy test (`war-deploy.sh`) that builds a tiny WAR inside the container and verifies the context.
- Adopt the shared runtime startup mechanism: `src/entrypoint.sh` orchestrator + `src/entrypoint.d/10-webapps.sh` + `src/start.sh`, replacing `src/cmd.sh`. User hooks can be added under `/usr/local/tomcat/.w9/entrypoint.d` without rebuilding, and Tomcat now starts via `exec` as PID 1.
- Regenerate `README.md` from `variables.json` and `docker-compose.yml`.
