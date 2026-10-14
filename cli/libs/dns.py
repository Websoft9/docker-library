from __future__ import annotations

import shlex
from pathlib import Path

from libs import aliyun_rpc, credentials, http, remote
from libs.aliyun_rpc import percent_encode, sign

ALIYUN_VERSION = "2015-01-09"
ALIYUN_PROVIDER = "aliyun"
DEFAULT_PROVIDER = ALIYUN_PROVIDER
DEFAULT_ENDPOINT = "https://alidns.aliyuncs.com/"
DEFAULT_RECORD_TYPE = "A"
DEFAULT_TTL = 600
DEFAULT_LINE = "default"
LOCALHOST = "127.0.0.1"

WEBSOFT9_CLI = "websoft9"
WEBSOFT9_DOMAIN_SECTION = "domain"
WEBSOFT9_DOMAIN_KEY = "wildcard_domain"

ContainerContext = tuple[str, str, Path]

PROVIDER_KEY = "dns"
PROVIDER_ENV = "DNS_PROVIDER"
ACCESS_KEY_ID_ENV = "DNS_KEY_ID"
ACCESS_KEY_SECRET_ENV = "DNS_KEY_SECRET"
DOMAIN_ENV = "DNS_DOMAIN"
ENDPOINT_ENV = "DNS_ENDPOINT"


class DnsError(RuntimeError):
    pass


def call(
    action: str,
    params: dict[str, object],
    access_key_id: str,
    access_key_secret: str,
    endpoint: str | None = None,
) -> dict:
    if not access_key_id or not access_key_secret:
        raise DnsError(
            f"missing DNS credentials; run `make connector` and choose dns, "
            f"or set {ACCESS_KEY_ID_ENV} / {ACCESS_KEY_SECRET_ENV}"
        )
    response = http.get(
        endpoint or DEFAULT_ENDPOINT,
        params=aliyun_rpc.signed_params(action, params, access_key_id, access_key_secret, ALIYUN_VERSION),
    )
    try:
        payload = response.json()
    except ValueError as error:
        raise DnsError(f"Aliyun DNS {action} returned a non-JSON response (HTTP {response.status_code})") from error
    if not isinstance(payload, dict):
        raise DnsError(f"Aliyun DNS {action} returned an unexpected payload")
    if response.status_code >= 400 or payload.get("Code"):
        code = payload.get("Code") or response.status_code
        message = payload.get("Message") or response.reason
        detail = f"Aliyun DNS {action} failed: {code} {message}".strip()
        if str(code) == "Forbidden.RAM":
            detail += (
                "; the AccessKey lacks Alidns (Cloud DNS) permission. Attach AliyunDNSFullAccess"
                " (product Alidns / 云解析 DNS) — not Domain/域名 registration — to the RAM user,"
                " or grant alidns:DescribeDomains, alidns:DescribeDomainRecords, alidns:AddDomainRecord,"
                " alidns:UpdateDomainRecord, alidns:DeleteDomainRecord"
            )
        raise DnsError(detail)
    return payload


def _items(payload: dict, container: str, item: str) -> list[dict]:
    node = payload.get(container)
    if isinstance(node, dict):
        values = node.get(item)
    else:
        values = node
    if not values:
        return []
    if isinstance(values, dict):
        return [values]
    return list(values)


def normalize_domain(value: str) -> str:
    return value.strip().rstrip(".").lower()


def wildcard_fqdn(domain: str) -> str:
    name = normalize_domain(domain)
    if not name:
        raise ValueError(f"domain is required; pass --domain or set {DOMAIN_ENV}")
    if name.startswith("*."):
        return name
    return "*." + name


def resolve_zone(domain: str, zones: list[str]) -> tuple[str, str]:
    name = normalize_domain(domain)
    matches: list[tuple[str, str]] = []
    for zone in zones:
        candidate = normalize_domain(zone)
        if not candidate:
            continue
        if name == candidate:
            matches.append((candidate, "@"))
        elif name.endswith("." + candidate):
            matches.append((candidate, name[: -(len(candidate) + 1)]))
    if not matches:
        raise DnsError(f"domain {domain} is not managed by this Aliyun account")
    return max(matches, key=lambda item: len(item[0]))


