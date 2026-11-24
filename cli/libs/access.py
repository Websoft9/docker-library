from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote

import jsonschema
import yaml
from dotenv import dotenv_values

from libs.repo import repo_path


KIND_ORDER = {"ui": 0, "api": 1, "infra": 2}
CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")
VARIABLE_RE = re.compile(r"^\$\{([A-Za-z_][A-Za-z0-9_]*)\}$")
CREDENTIAL_FIELDS = {"token", "access_token", "password", "secret", "api_key", "authorization"}
VALUE_FIELDS = ("rootUrl", "host", "mappedPort")
URL_SCHEMES = frozenset({"http", "https", "ws", "wss"})
UNMANAGED_PORTS_KEY = "x-websoft9-unmanaged-ports"
W9_TOKEN_RE = re.compile(r"\b(W9_[A-Za-z0-9_]+)\b")
ENV_VAR_REF_RE = re.compile(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?")
DEPRECATED_W9_ACCESS_NAMES = frozenset({
    "W9_HTTP_PORT",
    "W9_HTTPS_PORT",
    "W9_DB_PORT",
    "W9_API_PORT",
    "W9_URL",
    "W9_URL_REPLACE",
    "W9_URL_WITH_PORT",
    "W9_ADMIN_PATH",
    "W9_LOGIN_ConnectURL",
})


def is_deprecated_w9_access_key(name: str) -> bool:
    return name in DEPRECATED_W9_ACCESS_NAMES or (name.startswith("W9_") and name.endswith("_PORT_SET"))


def _iter_yaml_strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from _iter_yaml_strings(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_yaml_strings(item)


def _find_deprecated_w9_residuals(target: Path, env: dict, compose: dict) -> list[str]:
    residuals: list[str] = []
    env_hits = sorted({
        name
        for key, value in env.items()
        for name in ([key] if is_deprecated_w9_access_key(key) else []) + [
            token for token in W9_TOKEN_RE.findall(value or "") if is_deprecated_w9_access_key(token)
        ]
    })
    if env_hits:
        residuals.append(f".env: deprecated platform access variables must be removed ({', '.join(env_hits)})")

    compose_hits = sorted({
        token
        for text in _iter_yaml_strings(compose)
        for token in W9_TOKEN_RE.findall(text)
        if is_deprecated_w9_access_key(token)
    })
    if compose_hits:
        residuals.append(
            f"docker-compose.yml: deprecated platform access variables must be removed ({', '.join(compose_hits)})"
        )

    src_dir = target / "src"
    if src_dir.is_dir():
        for path in sorted(src_dir.rglob("*")):
            if not path.is_file() or path.suffix.lower() == ".md":
                continue
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeError):
                continue
            file_hits = sorted({
                token
                for line in lines
                if not line.lstrip().startswith(("#", "//"))
                for token in W9_TOKEN_RE.findall(line)
                if is_deprecated_w9_access_key(token)
            })
            if file_hits:
                rel = path.relative_to(target).as_posix()
                residuals.append(f"{rel}: deprecated platform access variables must be removed ({', '.join(file_hits)})")
    return residuals


def safe_access_path(value: str) -> bool:
    if not value.startswith("/") or any(character in value for character in "?#\\"):
        return False
    if re.search(r"%(?![0-9a-fA-F]{2})", value):
        return False
    try:
        decoded = unquote(value, errors="strict")
    except UnicodeError:
        return False
    return not (
        decoded.startswith("//") or "\\" in decoded or CONTROL_RE.search(decoded)
        or any(segment in (".", "..") for segment in decoded.split("/"))
    )


def load_access_types(schema: dict) -> dict:
    dictionary = json.loads(repo_path("metadata", "access-types.json").read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator({"$defs": schema["$defs"], "$ref": "#/$defs/accessTypes"})
    if not validator.is_valid(dictionary):
        raise ValueError("Invalid access dictionary")
    if any(scheme not in dictionary["schemes"] for role in dictionary["roles"].values() for scheme in role["schemes"]):
        raise ValueError("Unknown dictionary scheme")
    return dictionary


def _protocol_of(item) -> str:
    if isinstance(item, dict):
        return str(item.get("protocol") or "tcp").lower()
    text = str(item)
    return text.rsplit("/", 1)[-1].lower() if "/" in text else "tcp"


def _service_ports(service: dict, env: dict) -> tuple[set[tuple[int, str]], set[tuple[int, str]], bool]:
    """Return (resolved container ports, published container ports, unresolved flag)."""
    from libs.validate import _container_port

    ports = service.get("ports") or []
    expose = service.get("expose") or []
    if not isinstance(ports, list) or not isinstance(expose, list):
        raise ValueError("Expected service port arrays")
    resolved: set[tuple[int, str]] = set()
    published: set[tuple[int, str]] = set()
    unresolved = False
    for item in ports:
        key = (_container_port(item, env), _protocol_of(item))
        if key[0] is None:
            unresolved = True
        else:
            resolved.add(key)
            published.add(key)
    for item in expose:
        protocol = _protocol_of(item)
        if protocol not in {"tcp", "udp"}:
            continue
        port = _container_port(item, env)
        if port is None:
            unresolved = True
        else:
            resolved.add((port, protocol))
    return resolved, published, unresolved


def access_metadata(target: Path) -> dict:
    result = {"ok": True, "status": "not_declared", "errors": [], "warnings": [], "migration": [], "entries": []}
    try:
        variables = json.loads((target / "variables.json").read_text(encoding="utf-8"))
        if not isinstance(variables, dict):
            raise ValueError("Expected object")
    except (OSError, ValueError):
        return {**result, "ok": False, "status": "invalid", "errors": ["variables.json: invalid object"]}
    declaration = variables.get("access")
    errors = result["errors"]
    warnings = result["warnings"]
    dictionary: dict = {"roles": {}, "schemes": {}}
    if "access" in variables:
        try:
            schema = json.loads(repo_path("metadata", "variables.schema.json").read_text(encoding="utf-8"))
            validator = jsonschema.Draft202012Validator({"$defs": schema["$defs"], **schema["properties"]["access"]})
            for error in validator.iter_errors(declaration):
                path = "/".join(str(part) for part in error.path)
                errors.append(f"access/{path}: violates {error.validator}")
            dictionary = load_access_types(schema)
        except (OSError, ValueError, KeyError, jsonschema.SchemaError):
            errors.append("access metadata: missing or invalid schema/dictionary")
        if errors:
            return {**result, "ok": False, "status": "invalid"}
    else:
        errors.append("access: declaration required; verify port groups or explicitly declare no network entry")
        return {**result, "ok": False, "status": "not_declared"}
    try:
        compose_path = target / "docker-compose.yml"
        compose = yaml.safe_load(compose_path.read_text(encoding="utf-8")) or {} if compose_path.exists() else {}
        services = compose.get("services") or {}
        if not isinstance(services, dict):
            raise ValueError("Expected services object")
    except (OSError, ValueError, yaml.YAMLError, AttributeError):
        return {**result, "ok": False, "status": "invalid", "errors": ["docker-compose.yml: invalid object"]}
    try:
        env = dotenv_values(target / ".env", interpolate=False)
    except (OSError, UnicodeError):
        return {**result, "ok": False, "status": "invalid", "errors": [".env: unreadable configuration"]}
    errors.extend(_find_deprecated_w9_residuals(target, env, compose))
    groups = [group for group in declaration if isinstance(group, dict)]
    seen_group_ids: set = set()
    seen_group_targets: set = set()
    seen_env_names: dict[str, str] = {}
    address_env_names: set[str] = set()
    for index, group in enumerate(groups):
        prefix = f"access/{index}"
        group_id = group.get("id")
        if group_id in seen_group_ids:
            errors.append(f"{prefix}/id: duplicate port group id")
        seen_group_ids.add(group_id)
        service_name = group.get("service")
        service = services.get(service_name)
        if not isinstance(service, dict):
            errors.append(f"{prefix}/service: service does not exist")
        else:
            if service.get("profiles"):
                errors.append(f"{prefix}/service: optional profile service cannot be a default access target")
            if str(service.get("restart") or "").strip().lower() == "no":
                errors.append(f"{prefix}/service: one-shot service (restart: no) cannot be an access target")
        protocol = group.get("protocol") or "tcp"
        port = group.get("port")
        if isinstance(port, str):
            reference = VARIABLE_RE.fullmatch(port)
            value = env.get(reference.group(1)) if reference else None
            try:
                port = int(value) if isinstance(value, str) and value.isascii() and value.isdecimal() else None
            except ValueError:
                port = None
        if isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535:
            errors.append(f"{prefix}/port: unresolved or out of range")
            continue
        target_key = (service_name, port, protocol)
        if target_key in seen_group_targets:
            errors.append(f"{prefix}: duplicate access port group target")
        seen_group_targets.add(target_key)
        evidence = "unverified"
        unresolved = False
        if isinstance(service, dict):
            try:
                resolved, _published, unresolved = _service_ports(service, env)
            except (TypeError, ValueError):
                errors.append(f"{prefix}/port: invalid target service port configuration")
                resolved, unresolved = set(), True
            if (port, protocol) in resolved:
                evidence = "matched"
            elif resolved and not unresolved:
                errors.append(f"{prefix}/port: conflicts with target service port configuration")
        if evidence == "unverified":
            warnings.append(f"{prefix}/port: listener evidence unverified; deployment test required")
        public = group.get("public")
        endpoints = group.get("endpoints") or []
        identities: set = set()
        kinds_all: list[str] = []
        bindable = False
        for endpoint_index, endpoint in enumerate(endpoints):
            endpoint_prefix = f"{prefix}/endpoints/{endpoint_index}"
            if not isinstance(endpoint, dict):
                errors.append(f"{endpoint_prefix}: expected object")
                continue
            roles = endpoint.get("roles") or []
            scheme = endpoint.get("scheme")
            if any(role not in dictionary["roles"] for role in roles) or scheme not in dictionary["schemes"]:
                errors.append(f"{endpoint_prefix}: unknown role or scheme")
                continue
            ranks = [KIND_ORDER[dictionary["roles"][role]["kind"]] for role in roles]
            if ranks != sorted(ranks):
                errors.append(f"{endpoint_prefix}/roles: kinds are out of order")
            if any(scheme not in dictionary["roles"][role]["schemes"] for role in roles):
                errors.append(f"{endpoint_prefix}/scheme: conflicts with roles")
            path_capable = dictionary["schemes"][scheme]["allowPathQuery"]
            bindable = bindable or path_capable
            if not path_capable and ("path" in endpoint or "query" in endpoint):
                errors.append(f"{endpoint_prefix}: protocol does not allow path/query")
            if "path" in endpoint and not safe_access_path(endpoint["path"]):
                errors.append(f"{endpoint_prefix}/path: unsafe access path")
            for key, value in (endpoint.get("query") or {}).items():
                if key.casefold() in CREDENTIAL_FIELDS or any(
                    CONTROL_RE.search(part) or "${" in part or "{{" in part for part in (key, value)
                ):
                    errors.append(f"{endpoint_prefix}/query: unsafe static parameter")
            identity = (scheme, endpoint.get("path", "/"), json.dumps(endpoint.get("query") or {}, sort_keys=True))
            if identity in identities:
                errors.append(f"{endpoint_prefix}: duplicate access endpoint target")
            identities.add(identity)
            kinds_all.extend(dictionary["roles"][role]["kind"] for role in roles)
        kinds = list(dict.fromkeys(kinds_all))
        require_domain = bool(group.get("requireDomain"))
        require_https = bool(group.get("requireHttps"))
        if require_domain and not bindable:
            errors.append(f"{prefix}/requireDomain: group has no URL-capable endpoint")
        if require_https and not bindable:
            errors.append(f"{prefix}/requireHttps: group has no URL-capable endpoint")
        if require_https and public and any(endpoint.get("scheme") in {"http", "ws"} for endpoint in endpoints):
            errors.append(f"{prefix}/public: plaintext listener requiring HTTPS cannot be published directly")
        for field in ("rootUrl", "host"):
            if field in group and not bindable:
                errors.append(f"{prefix}/{field}: group has no URL-capable endpoint")
        for field in VALUE_FIELDS:
            for name in group.get(field) or []:
                if name.startswith("W9_"):
                    errors.append(f"{prefix}/{field}: {name} must be an upstream native variable, not W9_*")
                if field in ("rootUrl", "host"):
                    address_env_names.add(name)
                if name in seen_env_names:
                    errors.append(f"{prefix}/{field}: {name} is already written by another declaration")
                else:
                    seen_env_names[name] = field
                if name not in env:
                    errors.append(f"{prefix}/{field}: {name} is not declared in .env")
        result["entries"].append(
            {
                "id": group_id,
                "service": service_name,
                "container_port": port,
                "protocol": protocol,
                "public": public,
                "require_domain": require_domain,
                "require_https": require_https,
                "can_bind_domain": bindable,
                "kinds": kinds,
                "main_kind": kinds[0] if kinds else None,
                "port_evidence": evidence,
                "endpoints": [
                    {
                        "roles": endpoint.get("roles"),
                        "scheme": endpoint.get("scheme"),
                        "path": endpoint.get("path", "/"),
                        "query": endpoint.get("query") or {},
                    }
                    for endpoint in endpoints
                    if isinstance(endpoint, dict)
                ],
            }
        )
    for service_name, service in services.items():
        if not isinstance(service, dict) or service.get("profiles"):
            continue
        prefix = f"services/{service_name}"
        try:
            _, published, _ = _service_ports(service, env)
        except ValueError:
            errors.append(f"{prefix}/ports: invalid port configuration")
            continue
        unmanaged = service.get(UNMANAGED_PORTS_KEY, {})
        if not isinstance(unmanaged, dict):
            errors.append(f"{prefix}/{UNMANAGED_PORTS_KEY}: expected a mapping of target ports to reasons")
            unmanaged = {}
        validated_exemptions = set()
        for key, reason in unmanaged.items():
            match = re.fullmatch(r"([0-9]{1,5})/(tcp|udp)", key) if isinstance(key, str) else None
            if not match or not isinstance(reason, str) or not reason.strip():
                errors.append(f"{prefix}/{UNMANAGED_PORTS_KEY}: expected '<port>/<protocol>' and a nonempty reason")
                continue
            binding = (int(match[1]), match[2])
            if binding not in published or (service_name, *binding) in seen_group_targets:
                errors.append(f"{prefix}/{UNMANAGED_PORTS_KEY}: {key} must be published and absent from access")
                continue
            validated_exemptions.add(binding)
        for port, protocol in sorted(published - validated_exemptions):
            if (service_name, port, protocol) not in seen_group_targets:
                errors.append(f"{prefix}/ports: published {port}/{protocol} must be declared in access or explicitly exempted")
    if address_env_names:
        for svc_name, svc_def in services.items():
            if not isinstance(svc_def, dict) or not isinstance(svc_def.get("hostname"), str):
                continue
            for ref in ENV_VAR_REF_RE.findall(svc_def["hostname"]):
                if ref in address_env_names:
                    errors.append(
                        f"services/{svc_name}/hostname: must not reference external address variable {ref}"
                    )
    status = (
        "invalid" if errors
        else "unverified" if warnings
        else "ok" if result["entries"]
        else "no_entries"
    )
    return {**result, "ok": not errors, "status": status, "entries": [] if errors else result["entries"]}