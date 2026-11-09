# Application Database Connection and Declaration Specification

| Item | Description |
| :--- | :--- |
| Status | Phased implementation |
| Updated | 2026-11-04 |
| Principle | Factual declarations only; preserve native variable names, introduce no intermediate variables or runtime controls |

## 1. Goals and Responsibilities

This specification declares only application database dependencies, providing a basis for Websoft9 installation and retrieval/display of supported connection information: hosts, ports, database names, accounts, and usage. Information may be incomplete. Declarations do not select connections, write configuration, persist state, create databases or grants, migrate data, or start/stop services.

Complex applications do not provide external database support. For complex built-in databases, prioritize retrieving and declaring known information without changing `.env`, Compose, initialization scripts, or other source files where possible. Do not force runtime changes to standardize fields, fill unknowns, or provide external connections. Unknown components/fields do not block declarations of other known information; see Sections 1.3 and 4.9 for application boundaries.

Database, search, and vector products do not describe themselves through `database[]`. Their own deployment parameters, entry points, administrative credentials, and initialization remain in existing product configuration/metadata, outside this dependency contract. Determine scope by component role, not application name: if a product depends on another independent in-scope database, declare that dependency, not the product itself. The same database remains declarable when another app depends on it. The shared type dictionary defines dependency engines, not a product self-description inventory.

| Location | Responsibility |
| :--- | :--- |
| `metadata/database-types.json` | Shared engine dictionary: image families, default ports, URL templates, database/account sources, and reusable default account usage |
| `database[]` in `apps/<app>/variables.json` | Application database dependencies, internal services, external engines, and native-variable mappings; override only sources/usage that differ from the dictionary |
| Application `.env`, Compose, and existing configuration | Actual configuration sources; the platform supplies connection parameters through the project `.env` |
| Websoft9 | Display known information from declarations and existing configuration; omit unknown fields without guessing live credentials or active connections |

This file is the sole database connection declaration contract. The type dictionary, metadata Schema, and CLI declaration validation are integrated. Websoft9 UI retrieval, resolution, and configuration writing still require independent consumer implementation; this repository does not execute them.

Supporting updates to this specification, related documentation, dictionary, Schema, CLI, tests, skills, and delivery pipeline are complete; applications enter phased migration/validation. Each batch verifies configuration sources, updates declarations, and runs relevant tests. Examples below do not establish that their packages have migrated; unmigrated apps retain configuration under the transition contract. Record declaration checks, migration coverage, and deployment tests separately. Passing repository tests does not prove full migration or runtime validation; `archive/` is not bulk-rewritten in this phase.

58 applications currently have declarations. This round narrows external support for seven complex apps under Section 1.3 and adds known MongoDB information for `graylog`; its managed Data Node search connection remains unknown, without guessing or blocking known information. Section 1.2 classifies all 146 packages: 58 declared, 88 out of scope for this phase, no whole-package source deferrals. 58 is a coverage count, not proof of complete fields, valid live credentials, or full runtime validation. Database products are not dependency-migration targets; their self-descriptions were withdrawn and boundary regression checks added.

**The following batches are historical implementation records**. External declarations/wiring and initialization-separation conclusions for `supabase`, `erpnext`, `dify`, `budibase`, `jitsu`, and `librechat`, and Graylog's whole-package source deferral, are superseded by Section 1.3. They do not establish current external support. Apps outside this round retain their existing boundaries; none of these batches performed deployment validation.

**Standard connection batch (2026-11-03)**: Apply Section 4.1 connection forms together with relevant cases in Sections 4.2, 4.3, 4.4, and 4.7; do not divide batches by a fixed app count.

| Status | Applications and Boundaries |
| :--- | :--- |
| Declarations completed (13) | `ghost`, `redmine`, `directus`, `dolibarr`, `espocrm`, `metabase`, `moodle`, `prestashop`, `semaphoreui`, `xwiki`, `sonarqube`, `mattermost`, `kong` |
| Subsequent status of deferrals (2) | `mautic`'s variable target-port false positive was fixed; `typo3`'s missing username source was added. Both declarations are complete. Mautic's MySQL 8.0 EOL risk remains; no upgrade in this round |
| Subsequent external-support follow-up | `kong` initially had only an internal declaration; initialization sources were separated and external support declared on 2026-11-04, with deployment validation pending |
| Retained lifecycle risks | MySQL 8.0 for `ghost`, `redmine`, `semaphoreui`, and MariaDB 10.6 for `espocrm` are EOL. Declaration checks do not remove these risks; no database upgrades in this batch |
| Mapping scope | Fixed drivers stay outside `datasource`; unwired optional inputs are not added. Connections without port mappings retain native defaults, without claiming arbitrary parameter support |

**Special-source batch (2026-11-03)**: Implement the following established rules from Sections 4.3, 4.5, 4.6, 4.7, 4.8, and 4.9.

| Application | Implemented Declaration and Source Boundaries |
| :--- | :--- |
| `seafile` | One MariaDB component lists three databases; separate initialization root and application accounts. Map only four wired inputs, supporting external MariaDB/MySQL. Redis cache remains internal with native inputs; trace the password to actual `REDIS_PASSWORD`, including explicit empty values |
| `umami` | Internal/external PostgreSQL use existing `DATABASE_URL`; the administrative account comes from PostgreSQL environment, the application account from initialization scripts, and its password from `W9_RCODE`. Do not map fixed `DATABASE_TYPE` |
| `odoo` | Retain internal/external PostgreSQL, inherit standard database/account sources, and map only `HOST/PORT/USER/PASSWORD`. Add no database-name input; preserve dynamic database creation |
| `langfuse` | Declare only the three established internal components: PostgreSQL, ClickHouse, Redis. Redis password comes from command interpolation `REDIS_AUTH`; MinIO is not a database component |

Existing native inputs/initialization sources satisfy these rules for all four packages; no runtime changes are needed. Structure, policy, and declaration gates pass. Regressions cover service wiring, multiple database sources, script-created accounts, dynamic names, and Redis command interpolation. Lifecycle data still marks `umami`'s `15-alpine` and `langfuse`'s ClickHouse/Redis as `unknown`, not confirmed supported. This batch changed only declarations, changelogs, and tests; no deployment or proof of external connectivity/live credential validity.

**No-runtime-change batch (2026-11-03, 10 apps)**: Migrate using wired native inputs, Section 4.9 wizard rules, and Section 4.10 Runtime rules; do not modify Compose, `.env`, or runtime scripts.

| Category | Applications and Implemented Boundaries |
| :--- | :--- |
| Wired native inputs (3) | `vaultwarden`: MariaDB uses `MYSQL_*` sources; retain `mysql://` and the `W9_RCODE` password source. `chatwoot`: Rails/Sidekiq share native PostgreSQL inputs. `inngest`: Retain the PostgreSQL URI. The latter two retain internal unauthenticated Redis without restricting external primary-database declarations |
| Installation wizards (3) | `drupal`, `nopcommerce`, `teamcity`: Declare actual internal MySQL and inherit standard sources; invent no native inputs or external support. TeamCity targets `teamcity-mysql`, excluding server/agent |
| Optional external Runtime (4) | `django`, `laravel`, `nextjs`, `springboot`: Declare optional `DATABASE_URL` for PostgreSQL/MySQL/MariaDB only, no internal database. Keep default URLs commented out; display neither assumed connections nor SQLite fallback |
| Retained risks | `nopcommerce`'s MySQL 8.0 remains EOL; Redis lifecycles for `chatwoot`/`inngest` remain `unknown`. No image upgrades; declaration checks do not eliminate existing risks |

Regressions cover actual services, all native-input consumers, MariaDB aliases/password sources, wizard boundaries, unconfigured Runtime defaults, and environment pass-through. Remove outdated internal PostgreSQL volume descriptions from Django/Spring Boot READMEs. Only static gates and repository regressions ran; no deployment or live credential/external connectivity verification.

**Multiple-account/search-dependency batch (2026-11-04, 4 complete, 1 source pending)**: Change declarations and supporting files only, not runtime files.

| Application | Declaration Results and Boundaries |
| :--- | :--- |
| `zentao` | Internal MySQL with existing `ZT_MYSQL_*` mappings; declare only configuration-confirmed root, conservatively retain MySQL as the external driver |
| `zulip` | Internal PostgreSQL/Redis under Section 4.9; trace Redis credentials through service environment `REDIS_PASSWORD` and command, without falsely labeling it unauthenticated. Exclude RabbitMQ; Memcached scope remains pending. Invent no complete external mapping |
| `ckan` | PostgreSQL, Solr, Redis. One PostgreSQL instance lists the primary database, datastore, two script-created test databases, and four account-source categories; retain three production URLs. Solr core is `ckan`; retain known Redis logical-database sources; exclude Datapusher |
| `zammad` | PostgreSQL, Elasticsearch, Redis. Separate administrative/script-created application accounts; retain `ZAMMAD_DB*` sources traced to `W9_RCODE`. Check five services sharing `.env`. Elasticsearch security is explicitly disabled; Redis is unauthenticated; exclude Memcached |
| Subsequent `graylog` status | Known internal MongoDB declared, no external support. Data Node search endpoint/TLS/credentials remain unknown; do not assume ordinary OpenSearch or completeness. See Section 1.3 |
| Retained risks | `zentao`'s MySQL 5.7 lifecycle remains `unknown`, not confirmed supported; `zulip`'s PostgreSQL 14 reaches EOL on 2026-11-12; some Redis lifecycles remain `unknown`. No image upgrades |

Add Solr/Elasticsearch types under Section 3 extension rules; seven initial examples are not a permanent limit, and search products get no self-descriptions. Regressions cover new types, actual services, all declared-input consumers, multiple accounts/initialization scripts, Redis command authentication, and security switches. Only static gates and repository regressions ran; no deployment or external connectivity validation.

**Internal multi-storage/optional-dependency batch (2026-11-04, 6 internal declarations complete)**: Declare actual storage under Section 4.9 without changing default deployment/runtime inputs. Passing internal declarations does not prove external wiring is complete.

| Application | Declaration Results and Boundaries |
| :--- | :--- |
| `budibase` | Internal CouchDB, Redis, and LiteLLM PostgreSQL declared. Subsequent batch four wired three CouchDB consumers and LiteLLM database inputs, separated initialization, and declared external CouchDB/PostgreSQL. Redis stays internal; exclude MinIO, proxy, and LiteLLM itself |
| `akeneo` | Internal MySQL/Elasticsearch and five `APP_DATABASE_*` mappings declared. Subsequent batch three separated MySQL initialization and declared external MySQL. Elasticsearch stays internal with security explicitly disabled |
| `jitsu` | Internal PostgreSQL/MongoDB/ClickHouse declared; database names are `postgres`/`admin`, not `schema=newjitsu`. Subsequent batch four wired four consumers and declared external PostgreSQL/MongoDB. ClickHouse stays internal; exclude Redpanda |
| `librechat` | MongoDB, Meilisearch, PostgreSQL vector database declared; MongoDB explicitly uses `--noauth`, database `LibreChat`. Subsequent batch four wired API/RAG inputs and declared external MongoDB/PostgreSQL. Meilisearch stays internal; API keys are not account passwords; admin-panel is not a database |
| `openwebui` | Declare only actual `chroma`, retaining its optional profile, disabled by default with no configured connection inputs. Add no mappings or assumed active instance; exclude application-internal SQLite and Ollama |
| `wazuh` | Declare only `wazuh.indexer` with OpenSearch. Mounted configuration confirms HTTPS. Trace two indexer accounts to existing `INDEXER_*`/`DASHBOARD_*` sources; hashes/Wazuh `API_*` credentials are not indexer passwords. Exclude certificate generator, busybox, manager, dashboard |
| Reviewed, no new declarations (5; not counted as migrations) | `n8n`, `keycloak`, `gitea`, `onlyofficedocs`, `strapi` have no independent database or wired external inputs. Strapi's optional relational parameters remain commented; retain default SQLite, without inventing internal services/external support |
| Retained risks | `jitsu`'s PostgreSQL 14 reaches EOL on 2026-11-12; ClickHouse remains `unknown`. Lifecycle detection does not cover all images; `not_applicable` or partial `ok` does not prove all dependencies supported. No image upgrades/lifecycle changes |

Add Meilisearch, Chroma, and OpenSearch types for dependencies of other apps only, not product self-descriptions. Regressions cover services, inheritance, command interpolation, multiple consumers, initialization coupling, API-key/security-file sources, optional profiles, and exclusions. Only static gates/repository regressions ran; no deployment/external connectivity validation.

**Multiple-consumer/dynamic-database batch (2026-11-04, 4 internal declarations complete, 2 deferred)**: Verify actual consumers and initialization scripts without changing runtime files.