def list_domains(access_key_id: str, access_key_secret: str, endpoint: str | None = None) -> list[str]:
    domains: list[str] = []
    page = 1
    while True:
        payload = call(
            "DescribeDomains",
            {"PageNumber": page, "PageSize": 100},
            access_key_id,
            access_key_secret,
            endpoint=endpoint,
        )
        chunk = _items(payload, "Domains", "Domain")
        domains.extend(item["DomainName"] for item in chunk if isinstance(item, dict) and item.get("DomainName"))
        total = int(payload.get("TotalCount") or 0)
        if not chunk or len(domains) >= total:
            break
        page += 1
    return domains


def find_records(
    zone: str,
    rr: str,
    record_type: str | None,
    access_key_id: str,
    access_key_secret: str,
    endpoint: str | None = None,
) -> list[dict]:
    records: list[dict] = []
    fetched = 0
    page = 1
    while True:
        payload = call(
            "DescribeDomainRecords",
            {"DomainName": zone, "PageNumber": page, "PageSize": 100},
            access_key_id,
            access_key_secret,
            endpoint=endpoint,
        )
        chunk = _items(payload, "DomainRecords", "Record")
        fetched += len(chunk)
        for record in chunk:
            if not isinstance(record, dict):
                continue
            if record.get("RR") != rr:
                continue
            if record_type and record.get("Type") != record_type:
                continue
            records.append(record)
        total = int(payload.get("TotalCount") or fetched)
        if not chunk or fetched >= total:
            break
        page += 1
    return records


def resolve_credentials(
    access_key_id: str | None = None,
    access_key_secret: str | None = None,
    env_file: str | None = None,
) -> tuple[str | None, str | None]:
    return (
        credentials.resolve_secret(ACCESS_KEY_ID_ENV, PROVIDER_KEY, access_key_id, env_file),
        credentials.resolve_secret(ACCESS_KEY_SECRET_ENV, PROVIDER_KEY, access_key_secret, env_file),
    )


def resolve_domain(explicit: str | None = None, env_file: str | None = None) -> str | None:
    return credentials.resolve_secret(DOMAIN_ENV, PROVIDER_KEY, explicit, env_file)


def resolve_provider(explicit: str | None = None, env_file: str | None = None) -> str:
    return credentials.resolve_secret(PROVIDER_ENV, PROVIDER_KEY, explicit, env_file) or DEFAULT_PROVIDER


def ensure_supported_provider(provider: str) -> None:
    if provider != ALIYUN_PROVIDER:
        raise DnsError(f"unsupported DNS provider {provider!r}; only {ALIYUN_PROVIDER} is implemented")


def resolve_endpoint(explicit: str | None = None, env_file: str | None = None) -> str:
    return credentials.resolve_secret(ENDPOINT_ENV, PROVIDER_KEY, explicit, env_file) or DEFAULT_ENDPOINT


def resolve_target_ip(target: str | None = None, ip: str | None = None, ssh_host: str | None = None) -> str:
    if ip:
        return ip
    mode = (target or remote.default_target()).lower()
    if mode == "local":
        return LOCALHOST
    if mode != "remote":
        raise ValueError(f"invalid target: {target!r}; expected local or remote")
    host = remote.ssh_host(ssh_host)
    if not host:
        raise ValueError("missing remote host; run `make remote`, pass --ssh-host, or use --target local")
    return host


def _run_container(command: list[str], ctx: ContainerContext | None):
    if ctx is None:
        return remote.run_command(command)
    host, user, secret_path = ctx
    return remote.run_ssh(host, user, secret_path, shlex.join(command))


