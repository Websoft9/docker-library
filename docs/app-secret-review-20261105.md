# Application Secret Review: 2026-11-05

## Decision And Scope

Review only. No application configuration, declaration, consumer, deployment,
publication, or real instance key was changed or rotated by this review.
This is the follow-up to [app-secret-spec.md](app-secret-spec.md).

All 143 current `apps/` packages were included. The repository scan covered
2,765 text files, including active environment inputs, Compose environments,
commands, configuration files, startup scripts, metadata, and source hints.
77 binary, large, or generated/vendor-path files were excluded and recorded.
Archives and image-internal implementation were not inspected exhaustively.
This is a startup Key/Secret audit, not a general deployment, database-password,
network-exposure, or vulnerability audit.

The local Websoft9 consumer was run on temporary copies of every template,
without explicit user overrides. 142 initialized successfully; Semaphore UI
was rejected. For the 142 successful copies, retries retained values and
independent managed fields differed between two installation identities.
Temporary copies and caches were removed. No secret values are in the evidence.
This verifies the local consumer snapshot, not the deployed platform version.

**15 packages have confirmed repository/consumer issues:** 11 ship unmanaged
fixed secret inputs, 3 have identified production-security configuration issues,
and 1 cannot initialize with the current generic consumer. Another 5 need
application-specific format/strength verification; they are not confirmed
startup failures. Successful initialization does not establish key correctness,
image consumption, authenticated use, restore safety, or Owner E2E acceptance.

## Confirmed Findings