| Application | Declaration Results and Boundaries |
| :--- | :--- |
| `canvas` | Internal PostgreSQL/Redis declared; ERB confirms web/jobs share four primary-database inputs and Redis URL. Subsequent batch three separated initialization password and declared external PostgreSQL. Redis stays unauthenticated; default URL has no logical-database path, so do not guess its name |
| `superset` | One PostgreSQL instance lists primary/examples/script-created `superset_cypress`, with separate primary/example account sources. Four consumers share inputs. Subsequent batch three separated initialization and declared external PostgreSQL. Unauthenticated Redis logical databases remain `0`/`1` |
| `erpnext` | Internal MariaDB, redis-cache, redis-queue declared. List only known root initialization/administrative account, not guessed dynamic site databases/accounts. Subsequent batch five wired shared configuration/site creation, separated administrator password, and declared external MariaDB. Both Redis instances stay internal |
| `supabase` | The base stack has one PostgreSQL instance; list primary database and `_supabase` together, retaining seven known account sources and omitting unconfirmed usage. Subsequent batch five separated initialization and declared restricted external PostgreSQL for compatible Supabase instances. Do not count rest/meta/Supavisor/gateway as instances or enable old topology |
| Subsequent quality-gate deferral status | `dify` was blocked by variable target-port misclassification; validation was fixed, initialization separated, and three components declared, without image upgrades |
| Subsequent runtime deferral status | `phpmyadmin` lacked a password source and `mysql` alias; wiring/declaration now complete under Section 4.9, retaining optional `db` profile and no literal passwords in metadata |
| Retained risks | Relevant Superset/ERPNext Redis lifecycles, Dify PostgreSQL/Redis tags, and phpMyAdmin MariaDB 10.3 remain `unknown`. Supabase's old lifecycle detection still miscounts rest/meta as PostgreSQL by image name; declarations do not inherit this. No lifecycle changes/image upgrades |

No types/model fields added. Regressions cover services, ERB/Python/Elixir consumers, initialization coupling, SQL-created databases/account sources, dynamic sites, and two independent Redis instances. Only static gates/repository regressions ran; no deployment/external connectivity validation.

**Runtime wiring batch (2026-11-04, 3 apps)**: Authorized changes only; no deployment, container startup, appstore synchronization, or publication.

| Application | Completed Changes and Validation Boundaries |
| :--- | :--- |
| `nextcloud` | Wire four native `MYSQL_*` inputs through project `.env` and same-name Compose references; retain independent internal MySQL initialization defaults. Declare internal MySQL and external MySQL/MariaDB |
| `matomo` | Wire four `MATOMO_DATABASE_*` inputs through project `.env` and same-name references; retain `mysql` adapter, table prefix, and internal initialization defaults. Declare internal MySQL and external MySQL/MariaDB |
| `kong` | Initialize internal PostgreSQL through independent `POSTGRES_DB/USER/PASSWORD`, including health checks. Main/two migration services retain shared native `KONG_PG_*` inputs. Declare external PostgreSQL, preserving migration commands/dependencies |

Default images, volumes, and internal connections remain unchanged. No new port input; `datasource` maps only four wired host/database/account/password inputs, not arbitrary ports, TLS, or other options. Checks cover structure, policy, declarations, static Compose, and repository regressions, not successful live connections/migration/switching. Persisted instance configuration may override environment inputs; existing data migration is out of scope. Matomo MySQL 5.7/Kong PostgreSQL 13 remain `unknown`; no image upgrade or claim of confirmed support.

All three passed structure/declaration gates; Nextcloud/Kong passed policy. Matomo initially falsely lacked `web:80` because static validation did not resolve `${W9_HTTP_PORT}`; shared validation was unchanged in that batch. Subsequent Dify/Mautic work fixed resolution, so Matomo policy now passes without port changes. Internal/external static Compose parsing passes; external inputs reach all five consumers without changing internal initialization/health checks. No deployment/live connectivity verification.

**Runtime wiring batch two (2026-11-04, 3 apps)**: Changes/static validation only as requested; no deployment/container startup.

| Application | Completed Changes and Boundaries |
| :--- | :--- |
| `airflow` | Wire two native PostgreSQL URLs through project `.env`/shared environment to seven consumers: API, scheduler, dag-processor, worker, triggerer, init, debug CLI. Internal initialization stays independent. Declare internal/external PostgreSQL and internal unauthenticated Redis broker, retaining logical database `0`/dependencies |
| `phpmyadmin` | Optional `db` root password now uses `MYSQL_ROOT_PASSWORD` defaulting to `W9_POWER_PASSWORD`, retaining original default without rotation; add `mysql` alias. Declare only optional internal MariaDB, root administrative account, existing PMA host/port inputs. Do not enable profile or declare external support |
| `thingsboard` | Main/`init` receive same-name `SPRING_DATASOURCE_URL/USERNAME/PASSWORD`; remove old `POSTGRESQL_*` intermediates. Initialize/health-check through independent `POSTGRES_DB/USER/PASSWORD`, preserving default connection/credentials. Declare internal/external PostgreSQL, retaining installation/demo switches |

These changes complete wiring/declarations, not live connection/migration verification. Do not automatically rewrite persisted instance configuration/credentials. phpMyAdmin's optional database stays disabled; package default passwords are not secure production credentials. Image versions, volumes, and startup dependencies stay unchanged. Airflow Redis/phpMyAdmin MariaDB 10.3 remain lifecycle `unknown`, not confirmed supported.

**Runtime wiring batch three (2026-11-04, 3 apps)**: Address initialization coupling in existing declarations only; no intermediate connection variables, application-template/image changes, or deployment.

| Application | Completed Changes and Boundaries |
| :--- | :--- |
| `akeneo` | MySQL initialization uses independent `MYSQL_DATABASE/USER/PASSWORD` defaults, not application `APP_DATABASE_*`. web/worker retain five native inputs. External support lists only package-confirmed MySQL; Elasticsearch stays internal |
| `canvas` | web/jobs and ERB retain four inputs, including application-side `POSTGRES_PASSWORD`. Internal PostgreSQL independently uses `W9_POWER_PASSWORD`; remove unnecessary full application `env_file` injection from the database. Declare external PostgreSQL; retain internal Redis/bootstrap |
| `superset` | `POSTGRES_DB/USER/PASSWORD` defaults no longer reference `DATABASE_*`. Example initialization retains fixed database/account/password seed inside the database container, not application `EXAMPLES_*`. Four consumers retain ten primary/example inputs. Declare external PostgreSQL; retain three databases/scripts/internal Redis |

All three pass structure/policy/declaration gates and internal/external static Compose parsing. External inputs reach eight consumers without changing internal initialization/auxiliary storage. This does not prove external creation grants, migration, live credentials, or connectivity; prepare external primary/Superset example databases first. Default connections, images, volumes, migration commands, and dependencies remain unchanged. Superset Redis remains `unknown`; no upgrades/lifecycle changes. Canvas has no new native port input and no arbitrary-port promise.

**Runtime wiring batch four (2026-11-04, 3 apps)**: Wire existing native inputs and retain independent initialization; no new drivers, image upgrades, or deployment.

| Application | Completed Changes and Boundaries |
| :--- | :--- |
| `budibase` | app/worker share same-name `COUCH_DB_URL`; wire worker username/password and proxy `COUCHDB_UPSTREAM_URL` through `.env`. CouchDB initialization retains its independent password seed; wire LiteLLM `DATABASE_URL` while retaining PostgreSQL initialization sources. Declare external CouchDB/PostgreSQL; Redis stays internal |
| `jitsu` | console/rotor share two PostgreSQL URLs and MongoDB URL, retaining `schema=newjitsu`. Wire existing ClickHouse inputs by name to console/rotor/bulker/ingest; initialization remains independent. Declare external PostgreSQL/MongoDB. ClickHouse stays internal because bulker/ingest username inputs are unconfirmed; invent no keys or complete external support |
| `librechat` | Wire API `MONGO_URI`/`MEILI_HOST` and four RAG PostgreSQL inputs without changing vector initialization/Meilisearch configuration. Declare external MongoDB/PostgreSQL; Meilisearch stays internal, API keys are not database passwords. External PostgreSQL needs pgvector prepared; no new native port input |

All three pass structure/policy/declaration gates and default/override/baseline static Compose parsing. Ten consumers receive expected inputs; internal initialization/storage/images/volumes/health/dependencies are unchanged. Budibase worker uses the app's existing same-instance CouchDB alias, not a different instance. Remove unnecessary full database `env_file` injection while retaining explicit configuration. No deployment or verification of grants/migration/credentials/connectivity. Existing data is not migrated; internal startup relationships remain. Jitsu PostgreSQL 14 EOL on 2026-11-12 and unknown lifecycle risks remain; no lifecycle changes.

**Runtime wiring batch five (2026-11-04, 2 apps)**: Address shared configuration/initialization boundaries; no metadata business logic, image upgrades, or deployment.

| Application | Completed Changes and Boundaries |
| :--- | :--- |
| `erpnext` | configurator receives same-name `DB_HOST/DB_PORT`, writes shared sites configuration, and site creation waits for that address. Upstream-named `DB_PASSWORD` feeds existing root creation arguments instead of administrator `W9_LOGIN_PASSWORD`; internal MariaDB independently uses `W9_POWER_PASSWORD`. Declare external MariaDB only for confirmed root site creation; database/application accounts remain dynamic; Redis stays internal |
| `supabase` | Retain four `POSTGRES_HOST/PORT/DB/PASSWORD` inputs and eight consumers' fixed roles/URL protocols. Internal port/name defaults remain; initialization independently uses `W9_POWER_PASSWORD`; SQL unchanged. Declare external PostgreSQL only for compatible Supabase instances with roles/extensions/schemas/`_supabase` prepared. Roles continue sharing the configured password; ordinary PostgreSQL is not a drop-in replacement |

Both pass structure/policy/declaration gates and default/override/baseline static Compose parsing. ERPNext configurator/site creation receive consistent inputs; seven shared-sites consumers are unchanged. Container-free script doubles cover new/existing sites, administrator-password separation, skipping existing sites, and no forced dynamic database name. Supabase's eight consumers/Supavisor tenant receive overrides without changing internal initialization; default Compose matches the baseline exactly. Fix project names during comparison to exclude temporary-directory volume-name differences.

Images, volumes, health checks, and dependencies remain; only necessary ERPNext configurator argument references/site inputs change. Existing site credentials/data and Supavisor tenants are not migrated/rewritten; connection inputs do not rotate passwords. Prepare external initialization conditions/grants; internal startup dependencies remain. No deployment or proof of connectivity/migration/role grants. Unknown Redis lifecycles and Supabase rest/meta lifecycle miscounting remain out of scope.

**Initial-example completion batch (2026-11-04, 3 apps)**: Fix confirmed gaps only; existing internal declarations do not mandate runtime changes. No deployment.

| Application | Completed Verification and Changes |
| :--- | :--- |
| `activepieces` | app/worker receive five native `AP_POSTGRES_*` inputs through `.env`. Internal initialization retains fixed database `activepieces`, user `postgres`, and independent `W9_POWER_PASSWORD`; remove unnecessary full database application `env_file`. Declare external PostgreSQL; retain internal Redis/fixed `AP_DB_TYPE` |
| `litellm` | Existing `DATABASE_URL` reaches the app; mounted proxy configuration does not override it, and initialization is independent. Add external PostgreSQL declaration/regressions only; no Compose/`.env`/configuration changes |
| `lobehub` | Existing `DATABASE_URL` reaches the app; initialization is independent. Add external PostgreSQL declaration/regressions only; retain internal Redis/RustFS/init helper, with no Compose/`.env`/source changes |

All three pass structure/policy/declaration gates and default/override/baseline static Compose parsing. Four consumers receive external inputs without changing internal initialization/storage/images/volumes/commands/health/dependencies. LiteLLM/LobeHub defaults match baseline; Activepieces retains initialization/default connections, removing only unnecessary database environment injection. Prepare required external extensions/grants; LobeHub retains internal `pg_search,pg_cron` preload, not an unconditional ordinary-PostgreSQL replacement promise. No deployment, external connection, data migration, rotation, upgrades, or removal of lifecycle risks.

The records above describe historical wiring/example verification. Current narrowed boundaries follow Section 1.3 and package declarations. Internal-only scope does not create mandatory external-support work. Live connections/deployment remain deferred as requested; static validation is not full-library deployment completion.

**Deferral-resolution batch (2026-11-04, 4 complete, 1 source deferred)**: Fix clear blockers; do not guess connection sources or deploy.