def configure_container(
    domain: str | None,
    target: str | None = None,
    container: str | None = None,
    ssh_host: str | None = None,
    ssh_user: str | None = None,
    ssh_secret_path: str | None = None,
) -> dict:
    """Best-effort: point the Websoft9 container's wildcard_domain config at the domain.

    Does nothing when the container or its host is unreachable, and never raises.
    """
    result: dict = {"section": WEBSOFT9_DOMAIN_SECTION, "key": WEBSOFT9_DOMAIN_KEY}
    try:
        container_name = remote.appstore_container(container)
        result["container"] = container_name
        mode = (target or remote.default_target()).lower()
        ctx: ContainerContext | None = None
        if mode == "remote":
            host = remote.ssh_host(ssh_host)
            if not host:
                result.update(status="skipped", reason="missing remote host")
                return result
            user = remote.ssh_user(ssh_user)
            secret_path = remote.resolve_secret_path(ssh_secret_path)
            if not secret_path.exists():
                result.update(status="skipped", reason="missing SSH secret")
                return result
            ctx = (host, user, secret_path)
        elif mode != "local":
            result.update(status="skipped", reason=f"unsupported target: {mode}")
            return result

        probe = _run_container(["docker", "inspect", container_name], ctx)
        if probe.returncode != 0:
            result.update(status="skipped", reason="container not found")
            return result

        value = normalize_domain(domain or "")
        run = _run_container(
            [
                "docker",
                "exec",
                container_name,
                WEBSOFT9_CLI,
                "setconfig",
                "--section",
                WEBSOFT9_DOMAIN_SECTION,
                "--key",
                WEBSOFT9_DOMAIN_KEY,
                "--value",
                value,
            ],
            ctx,
        )
        if run.returncode != 0:
            result.update(status="failed", error=(run.stderr or run.stdout).strip() or "setconfig failed")
            return result
        result.update(status="updated", domain=value)
        return result
    except Exception as error:
        result.setdefault("container", container)
        result.update(status="skipped", reason=str(error))
        return result


def _bind_payload(
    domain: str | None,
    fqdn: str,
    zone: str,
    rr: str,
    record_type: str,
    ttl: int,
    value: str,
    action: str,
    record_id: str | None,
    previous: str | None,
    provider: str = ALIYUN_PROVIDER,
) -> dict:
    return {
        "provider": provider,
        "action": action,
        "domain": normalize_domain(domain or ""),
        "fqdn": fqdn,
        "zone": zone,
        "rr": rr,
        "type": record_type,
        "ttl": ttl,
        "value": value,
        "previous_value": previous,
        "record_id": record_id,
    }


def _bind_existing(
    record: dict,
    *,
    domain: str | None,
    fqdn: str,
    zone: str,
    rr: str,
    record_type: str,
    ttl: int,
    value: str,
    key_id: str,
    key_secret: str,
    endpoint: str,
    provider: str = ALIYUN_PROVIDER,
) -> dict:
    current = record.get("Value")
    if current is not None and str(current).strip() == str(value).strip():
        return _bind_payload(domain, fqdn, zone, rr, record_type, ttl, value, "unchanged", record.get("RecordId"), current, provider)

    try:
        result = call(
            "UpdateDomainRecord",
            {
                "RecordId": record.get("RecordId"),
                "RR": rr,
                "Type": record_type,
                "Value": value,
                "TTL": ttl,
                "Line": record.get("Line") or DEFAULT_LINE,
            },
            key_id,
            key_secret,
            endpoint=endpoint,
        )
    except DnsError as error:
        # Aliyun reports DomainRecordDuplicate when the requested value already
        # matches an existing record's value (including the record being updated).
        if "DomainRecordDuplicate" not in str(error):
            raise
        for item in find_records(zone, rr, record_type, key_id, key_secret, endpoint=endpoint):
            if str(item.get("Value", "")).strip() == str(value).strip():
                return _bind_payload(
                    domain, fqdn, zone, rr, record_type, ttl, value, "unchanged", item.get("RecordId"), item.get("Value"), provider
                )
        raise

    return _bind_payload(
        domain, fqdn, zone, rr, record_type, ttl, value, "updated", record.get("RecordId") or result.get("RecordId"), current, provider
    )


