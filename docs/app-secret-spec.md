# Application Secret Spec

## Scope

This specification covers startup key handling in current `apps/`, not external service provisioning, database account rotation, or Docker secrets. `variables.json` declares `env.secrets` entries using either plain variable names (shape-based generation) or single-key objects from the shared rule dictionary `metadata/secret-rules.json` (`base64`, `fernet`, `jwt:<SECRET_KEY>`). `metadata/secret-rules.json` is validated by `metadata/variables.schema.json` (`$defs.secretRules`), synced by `libs appstore-sync`, and published with Appstore library artifacts alongside `metadata/database-types.json`. All secret generation and persistence are executed by the Websoft9 consumer.

The canonical declaration contract is [appstore-release-spec.md](appstore-release-spec.md#L172).

## Classification

| Class | Treatment | Examples |
|---|---|---|
| Plain random seed or list | Declare `"KEY"` in `env.secrets` | Session secret, hex encryption key, `sk-` key, comma-separated `APP_KEYS` |
| Encoded byte key | Declare `{ "KEY": "base64" }` or `{ "KEY": "fernet" }` in `env.secrets` | Semaphore UI access-key encryption, Dify/LobeHub/Supabase base64 keys, Airflow Fernet key |
| Signed JWT | Declare `{ "KEY": "jwt:<SECRET_KEY>" }` in `env.secrets` | Supabase `ANON_KEY` and `SERVICE_ROLE_KEY` signed with `JWT_SECRET` |
| Platform password | Existing implicit platform handling; no repeated declarations required | `W9_POWER_PASSWORD`, `W9_RCODE` |
| Shared secret or protocol wrapper | Reference a declared seed in `.env`; do not independently regenerate copies | CKAN `string:${CKAN_API_TOKEN_SECRET}`, Dify `CODE_EXECUTION_API_KEY=${SANDBOX_API_KEY}` |
| Container/volume-managed key | Persisted by the upstream image inside a mounted volume | Laravel `app.env`, JupyterHub cookie secret, n8n, Gitea, GitLab, Wazuh certs |
| External credential | Obtain from the provider/user; do not generate a lookalike | Cloud API token, OAuth secret, issued license |

## Shared Rule Dictionary (`metadata/secret-rules.json`)

`metadata/secret-rules.json` defines reusable generation profiles, not executable recipes or syntax templates. Each profile selects a consumer-implemented `generator` and its typed options. It is published with Appstore library artifacts (`library/metadata/secret-rules-<sha256>.json` and `library/metadata/secret-rules.json` in full packages):

```json
{
    "base64": {
        "generator": "random_bytes",
        "encoding": "base64",
        "description": "Generate random bytes of the same decoded length and encode as Base64."
    },
    "fernet": {
        "generator": "random_bytes",
        "encoding": "base64url",
        "bytes": 32,
        "description": "Generate 32 random bytes and encode as URL-safe Base64."
    },
    "jwt": {
        "generator": "jwt",
        "algorithm": "HS256",
        "description": "Update iat/exp on the default JWT payload and sign with the referenced secret."
    }
}
```

| Rule Key | Declaration in `variables.json` | Machine Parameters | Consumer Execution |
|---|---|---|---|
| *(default)* | `"KEY"` | Shape inferred from `.env` default | Regenerate same length and character classes (including comma-separated lists) |
| `base64` | `{ "KEY": "base64" }` | `generator: "random_bytes"`, `encoding: "base64"` | Decode `.env` default to get byte length $N$, generate $N$ random bytes, encode as standard Base64 |
| `fernet` | `{ "KEY": "fernet" }` | `generator: "random_bytes"`, `encoding: "base64url"`, `bytes: 32` | Generate 32 random bytes and encode as URL-safe Base64 with `=` padding |
| `jwt` | `{ "KEY": "jwt:<SECRET_KEY>" }` | `generator: "jwt"`, `algorithm: "HS256"` | Decode `.env` default JWT header/payload, update `iat`/`exp`, and sign with `<SECRET_KEY>` |

- `bytes` counts raw random bytes, not encoded characters. When omitted for `random_bytes`, the consumer uses the nonempty default template's decoded length. This is a compatibility convention for the compact application syntax, not a security guarantee: maintainers must verify each application's required length against upstream documentation.
- `encoding` selects canonical standard Base64 or URL-safe Base64, including required `=` padding. `fernet` fixes both encoding and byte length; these are not user-tunable Fernet parameters.
- `jwt` requires a variable-name argument after `:`; byte profiles take no arguments. The argument is a dependency reference, not a literal key or dotenv interpolation. `description` is documentation only and must never be parsed to execute a rule.
- JSON Schema rejects unknown profiles, generators, options, encodings, and algorithms. The dictionary must be present and valid; consumers must not silently fall back to built-in copies or ordinary random strings.
- Websoft9 must implement these generators and the object declaration syntax before packages using them are installed. Publishing the dictionary alone does not add algorithm support. Persistence, retry reuse, and rotation remain consumer responsibilities, separate from generation profiles.

This separation follows the explicit byte-count/encoding model of [Vault random bytes](https://developer.hashicorp.com/vault/api-docs/system/tools#generate-random-bytes). Fernet's fixed format follows the [Fernet key API](https://cryptography.io/en/latest/fernet/); JWT algorithm selection follows [RFC 8725 section 3.1](https://www.rfc-editor.org/rfc/rfc8725.html#section-3.1). Reusing default JWT claims and their lifetime is a repository-specific installation convention, not a general JWT requirement.

## Consumer Contract

- Read entries from `env.secrets`; platform password fields (`W9_POWER_PASSWORD`, `W9_RCODE`) present in `.env` remain implicit targets.
- Plain `"KEY"` entries preserve the `.env` template's length and character classes (alphanumeric, hex case, hyphen-separated segments, fixed `sk-` prefix, and comma-separated lists where each item has at least 12 random characters).
- `{ "KEY": "base64" }` decodes the nonempty `.env` template to determine raw byte length $N$, generates $N$ random bytes from a CSPRNG, and encodes as standard Base64. No universal minimum length is implied by the encoding.
- `{ "KEY": "fernet" }` generates 32 random bytes and encodes as URL-safe Base64 with `=` padding.
- `{ "KEY": "jwt:<SECRET_KEY>" }` decodes the `.env` default JWT header and payload, updates `iat`/`exp` preserving the template's lifetime, and signs with the resolved value of `<SECRET_KEY>`.
- Preserve `$NAME`/`${NAME}` references, including forward/partial references; reject missing/empty/cyclic references and default-expression syntax in secret references.
- Explicit user settings win, then cached values, then fresh generation. Cache is keyed by instance identity, protected by locks and atomic writes; retrying an installation reuses values. Deleting an instance clears its installation cache.
- Existing values must not be silently rotated during startup, recreation, upgrade, or restore. Cached values and instance `.env` require backup.

## Validation

Run the secret gate on any app or across all apps:

```bash
PYTHONPATH="$PWD/cli" .venv/bin/libs app-check --app <app> --gate secrets --json
```

## Acceptance

1. Validate schema, policy, shape templates, rule templates (`base64`, `fernet`, `jwt:<SECRET_KEY>`), and variable references via `libs app-check --app <app> --gate secrets`.
2. Test the consumer on temporary copies: correct formats, shared/prefixed values, retry stability, different-instance uniqueness, and no secret output.
3. Deploy changed runnable behavior, remotely when configured. Verify initialization, health, logs, actual authenticated use, and retained data/keys across recreation.
4. Keep real instance values during upgrades/restores. Validate any rotation using the app-specific procedure separately.
5. Owner validates login and a relevant business path.