| Application | Results and Boundaries |
| :--- | :--- |
| `dify` | Primary/plugin PostgreSQL databases share one component; API/worker/plugin daemon share host/port/account/password, retaining a separate native plugin database name. Initialization no longer references app inputs; remove excess PostgreSQL/Redis environment injection. Retain Redis authentication/logical databases `0/1`/internal Weaviate. New Weaviate type supplies only default HTTP port/image source; API key is not a password. Declare external PostgreSQL only, requiring two prepared databases/grants |
| `mautic` | web/cron/worker have five wired `MAUTIC_DB_*` inputs and independent initialization. Add internal/external MySQL declarations; retain Compose/`.env`/MySQL 8.0 EOL risk |
| `typo3` | Native administrator username referenced missing `W9_LOGIN_USER`; add `admin` default. Declare internal/external MySQL for five inputs; do not map fixed `mysqli`. Retain entrypoint/Compose/first-install limits; no automatic existing-site configuration changes |
| `kibana` | Official Docker documentation confirms environment mappings/JSON host arrays; declare optional external Elasticsearch through existing `.env`. Keep `ELASTICSEARCH_HOSTS` commented, mapping `["${url}"]` as a single-target array without assumed active backend. Tokens/TLS are not database passwords; no runtime changes |
| `graylog` (known information added this round) | Graylog/Data Node share MongoDB URI; declare actual `mongodb` service/database `graylog`, no external support. Search endpoint/TLS/credentials remain unknown. Neither management port 8999 nor Graylog login password represents search connectivity; declaration does not imply completeness |

Shared policy validation now resolves target ports from project `.env` only, supporting ordinary references and `:-`/`-` defaults without host overrides. Dify/Mautic/Matomo false positives are fixed without mapping changes. Four packages pass gates/default/override/baseline Compose parsing; eight consumers receive inputs without affecting initialization/storage. Dify only makes the implicit Redis broker default port explicit; connection semantics/images/volumes/commands/health/dependencies remain unchanged. Static checks do not prove connectivity/migration/grants; no persisted-site rewriting, upgrades, synchronization, or publication.

### 1.1 Compatibility and Delivery

- New/migrated apps use only `database[]`. During transition, Schema accepts legacy objects; CLI reports `legacy`/migration follow-ups without guessing new sources from old fields. Archives may remain unchanged until restoration reports migration requirements.
- Shared definitions use only `metadata/database-types.json`. Removed `metadata/database-defaults.json` is neither a compatibility layer nor fallback. Legacy objects receive identification/migration notices, not expansion through the draft. `externalDB` remains user help; `db-lifecycle.json` remains lifecycle facts.
- `app-info` returns the new array in `database_connections`, declaration validation in `database_metadata`, and lifecycle in `database_lifecycle`; original `database` remains a lifecycle compatibility alias. None returns resolved environment values.
- Full library packages include `metadata/database-types.json`; incremental releases distribute that dictionary separately with checksums. Dictionary content contributes to library versions. Consumers validate/update/roll back declarations and dictionary as one snapshot, not apps alone.
- The former database object was experimental and was not enabled in product consumers. Optional `database[]` declarations and the shared dictionary are additive library schema 1 extensions, not a reason to raise the library schema. Consumers implementing connection features must support the arrays and dictionary; existing installation workflows may ignore unused declarations.
- Aggregate `app-check` includes declaration structure, component ID uniqueness, actual service references, and dictionary engine checks. It does not validate live credentials, require unknown source values, select connections, or execute database operations.

### 1.2 Full-Library Coverage Inventory

As of 2026-11-09, all 146 current `apps/` packages have mutually exclusive classifications without omissions/duplicates; exclude `archive/`. Building on migrations, check remaining apps' `app-info` service/image roles and native inputs under Section 4.11. Verify JFrog Derby, Umbraco local SQLite DSN, and Kibana/Logstash configuration entry points. `not_applicable` alone does not prove absence of database dependencies; do not infer configured connections from key names, image defaults, or examples.

| Status | Count | Applications | Boundaries and Follow-Up |
| :--- | ---: | :--- | :--- |
| `declared` | 58 | `activepieces`, `affine`, `airflow`, `akeneo`, `budibase`, `canvas`, `chatwoot`, `ckan`, `dify`, `directus`, `django`, `dolibarr`, `drupal`, `erpnext`, `espocrm`, `ghost`, `graylog`, `inngest`, `jitsu`, `kibana`, `kong`, `langfuse`, `laravel`, `librechat`, `litellm`, `lobehub`, `matomo`, `mattermost`, `mautic`, `metabase`, `moodle`, `nextcloud`, `nextjs`, `nopcommerce`, `odoo`, `openwebui`, `phpmyadmin`, `prestashop`, `redmine`, `seafile`, `semaphoreui`, `sonarqube`, `springboot`, `supabase`, `superset`, `teamcity`, `thingsboard`, `typo3`, `umami`, `vaultwarden`, `wazuh`, `woocommerce`, `wordpress`, `wordpresspro`, `xwiki`, `zammad`, `zentao`, `zulip` | Current-phase declarations under Section 1.3/actual packages may cover known information only. Graylog Data Node remains unknown; no claim of complete fields, deployment, or all external validations |
| `deferred-runtime` | 0 | None | Listed runtime wiring/example verification is complete; policy/source blockers are separate. Internal-only scope is not pending runtime work |
| `deferred-policy` | 0 | None | Port false positives/missing login username fixed; three packages moved to declared. Lifecycle risks remain separately recorded |
| `deferred-source` | 0 | None | Declare known information without blocking whole apps on unknown components. Graylog is declared, with Data Node gaps retained, not filled from examples/OpenSearch defaults |
| `excluded-product` | 25 | `arangodb`, `chroma`, `clickhouse`, `couchbase`, `couchdb`, `elasticsearch`, `influxdb`, `mariadb`, `meilisearch`, `milvus`, `mongodb`, `mysql`, `neo4j`, `opensearch`, `oracle`, `pgvector`, `postgresql`, `qdrant`, `redis`, `rethinkdb`, `sqlserver`, `timescaledb`, `typesense`, `vespa`, `weaviate` | No database/search/vector self-descriptions. Exclude backup/init/console/etcd/object storage by role; reassess if independent database dependencies are added |
| `excluded-sqlite` | 8 | `anythingllm`, `hermes`, `jupyterhub`, `mlflow`, `pocketbase`, `strapi`, `umbraco`, `uptimekuma` | Current SQLite storage is excluded; commented optional inputs do not prove wired external connections |
| `excluded-internal` | 12 | `airbyte`, `gitea`, `gitlab`, `grafana`, `homeassistant`, `jfrog`, `jihu`, `keycloak`, `n8n`, `onlyofficedocs`, `rundeck`, `youtrack` | Self-managed/image-internal storage under Section 4.11, without declarable independent standard databases/wired external sources; infer no internal topology |
| `excluded-client` | 3 | `cloudbeaver`, `pgadmin`, `redisinsight` | No bundled independent database; general clients/user-added targets are not package database dependencies |
| `excluded-tool` | 40 | `activemq`, `caddy`, `codeserver`, `consul`, `dsh`, `ffmpeg`, `geoserver`, `gocd`, `grav`, `haproxy`, `jellyfin`, `jenkins`, `jitsi`, `kafka`, `localai`, `logstash`, `nifi`, `nodered`, `ollama`, `openclaw`, `opendesign`, `openhands`, `php`, `portainer`, `prometheus`, `qwenpaw`, `rabbitmq`, `rancher`, `redpandaconsole`, `registry`, `selenium`, `symfony`, `teleport`, `tensorflow`, `tomcat`, `traefik`, `trivy`, `varnish`, `vault`, `xinference` | Tool/framework-runtime/gateway/queue/model/monitoring packages have no in-scope independent database/wired native connection. APIs/models/collection targets/disabled examples are not database connections |

This is static package coverage, not persisted runtime state or business control. Reassess classifications after adding apps/dependencies/native inputs; consistency tests check coverage, exclusivity, counts, and declaration/status agreement. Graylog search information remains unknown; requested deferrals of live connections/deployment and lifecycle risks remain. Internal-only information does not mandate external support/runtime changes or imply complete runtime validation.
<a id="13-复杂应用信息优先与本轮收缩"></a>
### 1.3 Information-First Boundaries for Complex Applications

Complex apps do not provide external databases. Determine complexity by roles, initialization/grants, dynamic site creation, shared generated configuration, and coordinated storage, not container/consumer/URL counts or Redis presence. Native connection variables do not promise package external support.

| Application | Current Declaration and Runtime Boundaries |
| :--- | :--- |
| `supabase` | Internal PostgreSQL only; retain two known databases/seven account sources. Withdraw external declarations/mappings/external-only initialization separation; restore `POSTGRES_PASSWORD` first-start marker. Leave role SQL/pooling/consumers unchanged |
| `erpnext` | Internal MariaDB/two Redis only; declare known root, not guessed dynamic site databases/accounts. Restore internal host/port, remove external-only inputs. Retain independent fix separating root `W9_POWER_PASSWORD` from administrator `W9_LOGIN_PASSWORD` |
| `budibase` | Internal CouchDB/Redis/LiteLLM PostgreSQL only. Restore original expressions/initialization sources, remove external-only inputs; do not force same-instance alias unification |
| `jitsu` | Internal PostgreSQL/MongoDB/ClickHouse only. Restore four consumers' expressions; `schema=newjitsu` is not a database name. Add no native variables merely for retrieval |
| `librechat` | Internal MongoDB/Meilisearch/RAG PostgreSQL only. Restore runtime configuration, retaining known names, evidence of no authentication, and API-key/password distinction |
| `dify` | Internal PostgreSQL primary/plugin databases, Redis, Weaviate only. Restore initialization sources; declare default `postgres` explicitly without new database environment solely to match the dictionary. Preserve user wiring/formatting/verified Redis isolation; no whole-file revert |
| `graylog` | Add known internal MongoDB information only: actual service, database `graylog`, no declared account; no runtime changes. Data Node endpoint/TLS/credentials remain unknown. Do not guess OpenSearch/9200/management port or block MongoDB declaration |

None of these seven provides external support or needs `datasource`. Trace internal information through actual service environments/commands/scripts/configuration; override differing `name/users` without changing sources to fit the dictionary. Unknowns remain unknown; empty arrays prove neither absent accounts nor complete internal-storage coverage.

Do not change candidate boundaries for `superset`, `akeneo`, `lobehub`; existing restricted declarations do not promise arbitrary compatibility. Airflow's multiple consumers/two PostgreSQL URL forms/Redis coexistence alone do not imply complexity. Other apps retain verified scope; do not bulk-cancel simple native external support.

Retain independent shared-port/TYPO3-username fixes. Withdraw only clearly external-specific changes, not user edits. Validate structure/policy/declarations/static Compose/repository regressions. As requested: no deployment/container startup/live credentials/synchronization/publication.

**Test report (2026-11-04)**: Narrow seven declarations without application/dependency version changes. Configuration/static checks complete; deployment/Owner E2E pending.

| Check | Latest Result |
| :--- | :--- |
| Structure/policy/declarations | All seven pass; 154 consistency regressions cover internal-only/README boundaries, Graylog known information, full inventory, and Section 1.4 deployment scope |
| Static Compose | All seven parse/baseline comparisons pass. ERPNext retains quoted arguments; root/admin separation has new/existing-site doubles. Dify retains database isolation/equivalent broker port/three Nginx native inputs via `env_file`, each verified separately, without claiming byte-identical full configuration |
| Full tests | `PYTHONPATH="$PWD/cli" make test`: 557 CLI + 170 build + 15 skill = 742 passing; existing Typer/Click deprecation warnings only |
| Deployment/probes/logs/live credentials | Not executed as requested; static/script-double checks do not replace runtime verification |
| Risks/Owner E2E | Lifecycle risks/persisted credentials/dynamic gaps remain; later deployment must verify internal initialization/existing sites/information display, not external acceptance |

### 1.4 Full-Library Static Acceptance and Deployment Follow-Ups

This section covers all current `apps/`, not just Section 1.3's seven packages. On 2026-11-04, read `app-info` for all 143: all 58 in-scope declarations passed structure/policy/declaration gates; 85 were excluded under Section 1.2, not omitted or deemed storage-free. Database products, SQLite/etcd, and image-internal storage do not require changes merely because they contain databases. Known-information declarations/supporting changes are complete without whole-package static blockers; field completeness/runtime validation are not implied.

**Latest full-library static acceptance (2026-11-04)**:

| Check | Result and Boundary |
| :--- | :--- |
| Coverage | All 143 included once: 58 declared, 85 excluded; dynamic/unknown boundaries retained |
| Structure/policy/declarations | All 58 pass; add full gate regression coverage beyond the latest seven |
| Static Compose | All 58 pass `config --format json` with all optional profiles, isolating same-name host variables. Output checked in memory only; no credential printing, image pulls, or container startup |
| Repository tests | `PYTHONPATH="$PWD/cli" make test`: 557 CLI + 170 build + 15 skill = 742 passing, including 154 consistency checks |
| Deployment/connections | This table records static acceptance only; subsequent deployment/probe/data-retention results are in Section 1.4.4, not replaced by static checks |