def bind(
    domain: str | None,
    value: str,
    access_key_id: str | None = None,
    access_key_secret: str | None = None,
    record_type: str = DEFAULT_RECORD_TYPE,
    ttl: int = DEFAULT_TTL,
    endpoint: str | None = None,
    env_file: str | None = None,
) -> dict:
    domain = resolve_domain(domain, env_file)
    provider = resolve_provider(env_file=env_file)
    ensure_supported_provider(provider)
    fqdn = wildcard_fqdn(domain or "")
    key_id, key_secret = resolve_credentials(access_key_id, access_key_secret, env_file)
    api_endpoint = resolve_endpoint(endpoint, env_file)
    zone, rr = resolve_zone(fqdn, list_domains(key_id or "", key_secret or "", endpoint=api_endpoint))
    records = find_records(zone, rr, record_type, key_id or "", key_secret or "", endpoint=api_endpoint)
    if len(records) > 1:
        raise DnsError(f"multiple {record_type} records exist for {fqdn}; remove duplicates before binding")

    shared = {
        "domain": domain,
        "fqdn": fqdn,
        "zone": zone,
        "rr": rr,
        "record_type": record_type,
        "ttl": ttl,
        "value": value,
        "key_id": key_id or "",
        "key_secret": key_secret or "",
        "endpoint": api_endpoint,
        "provider": provider,
    }

    if records:
        return _bind_existing(records[0], **shared)

    try:
        result = call(
            "AddDomainRecord",
            {
                "DomainName": zone,
                "RR": rr,
                "Type": record_type,
                "Value": value,
                "TTL": ttl,
                "Line": DEFAULT_LINE,
            },
            shared["key_id"],
            shared["key_secret"],
            endpoint=api_endpoint,
        )
    except DnsError as error:
        # Defensive: a concurrent or missed lookup can make Add collide with an
        # existing record. Fall back to updating that record instead of failing.
        if "DomainRecordDuplicate" not in str(error):
            raise
        existing = find_records(zone, rr, record_type, shared["key_id"], shared["key_secret"], endpoint=api_endpoint)
        if not existing:
            raise
        return _bind_existing(existing[0], **shared)

    return _bind_payload(
        domain, fqdn, zone, rr, record_type, ttl, value, "created", result.get("RecordId"), None, provider
    )


def delete(
    domain: str | None,
    access_key_id: str | None = None,
    access_key_secret: str | None = None,
    record_type: str = DEFAULT_RECORD_TYPE,
    endpoint: str | None = None,
    env_file: str | None = None,
) -> dict:
    domain = resolve_domain(domain, env_file)
    provider = resolve_provider(env_file=env_file)
    ensure_supported_provider(provider)
    fqdn = wildcard_fqdn(domain or "")
    key_id, key_secret = resolve_credentials(access_key_id, access_key_secret, env_file)
    api_endpoint = resolve_endpoint(endpoint, env_file)
    zone, rr = resolve_zone(fqdn, list_domains(key_id or "", key_secret or "", endpoint=api_endpoint))
    records = find_records(zone, rr, record_type, key_id or "", key_secret or "", endpoint=api_endpoint)
    if not records:
        raise DnsError(f"no {record_type} record found for {fqdn}")
    if len(records) > 1:
        raise DnsError(f"multiple {record_type} records exist for {fqdn}; refusing to delete")

    record = records[0]
    call(
        "DeleteDomainRecord",
        {"RecordId": record.get("RecordId")},
        key_id or "",
        key_secret or "",
        endpoint=api_endpoint,
    )
    return {
        "provider": provider,
        "action": "deleted",
        "domain": normalize_domain(domain or ""),
        "fqdn": fqdn,
        "zone": zone,
        "rr": rr,
        "type": record_type,
        "value": record.get("Value"),
        "record_id": record.get("RecordId"),
    }
