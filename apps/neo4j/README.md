# Neo4j on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Neo4j**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the Neo4j Browser from the published web port and sign in as `neo4j`.
2. When the login page asks for a Connection URL, use `bolt://<server-ip>:<W9_DB_PORT_SET>` where `<server-ip>` is an address reachable from your browser and `<W9_DB_PORT_SET>` is the published Bolt port (the one shown in the Websoft9 console).
3. Create a small test graph or run a simple Cypher query to confirm the database is working.

Note: the Connection URL is resolved from your browser directly to the Bolt port. Using an intranet IP with the host port, or a container name with the container port (for example `bolt://neo4j:7687`), is not supported.

### Change Password

1. Sign in to Neo4j Browser or `cypher-shell` with the current password.
2. Change the password inside Neo4j, for example with `ALTER CURRENT USER SET PASSWORD FROM 'old-password' TO 'new-password';`.
3. Do not rely on changing `.env` after deployment; `NEO4J_AUTH` only sets the initial password on first startup when the `/data` volume is empty.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Neo4j Docker image](https://hub.docker.com/_/neo4j) and makes some improvements below.

<!-- W9_NOTE_START -->
This package tracks the current Neo4j `2026.07` release line with the official Docker image and persists database state in `/data`, which matches the current upstream Docker guidance.

Upstream release notes explicitly warn against using `2026.07.0` because of a data-readability bug in `trim()`. This package therefore publishes the floating `2026.07` tag instead of pinning the bad `2026.07.0` patch.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 2026.07, 2026.07-enterprise, 5.26, 5.26-enterprise.


### Ports

| Purpose | Port |
| --- | --- |


### Data Directory


Data is persisted in the `neo4j` volume, mounted at `/data`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `W9_LOGIN_PASSWORD`, `NEO4J_AUTH` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Neo4j Administrator Guide](https://support.websoft9.com/docs/neo4j) by Websoft9

- [Docker Hub image](https://hub.docker.com/_/neo4j)

- [Releases](https://neo4j.com/release-notes/database/)

- [Official docs](https://neo4j.com/docs/operations-manual/current/docker/introduction/)

- [Official docs](https://neo4j.com/release-notes/database/neo4j-2026-07-1/)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the published ports.

**Forgot or want to reset the Neo4j password?**
- Change it from Neo4j Browser or `cypher-shell`; changing `NEO4J_AUTH` in `.env` does not update an existing database stored in `/data`.
<!-- W9_TROUBLESHOOT_END -->