| Package | Finding | Evidence |
|---|---|---|
| semaphoreui | `SEMAPHORE_ACCESS_KEY_ENCRYPTION` is declared but its padded-base64 template is rejected by the actual consumer. This is an installation blocker, not merely an inventory warning. | [Environment](../apps/semaphoreui/.env#L1), [Declaration](../apps/semaphoreui/variables.json#L1), temporary consumer rejection |
| supabase | Fixed public signing/encryption/storage defaults are retained. `JWT_SECRET` and the privileged `SERVICE_ROLE_KEY` must not be shared between real installations. `ANON_KEY` is intentionally client-visible, not independently a confidentiality defect. The two JWT signatures currently match their seed and expire at 2027-01-09T23:00:00Z; the group is not independently randomizable. | [Environment](../apps/supabase/.env#L1), [Compose](../apps/supabase/docker-compose.yml#L1), local HMAC/role/expiry check |
| activepieces | `AP_API_KEY`, `AP_ENCRYPTION_KEY`, and `AP_JWT_SECRET` are nonempty fixed inputs, supplied to app/worker but not declared for generation. The consumer leaves them unchanged. | [Environment](../apps/activepieces/.env#L1), [Compose](../apps/activepieces/docker-compose.yml#L1) |
| canvas | Fixed `ENCRYPTION_KEY` and `JWT_ENCRYPTION_KEY` are supplied to both web/jobs and explicitly read by the security configuration; startup does not provision replacement seeds. | [Environment](../apps/canvas/.env#L1), [Security Configuration](../apps/canvas/src/security.yml#L2), [Startup](../apps/canvas/src/entrypoint.sh#L1) |
| dify | Fixed `SECRET_KEY` is unmanaged. Sandbox/plugin internal authentication also has fixed Compose fallbacks and paired server/client inputs, outside generic declarations. These are not the optional provider credentials. Changing only one side would break authentication; no such change was made. | [Environment](../apps/dify/.env#L1), [Shared Environment](../apps/dify/docker-compose.yml#L1) |
| jitsu | Three fixed `JITSU_*_TOKEN` seeds are unmanaged. Compose also hardcodes `JWT_SECRET`, `EE_API_AUTH_TOKENS`, and a JWT seed in `EE_CONNECTION`; the issue is not limited to `.env`. | [Environment](../apps/jitsu/.env#L1), [Compose](../apps/jitsu/docker-compose.yml#L1) |
| lobehub | Fixed `KEY_VAULTS_SECRET` and `AUTH_SECRET` are not generated. Storage access identifiers are not additional encryption seeds; storage secret references have a separate platform source. | [Environment](../apps/lobehub/.env#L1), [Compose](../apps/lobehub/docker-compose.yml#L1) |
| milvus | MinIO receives fixed demo access/secret credentials in Compose, with no installation-specific provisioning there. This is a shared-network storage credential risk, not evidence that a MinIO host port is published. Client/storage coordination still needs checking before any change. | [MinIO Configuration](../apps/milvus/docker-compose.yml#L1) |
| seafile | Fixed `JWT_PRIVATE_KEY` is supplied through `.env` and is not a declared/generated input. Its name alone does not prove it is a PEM private key. The exact application interpretation remains a prerequisite to implementation. | [Environment](../apps/seafile/.env#L1), [Compose](../apps/seafile/docker-compose.yml#L1) |
| typesense | Fixed `W9_LOGIN_API_KEY` supplies server/scraper API authentication. A `W9_LOGIN*` name is not an implicit consumer generation target; the value is retained. | [Environment](../apps/typesense/.env#L1), [API Key Wiring](../apps/typesense/docker-compose.yml#L1) |
| umami | `APP_SECRET` has a platform reference, but nonempty fixed `TWO_FACTOR_ENCRYPTION_KEY` is not declared and remains unchanged. The two-factor business path has not been exercised in this review. | [Environment](../apps/umami/.env#L1), [Compose](../apps/umami/docker-compose.yml#L1) |
| zulip | Lowercase-suffixed `SECRETS_secret_key` is a fixed unmanaged input. Service password references are a different category. The original candidate regex missed this field; the realm-creation hook does not regenerate it. | [Environment](../apps/zulip/.env#L1), [Realm Hook](../apps/zulip/src/create-default-realm.sh#L1) |
| airflow | Compose explicitly sets `AIRFLOW__CORE__FERNET_KEY` to an empty string for the shared service configuration. This is not a missing/pass-through value: it overrides file configuration and leaves connection/variable encryption disabled. No encrypted-connection workflow was tested. Version-specific distributed API JWT defaults are also unverified, not counted as a second confirmed defect. | [Shared Configuration](../apps/airflow/docker-compose.yml#L11), [Upstream Fernet Contract](https://airflow.apache.org/docs/apache-airflow/stable/security/secrets/fernet.html) |
| chatwoot | `SECRET_KEY_BASE` is constructed from the platform password and a fixed suffix. The current generator guarantees punctuation, contrary to upstream's alphanumeric-only guidance. This is a confirmed guidance mismatch, not a demonstrated Rails startup rejection or a claim that the final key is only 16 characters. | [Environment](../apps/chatwoot/.env#L1), [Upstream Requirements](https://developers.chatwoot.com/self-hosted/configuration/environment-variables/) |
| django | Runtime settings override the scaffold's native secret with `${W9_POWER_PASSWORD}`. The consumer supplies 16 characters, below Django's 50-character deployment security check, so the default installation fails that security criterion (`security.W009`), not necessarily application startup. | [Runtime Override](../apps/django/src/entrypoint.d/20-scaffold.sh#L26), [Environment](../apps/django/.env#L1), [Upstream Check](https://raw.githubusercontent.com/django/django/stable/6.0.x/django/core/checks/security/base.py) |

The fixed-input findings establish repository provisioning gaps. Except where a
local configuration reader was inspected, supplying a variable is not proof of
all image-internal consumers. Existing persisted instances may already have
different keys, and explicit user settings may override defaults. Neither
possibility makes the package's default provisioning complete.

## Cross-Package Consumer Risk

97 packages contain `W9_POWER_PASSWORD`. The inspected consumer generates that
field using `PasswordGenerator.generate_strong_password()`: 16 characters,
including punctuation, using Python `random`, not a cryptographic RNG.
`W9_RCODE` also uses the legacy noncryptographic generator. Generic independent
declared secrets use `secrets` instead. Therefore a platform reference is evidence
of generation coverage, **not** a cryptographic strength or application-format
certificate. Multiple derived secrets may also share the same source password.
This is a consumer-owned issue; it was inspected read-only and not changed.

## Pending Verification

| Package | Open Question |
|---|---|
| budibase | `API_ENCRYPTION_KEY`/`JWT_SECRET` use a platform source with fixed additions; embedded LiteLLM master/salt keys also derive from it. Verify actual pinned-image key derivation, accepted format, prefix policy, and distinct purposes. Do not infer AES byte length from the environment name. |
| graylog | Main/DataNode correctly share `GRAYLOG_PASSWORD_SECRET`, but inherit the 16-character legacy password. Verify pinned-version minimum versus production-strength recommendations; a recommendation is not a startup blocker. |
| redmine | Supplied `SECRET_KEY_BASE` is a platform-password reference. Verify pinned Rails/Redmine security requirements and retention behavior; Compose does not call an independent key generator. |
| strapi | `APP_KEYS` and signing/encryption salts are related platform-password constructions, not independent keys. Local configuration consumes them. Verify the pinned Strapi encryption implementation and key-ring semantics before treating generic reference validation as sufficient. |
| superset | The main secret uses a platform source plus a fixed suffix. Its final length must not be confused with the password length. The bundled websocket `jwtSecret` placeholder has no websocket service in the active Compose; it is not counted as an active secret defect. Verify actual main-secret strength and retention requirements. |

These five are deliberately not described as broken deployments. All other
image-internal defaults also remain outside the static proof boundary; the list
above singles out concrete format questions found in supplied inputs.

## Exclusions And Existing Handling

- CKAN's two declared seeds and shared `string:` references are generated by the
  consumer. Its earlier authenticated fresh/recreate regression is historical
  evidence, not a deployment performed by this review.
- Inngest, Langfuse, LibreChat, LiteLLM, LocalAI, and OpenHands pass their current
  declared-template checks. LibreChat's `CREDS_IV` was included even though one
  broader name scan omitted it. This does not prove every application workflow.
- DSH provider API keys, LibreChat/OpenAI credentials, ThingsBoard licenses,
  Superset/Mapbox, and Dify provider/OAuth credentials are external or optional;
  random lookalikes would not provision those providers.
- Jitsi's active component passwords reference the platform source. Optional
  JWT/Matrix/client-secret pass-through fields are not missing mandatory seeds
  under the current default authentication configuration.
- Laravel generates its application key in the persisted application `.env`;
  JupyterHub configures a cookie-secret file in its named volume; QwenPaw uses a
  credential-vault key path under its persisted working directory. These are
  file-owned mechanisms, not missing `env.secrets` declarations.
- Umbraco has a local self-signed certificate generation path and persistent
  certificate directory; Wazuh has a run-once certificate-generator service
  with persisted bind-mounted output. Wazuh's `SSL_KEY` is a pathname, not an
  independently randomizable string. Full certificate lifecycle was not tested.
- OpenClaw, OnlyOffice, OpenDesign, TensorFlow, Trivy, and Vaultwarden key/token
  aliases must be traced to their platform sources rather than automatically
  classified as undeclared literals. Provider identifiers and storage access
  usernames are likewise not independent encryption seeds.
- ERPNext's vendored workflow tokens are CI provider inputs; Registry's bundled
  example config is not mounted by its active Compose; TeamCity's agent
  authorization placeholder is not evidence of an installation seed. Jenkins
  has image-owned credentials and a legacy retrieval script; that script was
  not executed. These hits do not justify generic random generation.

## Complete Package Ledger

Every current package occurs once below. `fixed` and `security` are confirmed
repository/security findings; `blocked` is an actual consumer rejection.
`verify` means an unresolved format question. `managed` means an input source was
identified, not security approval; `file-owned` means a persisted file mechanism
was identified, not a lifecycle test. `external` means no generic seed decision
is appropriate. `source-only` means no additional explicit startup Key/Secret
input was identified in the examined repository surfaces, **not** that the image
has no secrets. The shared platform-generator caveat applies wherever relevant.

| Package | Result |
|---|---|
| activemq | source-only |
| activepieces | fixed |
| affine | source-only |
| airbyte | source-only |
| airflow | security |
| akeneo | managed |
| anythingllm | source-only |
| arangodb | source-only |
| budibase | verify |
| caddy | source-only |
| canvas | fixed |
| chatwoot | security |
| chroma | source-only |
| ckan | managed |
| clickhouse | source-only |
| cloudbeaver | source-only |
| codeserver | source-only |
| consul | source-only |
| couchbase | source-only |
| couchdb | source-only |
| dify | fixed |
| directus | managed |
| django | security |
| dolibarr | source-only |
| drupal | source-only |
| dsh | external |
| elasticsearch | source-only |
| erpnext | source-only |
| espocrm | source-only |
| ffmpeg | source-only |
| geoserver | source-only |
| ghost | source-only |
| gitea | source-only |
| gitlab | source-only |
| gocd | source-only |
| grafana | source-only |
| grav | source-only |
| graylog | verify |
| haproxy | source-only |
| hermes | managed |
| homeassistant | source-only |
| influxdb | source-only |
| inngest | managed |
| jellyfin | source-only |
| jenkins | source-only |
| jfrog | source-only |
| jihu | source-only |
| jitsi | managed |
| jitsu | fixed |
| jupyterhub | file-owned |
| kafka | source-only |
| keycloak | source-only |
| kibana | source-only |
| kong | source-only |
| langfuse | managed |
| laravel | file-owned |
| librechat | managed |
| litellm | managed |
| lobehub | fixed |
| localai | managed |
| logstash | source-only |
| mariadb | source-only |
| matomo | source-only |
| mattermost | source-only |
| mautic | source-only |
| meilisearch | source-only |
| metabase | source-only |
| milvus | fixed |
| mlflow | source-only |
| mongodb | source-only |
| moodle | source-only |
| mysql | source-only |
| n8n | source-only |
| neo4j | source-only |
| nextcloud | source-only |
| nextjs | source-only |
| nifi | source-only |
| nodered | source-only |
| nopcommerce | source-only |
| odoo | source-only |
| ollama | source-only |
| onlyofficedocs | managed |
| openclaw | managed |
| opendesign | managed |
| openhands | managed |
| opensearch | source-only |
| openwebui | source-only |
| oracle | source-only |
| pgadmin | source-only |
| pgvector | source-only |
| phpmyadmin | source-only |
| pocketbase | source-only |
| portainer | source-only |
| postgresql | source-only |
| prestashop | source-only |
| prometheus | source-only |
| qdrant | source-only |
| qwenpaw | file-owned |
| rabbitmq | source-only |
| rancher | source-only |
| redis | source-only |
| redisinsight | source-only |
| redmine | verify |
| redpandaconsole | source-only |
| registry | source-only |
| rundeck | source-only |
| seafile | fixed |
| selenium | source-only |
| semaphoreui | blocked |
| sonarqube | source-only |
| springboot | source-only |
| sqlserver | source-only |
| strapi | verify |
| supabase | fixed |
| superset | verify |
| teamcity | source-only |
| teleport | source-only |
| tensorflow | managed |
| thingsboard | external |
| timescaledb | source-only |
| tomcat | source-only |
| traefik | source-only |
| trivy | managed |
| typesense | fixed |
| typo3 | source-only |
| umami | fixed |
| umbraco | file-owned |
| uptimekuma | source-only |
| varnish | source-only |
| vault | source-only |
| vaultwarden | managed |
| vespa | source-only |
| wazuh | file-owned |
| weaviate | source-only |
| woocommerce | source-only |
| wordpress | source-only |
| wordpresspro | source-only |
| xinference | source-only |
| xwiki | source-only |
| youtrack | source-only |
| zammad | source-only |
| zentao | source-only |
| zulip | fixed |

## Evidence And Remaining Boundary

Generated review evidence:

- [Source Index](../build/secret-review-20261105/source-index.json#L1): all package names, declared/platform inputs, source
  kinds, references, configured services, source-hit locations, file hashes,
  and explicit scan exclusions. No defaults or generated values.
- [Consumer Checks](../build/secret-review-20261105/consumer-checks.json#L1): all 143 temporary-copy outcomes, changed field names,
  retry/identity checks, unchanged unmanaged literal names, and consumer-source
  fingerprint. No defaults or generated values.

The [Original Inventory](../metadata/secret-coverage.json#L1) remains the first-batch candidate
inventory and was not rewritten to imply manual security approval. No general
repository test, runtime deployment, API authorization, or restoration was
performed by this review. Solutions, encoding choices, provider provisioning,
consumer changes, and key rotation remain separate decisions.