Determine deployment follow-ups from retained runtime differences, not every file historically touched. Declaration/Schema/dictionary/documentation/test-only changes do not automatically trigger redeployment; external connectivity requires separate acceptance. The lists below define scope; Section 1.4.4 records execution/results/follow-ups.

Under the user's 2026-11-05 scope confirmation, deploy only differences affecting runtime. Do not deploy `variables.json`-only nonruntime changes; retain static acceptance for 45 declaration/documentation-only packages. Section 1.4.3 external tests are deferred, not blockers here. Reuse completed evidence when runtime files are unchanged; metadata changes do not require reruns. Latest additional tests are in Section 1.4.12.

#### 1.4.1 Runtime Changes Requiring Deployment Regression (13 Packages)

Deployment regression scope follows; see Section 1.4.4 for execution. Cover at least fresh-volume initialization, recreation with existing volumes, health, and one core business path, without production data. External entries test only declared engines/inputs; do not expand complex-app external boundaries.

| Application | Changed Runtime Files | Runtime Change Trigger | Deployment Acceptance Focus |
| :--- | :--- | :--- | :--- |
| `activepieces` | `docker-compose.yml` | PostgreSQL initialization moves from AP_POSTGRES inputs to original database/account defaults/independent password seed; remove full app environment injection | Fresh initialization/app-worker agreement/task execution; external overrides leave internal initialization unchanged |
| `airflow` | `.env`, `docker-compose.yml` | Two native PostgreSQL URLs supplied through project environment to seven consumers | Correct metadata migration/API/scheduler/worker/init/result connections |
| `akeneo` | `.env`, `docker-compose.yml` | MySQL initialization uses independent MYSQL_DATABASE/USER/PASSWORD, not APP_DATABASE inputs | Fresh grants/web-worker/initialization/search indexing; Elasticsearch stays internal |
| `canvas` | `docker-compose.yml` | Internal PostgreSQL uses initialization password seed; remove full app environment injection | Shared web/jobs credentials/bootstrap/existing-database compatibility; overrides do not rotate internal passwords |
| `dify` | `.env`, `docker-compose.yml` | Retain native port/vector wiring, variable normalization, PostgreSQL/Redis isolation, explicit Redis authentication | Primary/plugin initialization/API-worker-plugin/Redis broker/vector reads-writes; internal only |
| `erpnext` | `docker-compose.yml`, `src/create-site.sh` | Quote configurator arguments; site-creation root uses database seed, not administrator password | Fresh site grants/admin login/shared configuration/skip existing sites; internal only |
| `kong` | `.env`, `docker-compose.yml` | Independent POSTGRES initialization/health source, not KONG_PG inputs | Database health/both migration types/gateway/routes; overrides leave initialization unchanged |
| `matomo` | `.env`, `docker-compose.yml` | Four MATOMO_DATABASE fixed Compose inputs become same-name project references | Wizard/connection/one statistics write; persisted configuration/environment precedence |
| `nextcloud` | `.env`, `docker-compose.yml` | Four MYSQL fixed Compose inputs become same-name project references | First installation/database/login/files; retain configuration, environment changes are not migration |
| `phpmyadmin` | `.env`, `docker-compose.yml` | Optional db root password uses source variable; add mysql alias | db disabled by default; explicit-profile alias/login tests; no existing-root rotation |
| `superset` | `.env`, `docker-compose.yml` | Separate primary/example initialization from inputs; normalize worker health references | Primary/example/test databases/accounts/migration/four consumers/Celery health; no arbitrary replacement promise |
| `thingsboard` | `.env`, `docker-compose.yml` | Main/init receive three SPRING_DATASOURCE inputs, replacing intermediates; independent POSTGRES initialization/health | init schema/demo/main authentication/writes/two-consumer consistency/existing volumes |
| `typo3` | `.env` | Add missing W9_LOGIN_USER default already referenced by administrator username | Fresh administrator creation/login; no existing-site reinitialization/account changes |

#### 1.4.2 Declaration or Documentation Only: No Additional Deployment (45 Packages)

`affine`, `budibase`, `chatwoot`, `ckan`, `directus`, `django`, `dolibarr`, `drupal`, `espocrm`, `ghost`, `graylog`, `inngest`, `jitsu`, `kibana`, `langfuse`, `laravel`, `librechat`, `litellm`, `lobehub`, `mattermost`, `mautic`, `metabase`, `moodle`, `nextjs`, `nopcommerce`, `odoo`, `openwebui`, `prestashop`, `redmine`, `seafile`, `semaphoreui`, `sonarqube`, `springboot`, `supabase`, `teamcity`, `umami`, `vaultwarden`, `wazuh`, `woocommerce`, `wordpress`, `wordpresspro`, `xwiki`, `zammad`, `zentao`, `zulip`.

These packages retain no database runtime changes from this work. External-only wiring for Budibase/Jitsu/LibreChat/Supabase was withdrawn; Graylog only adds MongoDB metadata. Display declarations/optional dependencies/unknowns factually; no additional deployment does not mean connectivity was validated.

#### 1.4.3 Separate External-Connection Acceptance Within Declared Scope (43 Packages)

These packages declare external support through added/migrated providers/native mappings. Static tests verify mappings/wiring, not networking/authentication/TLS/roles/extensions/creation grants/migration. Before claiming external support works, perform targeted connection/business acceptance against prepared databases; do not label them deployment-passed. Ten overlap with the 13 runtime-change packages and are not double-counted; the other 33 have no additional runtime changes.

`activepieces`, `affine`, `airflow`, `akeneo`, `canvas`, `chatwoot`, `ckan`, `directus`, `django`, `dolibarr`, `espocrm`, `ghost`, `inngest`, `kibana`, `kong`, `laravel`, `litellm`, `lobehub`, `matomo`, `mattermost`, `mautic`, `metabase`, `moodle`, `nextcloud`, `nextjs`, `odoo`, `prestashop`, `redmine`, `seafile`, `semaphoreui`, `sonarqube`, `springboot`, `superset`, `thingsboard`, `typo3`, `umami`, `vaultwarden`, `woocommerce`, `wordpress`, `wordpresspro`, `xwiki`, `zammad`, `zentao`.

Use only declared drivers/inputs/limits. Runtime/Kibana remain unconfigured by default; test explicit connections separately. Generic protocol support does not replace extension/initialization/search compatibility acceptance for LobeHub/Superset/Akeneo. This list does not reopen external support for seven complex apps.

#### 1.4.4 Deployment Regression Execution: 2026-11-04

This records Section 1.4.1 execution, superseding historical "not deployed" status, not external tests/manual E2E. This run ended with ten fresh-install automated checks: eight had no scoped fresh/retained-marker blockers, ThingsBoard had existing-volume initialization errors, Superset exceeded the baseline-init budget, and three were not deployed due to disk protection. This is not all 13/core-business acceptance.

- Target: Configured dedicated remote test host, 4 cores, 7521 MiB RAM, 39 GiB system disk, initially approximately 32.7 GiB free.
- Isolated directory: `/opt/websoft9-test/db-regression-20261104-27f049e2`; exclude existing `websoft9-dev` from deployment/cleanup.
- Baseline: `fd4c72a7d637ef5fe570170dbdcfc5ad64c533d1`; initialize baseline configuration, write a test-table marker, replace package files, recreate retaining volumes. Reuse images without version upgrades.
- Scope: Direct Compose; no `appstore-sync`, publication, or external testing. No initial source edits; later authorized Superset fixes are in Section 1.4.5.
- Evidence: Local `build/db-regression-20261104-27f049e2/results.json`. Test containers/Compose named volumes removed; no global image/platform cleanup.
- Initial cleanup: Only original healthy `websoft9-dev` remained. Of six unreferenced anonymous volumes, three empty and one containing the test marker were verified/deleted; two nonempty unidentified volumes retained, without global prune. A later Superset instance was retained for fix verification.
- Resource blocker: Approximately 6.45 GiB free at protection trigger, 6.56 GiB after cleanup, image cache retained. The executor required 8 GiB before deployment, so ERPNext/Canvas/Akeneo created no directories/containers. Their JSON `cleanup=false` means no started project to down, not leaked instances; read-only checks confirmed directories absent.

| Application | Fresh Automated Check | Existing Volumes and Database Marker | Additional Business Checks and Boundaries |
| :--- | :--- | :--- | :--- |
| nextcloud | Passed | Passed | WebDAV upload/download/delete in both phases |
| typo3 | Passed | Passed | Backend/install entry reachable; administrator creation/login await manual E2E |
| matomo | Passed | Passed | Install entry reachable; wizard/statistics writes await manual E2E |
| phpmyadmin | Passed | Passed | No default database; separately enable db profile and verify mysqli root login via mysql alias |
| kong | Targeted checks passed | Passed | Service/route creation/query/proxy/delete in both phases; empty-gateway 404 is not startup failure |
| activepieces | Passed | Passed | app/worker healthy; real workflows await manual E2E |
| thingsboard | Passed | Marker retained; overall failed | Retained-volume init exits 1; main/setup API work; initialization lifecycle investigation pending |
| airflow | Passed | Passed | API/main pass; some sidecars only have starting snapshots; real DAG pending |
| superset | Basic checks passed; health fix in 1.4.5 | Full migration incomplete | Baseline init hit 240-second limit; later confirmed successful initialization, but mount hid health script. Fix passed health/script recreation-retention checks |
| dify | Passed | Passed | Main/marker checks pass both phases; initial connection errors absent from recreated log snapshot. Plugin/vector/E2E pending |
| erpnext | Environment-blocked, not deployed | Pending | Less than 8 GiB before deployment; local HRMS exists; site creation/login untested |
| canvas | Environment-blocked, not deployed | Pending | Less than 8 GiB; declared requirement 20 GiB; custom build not performed |
| akeneo | Environment-blocked, not deployed | Pending | Less than 8 GiB; custom build/initialization not performed |

All Owner E2E awaits manual confirmation. Database test tables verify connection/retention, not core business acceptance. Assess migration/init exit 0 separately from resident containers running; interpret startup-log matches alongside recovery/business outcomes.

Remaining actions: Provide test storage for builds/cache/runtime, then resume ERPNext/Canvas/Akeneo. Match Superset local-init budgets to measured example-import time while retaining defaults, not extending network timeouts. Investigate ThingsBoard retained-init exits and separate existing lifecycle issues from regressions. Update this record before core-business/Owner E2E. Without approval, do not expand paid resources, globally clear caches, or change source merely to pass validation.

#### 1.4.5 Superset Health Script and Retained-Data Verification

Apache Superset `6.1.0` Dockerfile/Compose/startup scripts confirm the probe calls `/app/docker/docker-healthcheck.sh`. Package mount `./src/docker:/app/docker` hides that file, causing exit 127 while `/health` returns 200. Add the executable upstream-logic probe without disabling health checks.

Upstream dev worker/beat can skip driver installation, but this package's `apache/superset:6.1.0` release image lacks `psycopg2`. Do not copy that condition; install only if missing, preserving first-start driver availability for all consumers. Image/Compose/database connections/example switch unchanged.

Sync only two scripts remotely; recreate Web/worker/beat with `--no-deps --force-recreate --pull never --no-build`, not database/init. Web/worker healthy, beat running, original init exit 0; image probe passes, database container ID unchanged, pre-recreation marker readable. Append `superset_script_fix_verifications` without overwriting initial timeout evidence.

This proves script fixes/process-recreation retention only, not full pre-change-HEAD migration. Retain Superset for inspection; Owner login/charts/datasets E2E pending. Other resource blockers/scope unchanged.

#### 1.4.6 Superset Example Import Timing and Disabled Default

Two isolated fresh-volume runs using cached `6.1.0`: examples enabled, initialization 468.44 seconds (424.68 import), all healthy 506.94; disabled, initialization 44.40, all healthy 83.40. Both exit 0; test containers/volumes/networks removed, original Superset/Websoft9 healthy. Evidence: `build/superset-fresh-timing-20261104/results.json`.

Example import reads image-bundled Parquet and creates demonstration data/charts; it is optional. As confirmed, default `SUPERSET_LOAD_EXAMPLES` to `no`, retaining migrations/admin creation/permission initialization. Delete no existing examples or example-database scripts/declarations. Explicit `yes` remains available.

#### 1.4.7 Resuming Incomplete Tests on a New Server (2026-11-05)

Using updated remote configuration, resume ERPNext/Canvas/Akeneo/Superset in an isolated directory, without rerunning completed apps. Baseline remains `fd4c72a7d637ef5fe570170dbdcfc5ad64c533d1`, image versions unchanged. Migration means pre/post-declaration configuration migration, not database major upgrades.

| Application | Current Fresh Install and Retained Recreation | Baseline Configuration Migration | Latest Evidence and Boundary |
| :--- | :--- | :--- | :--- |
| erpnext | Passed | Passed | Site creation exit 0, MariaDB healthy, admin login/identity API pass, marker retained. Replace missing MariaDB 11.8 `mysqladmin` probe with official `healthcheck.sh`. |
| superset | Passed | Passed | Web/worker healthy, init exit 0, homepage/marker pass; execute old-package default examples before current configuration. Charts/datasets/admin E2E untested. |
| akeneo | Passed | Unverified | MySQL/Elasticsearch/Web/worker normal, login page/retention pass. Build completes after narrowing repeated recursive permissions. No independent old build; current-image recreation is not full old-package migration. |
| canvas | Incomplete | Unverified | Custom build hit 600-second limit before initialization, not proof of startup failure. Requires 20 GiB; only 9.88 GiB remained. No forced build/resource expansion. |

Evidence: `build/db-regression-resume-20261105/results.json`; canceled Akeneo build retained in `akeneo-retry.json`. Its cleanup snapshot mistakenly included concurrent Superset resources; original-server-snapshot review confirmed cleanup. Preserve failures; canceled/missing-old-image cases are not passes.

Final `make test`: 558 CLI + 170 build + 15 skill = 743 passing. Test containers/project-labeled volumes removed; platform healthy, image cache/two unlabeled anonymous volumes retained, no global prune. Standard `websoft9` container absent, so skip store synchronization. No publication/downstream changes.

No external tests, other full migrations, or Owner E2E. Full old-package Canvas/Akeneo migration awaits suitable conditions.

#### 1.4.8 Narrowing Runtime Scope and Additional Airflow Tests (2026-11-05)

Recheck 13 packages' `.env`/Compose/Dockerfile/scripts against the same baseline. Exclude `variables.json`-only changes, external declarations, full E2E, and database version upgrades from deployment scope. Twelve have basic fresh evidence; Canvas has not initialized. Basic passes do not imply all required services healthy.

Because initial Airflow sidecars had only starting snapshots, check all services on the new server. PostgreSQL/Redis/API/scheduler healthy, init exit 0, homepage/version API 200, marker readable/writable. DAG processor/triggerer/worker remain unhealthy after 600 seconds. Standard main-only `app-tests` passes, but full-service regression fails; no retention/baseline migration phase. No database authentication/connectivity log matches, which does not exclude other runtime issues.

Airflow health checks were unchanged by database work; sidecar failure origin remains unconfirmed. Do not mask results with longer budgets/changed probes. Append evidence to Airflow in `build/db-regression-resume-20261105/results.json`.

For testing, remove only this round's downloaded, unreferenced, single-known-tag `frappe/erpnext:v16` image, no global prune. Test project removed, platform healthy, 10.73 GiB free/two unlabeled volumes retained; still below Canvas's 20 GiB requirement.

Remaining deployment blockers: Canvas build/init resources and three required Airflow sidecars. ThingsBoard repeated retained-volume installation reproduces in old configuration, retained as a lifecycle issue, not incidental work. Akeneo fresh/retention passes; independent old-image migration remains separate. External/metadata-only packages add no deployment work.

#### 1.4.9 Test Image Cleanup and Canvas/Airflow Completion (2026-11-05)

With user authorization, remove completed test images unreferenced by containers; retain platform, unidentified old volumes, and Canvas build cache. Free disk increases from 10.73 to 20.15 GiB. Verify the current Canvas release tag is downloadable, then pull/deploy without rebuilding source. Skip build detection only in the isolated test entry; production CLI build policy is unchanged.

| Application | Fresh Install and Retained Recreation | Same-Version Baseline Migration | Latest Evidence |
| :--- | :--- | :--- | :--- |
| canvas | Passed | Unverified, not additional work this round | Release digest `sha256:9ceb48851b7fb5023a464f156fda975f843454e3c0153b6a9550b77651fd71a0`; web/PostgreSQL healthy, jobs/Redis running, login page 200, marker retained; both phases total 198.20 seconds. |
| airflow | Passed | Passed | All required services healthy, init exit 0, homepage/version API/marker pass; full post-fix regression 403.40 seconds. |

The original Airflow probe reports `ModuleNotFoundError: airflow/celery` within approximately 0.1 seconds, not a 10-second timeout. With existing `AIRFLOW_UID=0`, the main process uses image `/entrypoint` to set Python paths while probes bypass it. Route only DAG processor/triggerer/worker probes through the same entry, retaining checks, 10-second timeout, retries, UID, image, database, and volumes. No disabled checks or database rewiring to force a pass.

Report remains `build/db-regression-resume-20261105/results.json`; retain failures in `previous_attempts`, with digests/post-fix results in latest entries. All 13 runtime-change apps have execution records. This resolves Canvas deployment/Airflow sidecar blockers, not full business E2E from other page checks. ThingsBoard old-configuration repeated installation remains separate; do not claim all 13 passed retained-volume regression.

Cleanup leaves original healthy platform containers; remove test projects/diagnostic anonymous volumes, retain two preexisting unidentified volumes, 16.41 GiB free. Standard `websoft9` absent, so skip store synchronization; no publication/downstream changes. Metadata-only packages, external tests, and independent old-build migrations remain outside scope.

#### 1.4.10 ThingsBoard Initialization Lifecycle Fix and Regression (2026-11-05)

This retains historical first-version Java/JDBC evidence; see Section 1.4.11 for the native-client approach and its results.

As confirmed, fix repeated installation already reproduced with old configuration. Upstream 4.4 installs the database once and creates demos through the web wizard. Retain default `init` for one-command deployment, adding a read-only JDBC guard to avoid reinstalling on recreation. Remove `LOAD_DEMO=true`; main waits for `init` success. Versions/volumes/declarations/credentials unchanged.

Validated image: `thingsboard/tb-node:4.4.0-latest`, digest `sha256:a34b6224a31700ee8b3f85b93eeb7398fa10e7301fc536dfe0f82b7c965ce302`, bundled app 4.4.0.2. Reuse bundled JDK/PostgreSQL JDBC without new tools/services. Run official installer only on empty public schema; existing databases require official `tb_schema_settings`, required structures, and final installer-generated `tb_cluster.cluster_id`; recheck after success. A mid-install version record alone cannot justify skipping. No cross-version upgrade; upstream owns upgrade compatibility.

| Check | Result |
| :--- | :--- |
| Empty-volume initialization | Passed: official install/recheck, init exit 0, main starts afterward, PostgreSQL healthy, homepage/setup-state pass. |
| Retained-volume recreation | Passed: init exit 0, no reinstall, marker retained. |
| Old installed configuration to current package | Passed: same image, init exit 0, homepage/setup-state/marker pass; full regression 417.13 seconds. |
| Incorrect credentials | Rejection passed: guard exit 1, SQLState 28P01, installer not called. |
| Nonempty incomplete database | Rejection passed: exit 1, installer not called. |
| Version/required tables without final cluster ID | Rejection passed: exit 1, not mistaken for completed installation. |

Historical evidence: `previous_attempts` in `build/db-regression-resume-20261105/results.json` and `thingsboard-guard-checks.json`. Initial incorrect `widget_bundle` was rejected in deployment; correct to upstream SQL `widgets_bundle` and rerun successfully. Retain failure; no suppressed errors/disabled guard. Repeated-init blocker resolved within this scope; administrator/telemetry/production license/external tests unverified, not full business E2E.

#### 1.4.11 ThingsBoard Official Compose Adaptation and Native Checks (2026-11-05)

This retains historical native SQL evidence; see Section 1.4.12 for the latest user-confirmed minimal file-marker approach.

Simplify using official [4.4 Docker Compose](https://thingsboard.io/docs/pe/installation/docker/): remove `InstallState.java`; `init` uses existing PostgreSQL-image `psql` for read-only checks. Main invokes official installation for empty databases, then starts; complete databases start directly. One `docker compose up -d`, no manual install/start sequence. `bootstrap-state` records package progress only; actual schema/cluster determines completeness. Failure stays `INSTALLING`, preventing restart-driven reinstalls.

Add internal official `tb-web-report`, report address, and `license-data:/data`; retain main image/PostgreSQL 18/database volume/credentials. Do not copy all protocol ports: retain original Web mapping, no report/database publication; withdraw extra port variables/translation keys. Add main health requiring completed install/reachable port; separately inspect wizard JSON, not HTTP 200 alone.

| Check | Native Approach Result |
| :--- | :--- |
| Fresh installation | Passed: PostgreSQL/main healthy, init exit 0, reports running, homepage/setup-state pass. |
| Retained-volume recreation | Passed: no reinstall, marker retained, homepage/setup-state pass. |
| Same-image old configuration transition | Passed after actual old installation: main healthy, marker/wizard API pass. Separate rerun 203.27 seconds, reusing earlier fresh/retention evidence. |
| Native positive/negative cases | Empty-database detection passes; incorrect credentials, nonempty incomplete schema, required tables/version without final cluster ID rejected. |

Evidence: ThingsBoard in `build/db-regression-resume-20261105/results.json` and `thingsboard-psql-guard-checks.json`. Wait for initialization, then select checks from deployed Compose; do not impose new main probes on the old package. Retain temporary installer-page/old-health-contract failures; Java rejection tests do not prove the native approach.

Test project removed, platform healthy, cached images/two unidentified volumes retained, 11.31 GiB free. Only report-process running verified, not report generation/license activation/administrator/telemetry/external/Owner E2E. No other-app/declaration-only/downstream expansion. Same-version configuration compatibility, not database/app upgrades.

Delivery: `ready-for-e2e`. No ThingsBoard `4.4.0-latest`/PostgreSQL 18 upgrades; structure/policy/declaration/shell/editor checks pass. Latest `make test`: 558 CLI + 170 build + 15 skill = 743 passing. Explicit container-type check finds no standard `websoft9`, so skip store sync; no publication/downstream changes. Owner must confirm wizard administrator creation/login/one telemetry path.

#### 1.4.12 ThingsBoard Minimal File-Marker Approach (2026-11-05)

Use the confirmed minimal persistent marker: remove `init`, read-only SQL, and `bootstrap-state`; startup only invokes official entry. Create `/data/.tb-installing` before first installation; on success write `/data/.tb-installed` and remove the in-progress directory. Existing success starts directly; failure/interruption blocks restart-driven reinstall. Reuse official `license-data:/data`, no new volumes/images/ports. Retain single-`up` fresh installation/database volume/native inputs/internal reports/main health.

No automatic old-database recognition/incomplete-schema checks. Existing databases without markers require manual installation-completeness/connection confirmation before creating success markers; commands are in the app README. Back up/restore database and `license-data` together; reconfirm markers after database/datasource changes. File existence does not prove live connectivity/schema completeness/upgrades. This accepted simplification does not inherit SQL automatic-old-database compatibility conclusions.

| Check | File-Marker Result |
| :--- | :--- |
| Fresh installation/retained recreation | Remote pass, both phases 230.02 seconds; main/PostgreSQL healthy, reports running, homepage/setup-state pass. |
| Persistence/install skipping | Database/success markers retained; recreation logs show no installer invocation; in-progress directory removed. |
| Script behavior | Actual script with mocked official entry tests fresh/recreation/existing markers/failure/interruption. Preserve failure exits, no success marker, retry does not invoke installer. Not actual incomplete-database detection. |
| Static gates | Six targeted ThingsBoard tests/shell syntax/structure/policy/version/declaration gates pass; actual Compose parsing/deployment pass. |

Evidence: `build/db-regression-resume-20261105/thingsboard-file-marker-checks.json`. Retain SQL reports as history, not replacement/proof of this approach. Test containers/project volumes removed, platform healthy, original containers/cache retained, 11.30 GiB free. No external support/automatic old migration/other deployments/downstream changes; administrator/telemetry/reports/license/Owner E2E unverified.

Delivery: `ready-for-e2e`, no app/database upgrades. Latest `make test`: 562 CLI + 170 build + 15 skill = 747 passing, editor diagnostics clean; no blocking log-keyword matches after retained recreation. Only original healthy platform containers remain, two original volumes retained. No standard `websoft9`, skip store sync; Owner confirms administrator creation/login/one telemetry path.

## 2. Fields and Reference Rules

### 2.1 Application Declarations

Use one `database[]` entry per independent database dependency; multiple names/accounts/protocol endpoints on one instance are not separate instances. Without in-scope dependencies, do not add product self-descriptive `database` fields.

| Field | Type | Rule |
| :--- | :--- | :--- |
| `id` | `string` | Required, component identifier unique within the app |
| `providers` | `array` | Required, in-scope connection options, not the instance's current selection |
| `providers[].type` | `string` | `internal` or `external` |
| `providers[].service` | `string` | Required internally, actual Compose database service name |
| `providers[].driver` | `string` | Required internally, engine key in the type dictionary |
| `providers[].drivers` | `array<string>` | Required externally, only supported engines expressible through mappings |
| `name` | `array<string>` | Optional, database-name constants or `${VAR}` sources; arrays even for one database |
| `users` | `array<object>` | Optional, entries require `user`, with optional `password`/`usage` |
| `datasource` | `object` | Required externally, optional internally; maps native app variable names to connection-property expressions |

**Inherit whole fields only**: omitted `name`/`users` inherit the type dictionary; explicit fields replace it entirely, without appending/index merging/username matching. `name: []`/`users: []` declare no such information, not absence of actual databases/accounts.

In `name`/`users`, `${VAR}` identifies environment sources and plain strings constants, without `env.` prefixes. Confirm sources against service `environment`/`env_file`/command interpolation/existing configuration; no unconditional project `.env` fallback for missing values.

### 2.2 Connection Property Labels

These expressions apply only to `datasource` and dictionary `url`, not environment templates:

| Expression | Meaning |
| :--- | :--- |
| `${host}` | Internal service address or external host, not automatically public |
| `${port}` | Engine-default reference or external port; default does not prove actual listener |
| `${name}` | Effective database-name source label, no selection/array concatenation/automatic URL expansion |
| `${users[*].user}` | Username source label in effective account objects, not account selection |
| `${users[*].password}` | Password source in the same object, not ordered pairing of independent queries |
| `${url}` | Driver template, not guaranteed complete authentication/protocol/app parameters |

Account labels borrow JSONPath notation without selection/write/reverse-parsing capabilities. Internal sources belong to the same account object; external properties belong to the same connection. Do not select external credentials using internal accounts. `usage` is not a filter.

`datasource` can combine properties/protocol prefixes/fixed parameters; it declares correspondence, not reads/assignments. Websoft9 implements Section 5 consumption; consumers own forms/protocol parsing/encoding/escaping/IPv6 handling.

### 2.3 Accounts and Display

| `usage` Enum | Display | Meaning |
| :--- | :--- | :--- |
| `application` | Application connection | Account actually used at runtime |
| `initialization` | Initialization | App initialization/database creation/grants, not generic database-image startup |
| `administration` | Database administration | Account provided for user database maintenance |

`usage` is optional; when supplied, a nonempty unique enum array allowing multiple values. Inherit matching general usages/sources; otherwise replace all `users`. Missing effective usage displays "Usage not declared", not inference from root/permissions/position. Metadata stores English enums; frontend localizes labels.

Using only a business account does not require hiding administration accounts. WordPress can inherit MySQL business/admin accounts without redeclaration. To display one account, configure only root, or represent multiple business accounts, replace with the complete object array; no new account IDs, `role`, or named outer structures.

| Special Value or Information Gap | Display Handling |
| :--- | :--- |
| `password: ""` | Explicitly empty password |
| Omitted `password` or unresolved source | Unknown password, not no authentication |
| Confirmed unauthenticated package | `users: []` may omit accounts; missing variables do not prove no authentication |
| Unavailable name/credential | Omit unknown items, not `${VAR}`/empty strings/guesses; continue displaying known information |

List names under one component; pair account fields within each object. Package/initialization configuration sources do not guarantee current persisted existence/valid credentials/unchanged permissions.

## 3. General Type Definitions

Keep one standard source set per engine, no candidate-variable fallbacks. `images` identifies image families; declared `internal.driver` determines the engine, including compatible images. `host` stays empty; actual host comes from services/external inputs. `port` is numeric.

General examples follow. Check MySQL/MariaDB default usages per app; omit other usages without reliable general applicability:

```json
{
  "postgresql": {
    "images": ["postgres", "pgvector", "paradedb", "timescale", "supabase/postgres"],
    "host": "", "port": 5432,
    "url": "postgres://${users[*].user}:${users[*].password}@${host}:${port}/${name}",
    "name": ["${POSTGRES_DB}"],
    "users": [{"user": "${POSTGRES_USER}", "password": "${POSTGRES_PASSWORD}"}]
  },
  "mysql": {
    "images": ["mysql"],
    "host": "", "port": 3306,
    "url": "mysql://${users[*].user}:${users[*].password}@${host}:${port}/${name}",
    "name": ["${MYSQL_DATABASE}"],
    "users": [
      {"user": "root", "password": "${MYSQL_ROOT_PASSWORD}", "usage": ["administration"]},
      {"user": "${MYSQL_USER}", "password": "${MYSQL_PASSWORD}", "usage": ["application"]}
    ]
  },
  "mariadb": {
    "images": ["mariadb"],
    "host": "", "port": 3306,
    "url": "mysql://${users[*].user}:${users[*].password}@${host}:${port}/${name}",
    "name": ["${MARIADB_DATABASE}"],
    "users": [
      {"user": "root", "password": "${MARIADB_ROOT_PASSWORD}", "usage": ["administration"]},
      {"user": "${MARIADB_USER}", "password": "${MARIADB_PASSWORD}", "usage": ["application"]}
    ]
  },
  "mongodb": {
    "images": ["mongo"],
    "host": "", "port": 27017,
    "url": "mongodb://${users[*].user}:${users[*].password}@${host}:${port}/${name}",
    "name": ["${MONGO_INITDB_DATABASE}"],
    "users": [{"user": "${MONGO_INITDB_ROOT_USERNAME}", "password": "${MONGO_INITDB_ROOT_PASSWORD}"}]
  },
  "redis": {
    "images": ["redis", "valkey"],
    "host": "", "port": 6379,
    "url": "redis://:${users[*].password}@${host}:${port}",
    "users": [{"user": "default", "password": "${REDIS_PASSWORD}"}]
  },
  "clickhouse": {
    "images": ["clickhouse"],
    "host": "", "port": 8123,
    "url": "http://${host}:${port}",
    "name": ["${CLICKHOUSE_DB}"],
    "users": [{"user": "${CLICKHOUSE_USER}", "password": "${CLICKHOUSE_PASSWORD}"}]
  },
  "couchdb": {
    "images": ["couchdb", "budibase/database"],
    "host": "", "port": 5984,
    "url": "http://${users[*].user}:${users[*].password}@${host}:${port}",
    "users": [{"user": "${COUCHDB_USER}", "password": "${COUCHDB_PASSWORD}"}]
  },
  "solr": {
    "images": ["solr", "ckan/ckan-solr"],
    "host": "", "port": 8983,
    "url": "http://${host}:${port}/solr",
    "name": [], "users": []
  },
  "elasticsearch": {
    "images": ["elasticsearch", "docker.elastic.co/elasticsearch/elasticsearch"],
    "host": "", "port": 9200,
    "url": "http://${host}:${port}",
    "name": [], "users": []
  },
  "meilisearch": {
    "images": ["getmeili/meilisearch"],
    "host": "", "port": 7700,
    "url": "http://${host}:${port}",
    "name": [], "users": []
  },
  "chroma": {
    "images": ["chromadb/chroma"],
    "host": "", "port": 8000,
    "url": "http://${host}:${port}",
    "name": [], "users": []
  },
  "weaviate": {
    "images": ["semitechnologies/weaviate"],
    "host": "", "port": 8080,
    "url": "http://${host}:${port}",
    "name": [], "users": []
  },
  "opensearch": {
    "images": ["opensearchproject/opensearch", "wazuh/wazuh-indexer"],
    "host": "", "port": 9200,
    "url": "https://${host}:${port}",
    "name": [], "users": []
  }
}
```

Add reliable general definitions in the same structure for other database/search/cache engines, without misidentifying them as listed engines. Redis `REDIS_PASSWORD` is a source convention, not automatic official-image authentication; override according to actual package commands.

Solr/Elasticsearch/Meilisearch/Chroma/Weaviate/OpenSearch have no reusable general name/credential sources; empty arrays do not prove no authentication. Override actual core/index/authentication sources, not API keys as account passwords. HTTP/HTTPS URLs/ports are defaults, not actual TLS/security/listeners. Confirm Wazuh HTTPS from mounted OpenSearch configuration, not other products' examples. New types describe dependencies, not database/search-product self-descriptions.

## 4. Cases and Configuration Examples

These cases cover `.env` and `docker-compose.yml` in all 143 packages under `apps/`, excluding `archive/`. Multiple cases may apply to one app; combine their handling.

Connection/source classifications are not an external-support list. Establish internal-only boundaries under Sections 1.3/4.9 first; expressible formats/native variables do not justify adding complex-app external support.

Examples use root `database`; app names remain outside code blocks, not metadata fields. "Field override fragment" examples show differences only; merge them into existing `database[]` entries, not as complete entries.

### 4.1 Standard Mappings: Combined Host/Port, Separate Fields, Full URL/JDBC

- **Applications**:
  - **Combined host/port**: `wordpress`, `wordpresspro`, `woocommerce` (`WORDPRESS_DB_HOST`, etc.).
  - **Separate fields**: `activepieces`, `akeneo`, `canvas`, `chatwoot`, `dify`, `directus`, `dolibarr`, `espocrm`, `ghost`, `kong`, `mautic`, `metabase`, `moodle`, `prestashop`, `redmine`, `seafile`, `semaphoreui`, `superset`, `typo3`, `xwiki`, `zammad`, `zentao`, `zulip`.
  - **Full URL / DSN / JDBC**: `affine`, `ckan`, `graylog`, `inngest`, `jitsu`, `librechat`, `litellm`, `lobehub`, `mattermost`, `sonarqube`, `thingsboard`, `umami`, `vaultwarden`.
  - **Fixed driver/dialect variables**: `activepieces` (`AP_DB_TYPE`), `directus` (`DB_CLIENT`), `ghost` (`database__client`), `kong` (`KONG_DATABASE`), `matomo` (`MATOMO_DATABASE_ADAPTER`), `mattermost` (`MM_SQLSETTINGS_DRIVERNAME`), `metabase` (`MB_DB_TYPE`), `moodle` (`MOODLE_DATABASE_TYPE`), `semaphoreui` (`SEMAPHORE_DB_DIALECT`), `sonarqube` and `thingsboard` (JDBC), `superset` (`DATABASE_DIALECT`), `typo3` (`TYPO3_DB_DRIVER`), `umami` (`DATABASE_TYPE`).
- **Handling**:
  1. Omit `name`/`users` to inherit Section 3 definitions when internal sources match.
  2. Write `datasource` expressions against native variables; retain fixed driver values in `.env`, outside `datasource`.
  3. Set service (`internal.service`), internal driver (`internal.driver`), and external drivers (`external.drivers`) from actual package configuration:

`wordpress`: Combined host/port.

```json
{
    "database": [{
      "id": "rds",
      "providers": [
        {"type": "internal", "service": "mysql", "driver": "mysql"},
        {"type": "external", "drivers": ["mysql", "mariadb"]}
      ],
      "datasource": {
        "WORDPRESS_DB_HOST": "${host}:${port}",
        "WORDPRESS_DB_NAME": "${name}",
        "WORDPRESS_DB_USER": "${users[*].user}",
        "WORDPRESS_DB_PASSWORD": "${users[*].password}"
      }
    }]
}
```

`mautic`: Separate fields.

```json
{
    "database": [{
      "id": "rds",
      "providers": [
        {"type": "internal", "service": "db", "driver": "mysql"},
        {"type": "external", "drivers": ["mysql", "mariadb"]}
      ],
      "datasource": {
        "MAUTIC_DB_HOST": "${host}",
        "MAUTIC_DB_PORT": "${port}",
        "MAUTIC_DB_DATABASE": "${name}",
        "MAUTIC_DB_USER": "${users[*].user}",
        "MAUTIC_DB_PASSWORD": "${users[*].password}"
      }
    }]
}
```

`mattermost`: URL with fixed parameters.

```json
{
    "database": [{
      "id": "postgres",
      "providers": [
        {"type": "internal", "service": "postgres", "driver": "postgresql"},
        {"type": "external", "drivers": ["postgresql"]}
      ],
      "users": [
        {"user": "${POSTGRES_USER}", "password": "${W9_RCODE}", "usage": ["application", "administration"]}
      ],
      "datasource": {
        "MM_SQLSETTINGS_DATASOURCE": "${url}?sslmode=disable&connect_timeout=10"
      }
    }]
}
```

`affine`: Fixed protocol prefix.

```json
{
    "database": [{
      "id": "postgres",
      "providers": [
        {"type": "internal", "service": "postgres", "driver": "postgresql"},
        {"type": "external", "drivers": ["postgresql"]}
      ],
      "datasource": {
        "DATABASE_URL": "postgresql://${users[*].user}:${users[*].password}@${host}:${port}/${name}"
      }
    }]
}
```

`sonarqube`: JDBC URL and account supplied separately.

```json
{
    "database": [{
      "id": "postgres",
      "providers": [
        {"type": "internal", "service": "db", "driver": "postgresql"},
        {"type": "external", "drivers": ["postgresql"]}
      ],
      "datasource": {
        "SONAR_JDBC_URL": "jdbc:postgresql://${host}:${port}/${name}",
        "SONAR_JDBC_USERNAME": "${users[*].user}",
        "SONAR_JDBC_PASSWORD": "${users[*].password}"
      }
    }]
}
```

### 4.2 Fixed Compose Connection Inputs or Coupled Database Initialization

- **Applications**:
  - **Fixed Compose `environment` inputs**: `nextcloud`, `matomo`, `librechat`, `thingsboard`, `dify`; some paths in `airflow`, `budibase`, `jitsu`, `erpnext`, `supabase`.
  - **Database `environment` directly references app inputs**: `activepieces`, `akeneo`, `canvas`, `kong`, `superset`, `thingsboard`, `dify`.
- **Handling**:
  1. For internal information only, trace existing `environment`/`env_file`/commands/scripts without rewiring/decoupling. Sections 1.3/4.9 exclude complex-app external support.
  2. Only for explicitly external-capable connections: fixed Compose `environment` overrides `env_file`, so `.env` edits alone cannot work. Move native inputs into project `.env` with same-name references. External inputs must not rewrite database initialization. Otherwise omit `external`, without blocking internal declarations.
  3. For example, declare `nextcloud` defaults in `.env`:

```dotenv
MYSQL_PASSWORD=${W9_POWER_PASSWORD}
MYSQL_DATABASE=nextcloud
MYSQL_USER=nextcloud
MYSQL_HOST=${W9_ID}-mysql
```

App services reference same-name variables while `db` retains independent initialization:

```yaml
services:
  nextcloud:
    env_file: .env
    environment:
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_HOST: ${MYSQL_HOST}
  db:
    environment:
      MYSQL_DATABASE: nextcloud
      MYSQL_USER: nextcloud
      MYSQL_PASSWORD: ${W9_POWER_PASSWORD}
      MYSQL_ROOT_PASSWORD: ${W9_POWER_PASSWORD}
```

### 4.3 Multiple App Services, Workers, or Initialization Containers Share a Database

- **Applications**: `activepieces`, `affine`, `airflow`, `akeneo`, `budibase`, `canvas`, `chatwoot`, `ckan`, `dify`, `erpnext`, `espocrm`, `graylog`, `jitsu`, `kong`, `langfuse`, `librechat`, `mautic`, `supabase`, `superset`, `thingsboard`, `woocommerce`, `wordpresspro`, `zammad`.
- **Handling**:
  1. One `database[]` component per database service, not per consumer. For example, `budibase` app/worker/proxy share `couchdb-service`; different URL purposes still describe one `couchdb`.
  Multiple consumers alone neither define complexity nor require external support/rewiring; trace internal information from existing configuration.
  2. For external wiring, check all web/worker/cron/migration/init/bootstrap containers receive `datasource` variables through `env_file: .env` or same-name `environment`, e.g. `thingsboard` `init` and `kong` `kong-migrations`.

### 4.4 Primary Relational Database and Redis (Cache vs Queue/Broker)

- **Applications**:
  - **Confirmed Redis cache**: `wordpresspro` (object cache), `seafile` (`CACHE_PROVIDER=redis`), `directus` (cache), `superset` (also Celery).
  - **Redis queues/tasks or usage pending confirmation**: `airflow` (Celery broker), `chatwoot` (Sidekiq), `activepieces`, `affine`, `canvas`, `inngest`, `lobehub`.
  - **Two independent Redis instances**: `erpnext` (`redis-cache` and `redis-queue`).
- **Handling**:
  1. Separate primary database/Redis `database[]` entries; declare two for `erpnext` `redis-cache`/`redis-queue`.
  2. Redis coexistence neither excludes nor requires primary external support; first satisfy Section 1.3. Where explicitly supported, primary can declare `internal` + `external` + `datasource`; keep Redis `internal` and existing dependencies/persistence. Not all components need externalization:

```json
{
  "database": [
    {
      "id": "mysql",
      "providers": [
        {"type": "internal", "service": "mysql", "driver": "mysql"},
        {"type": "external", "drivers": ["mysql", "mariadb"]}
      ],
      "datasource": {
        "WORDPRESS_DB_HOST": "${host}:${port}",
        "WORDPRESS_DB_NAME": "${name}",
        "WORDPRESS_DB_USER": "${users[*].user}",
        "WORDPRESS_DB_PASSWORD": "${users[*].password}"
      }
    },
    {
      "id": "redis",
      "providers": [
        {"type": "internal", "service": "redis", "driver": "redis"}
      ],
      "users": []
    }
  ]
}
```

### 4.5 Multiple Database Names in One Instance

- **Applications**: `seafile` (three business databases), `ckan` (primary `ckandb`/`datastore`), `dify` (primary `dify`/plugin `dify_plugin`), `supabase` (`postgres`/management `_supabase`), `superset` (`superset`/example `examples`).
- **Handling**:
  1. Do not split one container into multiple instances; list all known names as variable references/constants in a `name` string array.
  2. Frontend lists names under the same component, independently omitting unresolved entries:

```json
{
  "database": [{
    "id": "mariadb",
    "providers": [
      {"type": "internal", "service": "db", "driver": "mariadb"},
      {"type": "external", "drivers": ["mariadb", "mysql"]}
    ],
    "name": [
      "${SEAFILE_MYSQL_DB_CCNET_DB_NAME}",
      "${SEAFILE_MYSQL_DB_SEAFILE_DB_NAME}",
      "${SEAFILE_MYSQL_DB_SEAHUB_DB_NAME}"
    ],
    "users": [
      {"user": "root", "password": "${INIT_SEAFILE_MYSQL_ROOT_PASSWORD}", "usage": ["initialization", "administration"]},
      {"user": "${SEAFILE_MYSQL_DB_USER}", "password": "${SEAFILE_MYSQL_DB_PASSWORD}", "usage": ["application"]}
    ],
    "datasource": {
      "SEAFILE_MYSQL_DB_HOST": "${host}",
      "SEAFILE_MYSQL_DB_PORT": "${port}",
      "SEAFILE_MYSQL_DB_USER": "${users[*].user}",
      "SEAFILE_MYSQL_DB_PASSWORD": "${users[*].password}"
    }
  }]
}
```

### 4.6 Dynamic Databases or Site Creation (Runtime Database Names)

- **Applications**: `odoo`, `erpnext`.
- **Handling**:
  1. `odoo`: Internally inherit `postgresql` default names/accounts; external `datasource` maps only host/port/user/password, not `${name}`. Retain internal/external support.
  2. `erpnext`: Internal `mariadb` configures only `MYSQL_ROOT_PASSWORD`; site names/business accounts are runtime-generated. Declare `"name": []` and only known `root`, without guessing names:

`odoo`: No database-name connection input.

```json
{
  "database": [{
    "id": "postgres",
    "providers": [
      {"type": "internal", "service": "postgresql", "driver": "postgresql"},
      {"type": "external", "drivers": ["postgresql"]}
    ],
    "datasource": {
      "HOST": "${host}",
      "PORT": "${port}",
      "USER": "${users[*].user}",
      "PASSWORD": "${users[*].password}"
    }
  }]
}
```

`erpnext`: Only known initialization account.

```json
{
  "database": [{
    "id": "mariadb",
    "providers": [
      {"type": "internal", "service": "mariadb", "driver": "mariadb"}
    ],
    "name": [],
    "users": [
      {"user": "root", "password": "${MYSQL_ROOT_PASSWORD}", "usage": ["initialization", "administration"]}
    ]
  }]
}
```

### 4.7 Nonstandard Sources, Separate Initialization/Business Accounts, Root-Only, No Authentication

- **Applications**:
  - **MariaDB with `MYSQL_*` variables**: `moodle`, `vaultwarden`, `erpnext`, `phpmyadmin`, `seafile`.
  - **Passwords from `W9_RCODE`**: `umami`, `vaultwarden`, `mattermost`, `zammad`.
  - **Separate initialization superuser/business accounts (script-created)**: `umami`, `zammad`.
  - **Multiple business roles**: `ckan` (`ckan_default`, `datastore_write`, `datastore_read`), `supabase` (multiple service roles).
  - **Root-only configuration**: `zentao`, `erpnext`, `phpmyadmin`, `mysql`, `mariadb`.
  - **Confirmed no authentication**: Internal MongoDB in `librechat`/`graylog`; internal Redis in `activepieces`, `affine`, `airflow`, `canvas`, `chatwoot`, `ckan`, `directus`, `erpnext`, `inngest`, `lobehub`, `superset`, `wordpresspro`, `zammad`.
- **Handling**:
  1. Replace whole `name` and/or `users` fields where sources differ from Section 3.
  2. Retain actual password variables (e.g. `${W9_RCODE}`)/default constants (e.g. `dify` `"postgres"`), not unauthorized `${W9_POWER_PASSWORD}` substitution.
  3. Override confirmed unauthenticated services with `"users": []`. Missing variables with default authentication require omitted unknown fields, not `users: []`:

`vaultwarden`: MariaDB `MYSQL_*` sources, field override fragment.

```json
{
  "database": [{
    "name": ["${MYSQL_DATABASE}"],
    "users": [
      {"user": "root", "password": "${MYSQL_ROOT_PASSWORD}", "usage": ["administration"]},
      {"user": "${MYSQL_USER}", "password": "${MYSQL_PASSWORD}", "usage": ["application"]}
    ]
  }]
}
```

`umami`: Separate initialization/business accounts, field override fragment.

```json
{
  "database": [{
    "users": [
      {"user": "${POSTGRES_USER}", "password": "${POSTGRES_PASSWORD}", "usage": ["initialization", "administration"]},
      {"user": "umami", "password": "${W9_RCODE}", "usage": ["application"]}
    ]
  }]
}
```

`ckan`: Multiple business accounts, field override fragment.

```json
{
  "database": [{
    "name": ["${CKAN_POSTGRES_DB}", "${CKAN_DATASTORE_POSTGRES_DB}"],
    "users": [
      {"user": "${POSTGRES_USER}", "password": "${POSTGRES_PASSWORD}", "usage": ["initialization", "administration"]},
      {"user": "${CKAN_POSTGRES_USER}", "password": "${CKAN_POSTGRES_USER_PWD}", "usage": ["application"]},
      {"user": "${CKAN_DATASTORE_POSTGRES_WRITE_USER}", "password": "${CKAN_DATASTORE_POSTGRES_WRITE_PWD}", "usage": ["application"]},
      {"user": "${CKAN_DATASTORE_POSTGRES_READ_USER}", "password": "${CKAN_DATASTORE_POSTGRES_READ_PWD}", "usage": ["application"]}
    ]
  }]
}
```

`zentao`: Root-only, field override fragment.

```json
{
  "database": [{
    "users": [
      {"user": "root", "password": "${MYSQL_ROOT_PASSWORD}", "usage": ["application", "administration"]}
    ]
  }]
}
```

`librechat`: Confirmed unauthenticated MongoDB, field override fragment.

```json
{
  "database": [{
    "name": ["LibreChat"],
    "users": []
  }]
}
```

### 4.8 Passwords from Startup Command Interpolation (Not Standard Database Environment)

- **Applications**: Redis in `langfuse` (`--requirepass ${REDIS_AUTH}`); `budibase`, `dify`, `seafile`, `zulip` (`--requirepass ${REDIS_PASSWORD}`).
- **Handling**:
  Official Redis does not enable authentication from environment variables alone; verify `docker-compose.yml` `command` and override `users` with actual interpolation sources:

`langfuse`: Redis field override fragment.

```json
{
  "database": [{
    "users": [
      {"user": "default", "password": "${REDIS_AUTH}", "usage": ["application"]}
    ]
  }]
}
```

### 4.9 `internal` Only (Wizards, Internal-Only Multiple Stores, Clients with Bundled Databases)

- **Applications**:
  - **Wizard connection inputs without environment wiring**: `drupal`, `nopcommerce`, `teamcity`.
  - **Complex-app internal information only**: This round confirms `supabase`, `erpnext`, `dify`, `budibase`, `jitsu`, `librechat`, `graylog`; retain `langfuse`'s three internal components. Known/unknown sources are in Section 1.3; no external support or forced runtime changes for completeness.
  - **Other confirmed internal-only components**: Retain existing search/auxiliary scope for `akeneo`, `ckan`, `wazuh`, `zammad`, `zulip`. Do not expand/narrow existing primary declarations or infer whole-package external support from native variables/one component.
  - **Management clients with optional databases**: `phpmyadmin` (only bundled MariaDB under profile `db`, not the client as a database).
- **Handling**:
  Keep only `internal` providers with actual package services/drivers, omit `external`; `datasource` is optional, with no new mappings/runtime variables just for reading. Override nonstandard `name/users` as needed and trace existing sources, without requiring initialization separation. Unknown components/fields do not block known information. Retain reliable wizard/client inputs without implying external support:

`drupal`: Wizard-configured connection.

```json
{
  "database": [{
    "id": "mysql",
    "providers": [
      {"type": "internal", "service": "mysql", "driver": "mysql"}
    ]
  }]
}
```

`langfuse`: Three internal components only in this phase.

```json
{
  "database": [
    {
      "id": "postgres",
      "providers": [{"type": "internal", "service": "postgres", "driver": "postgresql"}]
    },
    {
      "id": "clickhouse",
      "providers": [{"type": "internal", "service": "clickhouse", "driver": "clickhouse"}]
    },
    {
      "id": "redis",
      "providers": [{"type": "internal", "service": "redis", "driver": "redis"}],
      "users": [
        {"user": "default", "password": "${REDIS_AUTH}", "usage": ["application"]}
      ]
    }
  ]
}
```

`phpmyadmin`: Retain optional database, move fixed root password into `.env`. Implemented in runtime wiring batch two; profile remains disabled by default, deployment unverified at that stage.

Retain existing host/port in `.env`, adding a password source:

```dotenv
MYSQL_ROOT_PASSWORD=${W9_POWER_PASSWORD}
PMA_HOST=mysql
PMA_PORT=3306
```

Compose fragment: `phpmyadmin` receives `PMA_HOST/PMA_PORT` via `env_file`; `db` references the password, retains profile, and adds `mysql` alias so existing `PMA_HOST=mysql` resolves to the database.

```yaml
services:
  phpmyadmin:
    env_file: .env
  db:
    env_file: .env
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
    profiles:
      - db
    networks:
      default:
        aliases:
          - mysql
```

Declare actual `db` service/`mariadb` driver, no fixed database name, root for administration. `datasource` records existing host/port, not root initialization password as client login input or proof the optional database is started.

```json
{
  "database": [{
    "id": "mariadb",
    "providers": [
      {"type": "internal", "service": "db", "driver": "mariadb"}
    ],
    "name": [],
    "users": [
      {"user": "root", "password": "${MYSQL_ROOT_PASSWORD}", "usage": ["administration"]}
    ],
    "datasource": {
      "PMA_HOST": "${host}",
      "PMA_PORT": "${port}"
    }
  }]
}
```

### 4.10 Runtime Scaffolds with Optional `external` Only

- **Applications**: `django`, `laravel`, `nextjs`, `springboot`.
- **Handling**:
  Without internal containers, declare only `external` providers mapping `DATABASE_URL`. When `DATABASE_URL` is unset, display no assumed database and do not misrepresent SQLite fallback as external relational storage:

```json
{
  "database": [{
    "id": "rds",
    "providers": [
      {"type": "external", "drivers": ["postgresql", "mysql", "mariadb"]}
    ],
    "datasource": {
      "DATABASE_URL": "${url}"
    }
  }]
}
```

### 4.11 Exclusions and Misclassification Risks (Database Products, SQLite, etcd, API Keys, Internal Storage, Similar Service Names)

- **Applications**:
  - **Database/search/vector products themselves (24)**: `arangodb`, `chroma`, `clickhouse`, `couchbase`, `couchdb`, `elasticsearch`, `influxdb`, `mariadb`, `meilisearch`, `milvus`, `mongodb`, `mysql`, `neo4j`, `opensearch`, `oracle`, `pgvector`, `postgresql`, `qdrant`, `redis`, `sqlserver`, `timescaledb`, `typesense`, `vespa`, `weaviate`. No primary-product `database` self-description; assess independent dependencies by role.
  - **SQLite/etcd (direct exclusions)**: SQLite apps including `mlflow`, `strapi`, `umbraco`, `pocketbase`, `uptimekuma`, `anythingllm`, `jupyterhub`, `hermes`; `milvus` `etcd`.
  - **Management clients without independent database services**: No `database` for `cloudbeaver`, `pgadmin`, `redisinsight`; clients are not database instances.
  - **Cache scope pending confirmation**: Independent `zammad` `zammad-memcached` and `zulip` `memcached` exist but inclusion remains undecided. No declarations yet, nor Redis type/authentication assumptions.
  - **App-managed/image-internal storage without independent standard services**: `airbyte`, `gitea`, `gitlab`, `grafana`, `homeassistant`, `jfrog`, `jihu`, `keycloak`, `n8n`, `onlyofficedocs`, `openwebui` (only explicit Compose `chroma` may separately declare `internal`), `rundeck`, `youtrack`.
  - **API-key/anonymous components used by other apps**: `typesense`, `meilisearch`, `weaviate`; this does not include the products themselves as dependencies.
  - **Backup/init/management containers with database images or similar names**: `postgresql` `database-backup-service`, `milvus` `milvus-volume-init`/`minio`, `opensearch` `opensearch-dashboards`, `typesense` `docsearch-scraper`, `supabase` `meta/rest/supavisor`, `librechat` `admin-panel` (image path contains `clickhouse`, not a ClickHouse service).
- **Handling**:
  1. Exclude database/search/vector products themselves, SQLite, etcd, object storage (MinIO/RustFS), queues (RabbitMQ/Kafka/Redpanda), and unexposed image-internal databases from `database[]`; product information does not reuse dependency declarations.
  2. Backup/init/admin UI/pool/API containers are not database instances.
  3. Internal search/vector components with only API-key/anonymous access use `"users": []`; never put API keys in `password`.
  4. Other unlisted app/gateway/tool packages have no declarations; do not invent configuration.

## 5. Websoft9 Consumption Workflow

This defines consumer behavior, not proof Websoft9 has implemented it. `database[]` describes facts/mappings only, not current selections/switching history/live credentials, and does not directly edit configuration/connect databases/start or stop services.

### 5.1 Reading and Displaying Data

1. **Separate declarations from instance configuration**: Read `database[]` and the dictionary. For deployed apps, use instance project `.env`, Compose, referenced environment files, and existing configuration, not repository defaults. Undeployed defaults are not current connections. Evaluate in deployment interpolation context, excluding unrelated same-name consumer-process variables.
2. **Determine components/definitions**: Internally locate actual `service`, load `driver` definitions, and wholly inherit/replace `name/users` under Section 2.1. Externally use known inputs/actual app connection configuration, not internal accounts. `providers` alone does not prove the active connection.
3. **Resolve sources**: Evaluate dictionary references in the database service's effective environment; app overrides against verified package sources. Apply Compose interpolation, then merge `env_file`/`environment` under Compose rules. Separately trace project command interpolation/container expansion/init-script variables. Do not scan other services/project `.env` for same-name fallbacks; unclear sources remain unknown.
4. **Prepare display**: Use known reachable instance-network service/container names or aliases, not assumed public addresses. Prefer confirmed container listeners, never host-published ports as internal ports; dictionary-only ports are default references. List names individually, pair accounts by object, omit unknowns under Section 2.3. Passwords appear only in authorized display workflows, not ordinary logs.

| Application Case | How Websoft9 Reads Data |
| :--- | :--- |
| `wordpress`: Standard environment | From `internal.service=mysql`, read effective `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_ROOT_PASSWORD`. Host comes from instance networking; app `WORDPRESS_DB_*` cross-checks connections, not root sources. |
| `langfuse`: Redis command interpolation | Trace `redis` `--requirepass ${REDIS_AUTH}` in project interpolation context. `REDIS_AUTH` is not environment-injected; project interpolation is not container environment. Account override uses `default/REDIS_AUTH`, not dictionary `REDIS_PASSWORD`. |
| `seafile`: Separate app/initialization sources | Read three names/business account from app-received `SEAFILE_MYSQL_DB_*`; trace root via `db` `MYSQL_ROOT_PASSWORD` to `INIT_SEAFILE_MYSQL_ROOT_PASSWORD`. Missing database-container business variables do not invalidate known app sources; do not cross-fill passwords. |
| `umami`: Script-created business account | Read administration account from PostgreSQL environment; init script identifies `umami` with `POSTGRES_UMAMI_PASSWORD`, traced to project `W9_RCODE`. Initialization source does not prove persisted passwords unchanged. |
| `django`, `laravel`, `nextjs`, `springboot`: Optional URL | Display known external connections only when instance `DATABASE_URL` is configured. Parse reliable fields using actual protocol; otherwise no assumed instances from `external.drivers` or SQLite fallback display. |

Read separate external fields through `datasource` correspondence. URL/DSN/JDBC-only inputs require parsers supporting the actual format, retaining protocol/app parameters. Templates are not general reverse parsers; do not guess passwords/names/drivers through simple splitting. Unreliably parsed fields stay unknown; no database queries to fill gaps.

### 5.2 Writing Application Connection Inputs

Consumer writes apply only when the package explicitly supports external connections and the user explicitly configures one; reading/displaying declarations must not write. Complex/internal-only declarations do not enable external writes or inferred writable connections. Package-maintenance wiring follows Section 4.2, separate from deployed-instance input writes.

1. **Confirm targets**: Locate the explicitly selected component/external driver and verify required mappings reach all consumers. Write only `datasource`-listed native variables in the instance project `.env`, not repository templates/dictionary/`variables.json` or separate specification-defined credential records.
2. **Generate values**: Interpret property labels from this external host/port/name/same-account credentials. `${url}` uses the driver template with required prefixes/fixed parameters. Internal `name/users` arrays are not external inputs; no first-item selection/array concatenation/internal-root fallback. Missing required inputs/unexpressible mappings must not produce incomplete writes.
3. **Serialize/verify**: Protocol-encode URL username/password/name components, then save complete values under Compose environment-file semantics. Plain passwords are not URL-encoded. Handle `$`, quotes, backslashes, and user literals versus existing `${VAR}` references; simple replacement/uniform quoting is insufficient. Before writing, verify parsed/interpolated targets match expectations; never log credential-bearing configuration.
4. **Preserve unrelated configuration**: Update only target mappings, retaining other variables/references. Do not rewrite initialization/other components/usages/declaration structure. Generate/validate all values before one configuration update; failures leave no partial writes. Consumers own instance storage/backups/recovery.
5. **Apply/recheck**: Deployment recreates receiving app containers, including workers/migration/init; ordinary `restart` does not reinject environment. Reread effective configuration; validate connectivity separately. Written inputs do not prove valid credentials/completed migration/stopped internal databases. Restore internal connections only from known original instance configuration, never guesses; declarations do not store switching history.

| Application Case | Writes and Preserved Configuration |
| :--- | :--- |
| `wordpress`: Combined host/port | Update only instance `WORDPRESS_DB_HOST/NAME/USER/PASSWORD`, combining host/port in supported format; preserve MySQL `MYSQL_*` initialization. |
| `seafile`: Multiple names/separate initialization password | Section 4.5 maps only `SEAFILE_MYSQL_DB_HOST/PORT/USER/PASSWORD`; retain three names and `INIT_SEAFILE_MYSQL_ROOT_PASSWORD`. Name changes require separate native-input configuration, not concatenated `${name}` arrays. |
| `langfuse`: Internal display only | No external mappings this phase; displayed sources do not automatically write `REDIS_AUTH`/other storage or change authentication on password reads. |
| Runtime: Full URL | Update only instance `DATABASE_URL`; existing Runtime entries convert it to app configuration. Consumers do not separately write generated Django/Laravel/Spring Boot configuration. |

Environment writes change startup configuration, not database passwords/creation/grants/migration. Fixed drivers/unmapped parameters are not automatically rewritten. If needed, use the app's configuration workflow first; current mappings alone do not necessarily complete switching.

## 6. Validation and Delivery Boundaries

Automatically validate types/references/service names/engine existence. The `users` contract below is for integration into the actual schema:

```json
{
  "type": "array",
  "items": {
    "type": "object",
    "additionalProperties": false,
    "required": ["user"],
    "properties": {
      "user": {"type": "string"},
      "password": {"type": "string"},
      "usage": {
        "type": "array", "minItems": 1, "uniqueItems": true,
        "items": {"type": "string", "enum": ["application", "initialization", "administration"]}
      }
    }
  }
}
```

- Maintainers verify sources/usages; structural validation does not prove valid credentials/external support.
- Before declaring `external`, verify project `.env` delivers required inputs to all consumers. Defer unexpressible connections without generalizing to whole-app capabilities.
- For runtime maintenance changes, first verify unchanged default internal connections, then effective external inputs without altered internal initialization; deploy under repository quality gates.
- Consumers separately implement forms/redaction/permissions/connectivity/initialization/migration/instance state/dependency or service pruning; declarations do not control them.