from __future__ import annotations

import base64
import binascii
import json
import re
from pathlib import Path

from dotenv import dotenv_values
import jsonschema

from libs.repo import repo_path


REFERENCE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")
VARIABLE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
PLATFORM_FIELDS = {"W9_POWER_PASSWORD", "W9_RCODE"}


def load_secret_rules() -> dict[str, dict]:
    rules_path = repo_path("metadata", "secret-rules.json")
    schema_path = repo_path("metadata", "variables.schema.json")
    rules = json.loads(rules_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator({"$defs": schema["$defs"], "$ref": "#/$defs/secretRules"}).validate(rules)
    return rules


def _valid_rule_spec(rule: str, rules: dict[str, dict]) -> bool:
    name, sep, param = rule.partition(":")
    spec = rules.get(name)
    if not isinstance(spec, dict):
        return False
    if spec.get("generator") == "jwt":
        return sep == ":" and bool(VARIABLE.fullmatch(param))
    return spec.get("generator") == "random_bytes" and not sep


def parse_secret_declarations(
    raw_secrets: object,
    rules: dict[str, dict] | None = None,
) -> tuple[list[tuple[str, str | None]], list[str]]:
    if raw_secrets is None:
        return [], []
    if not isinstance(raw_secrets, list):
        return [], ["env.secrets: expected a list of variable names or single-key rule objects"]
    if rules is None:
        try:
            rules = load_secret_rules()
        except (OSError, ValueError, KeyError, jsonschema.ValidationError):
            return [], ["metadata/secret-rules.json: missing or invalid secret rules dictionary"]
    declarations: list[tuple[str, str | None]] = []
    errors: list[str] = []
    seen: set[str] = set()
    for item in raw_secrets:
        if isinstance(item, str):
            if not VARIABLE.fullmatch(item):
                errors.append(f"env.secrets: invalid variable name {item!r}")
                continue
            name, rule = item, None
        elif isinstance(item, dict) and len(item) == 1:
            name, rule = next(iter(item.items()))
            if not isinstance(name, str) or not VARIABLE.fullmatch(name):
                errors.append(f"env.secrets: invalid variable name {name!r}")
                continue
            if not isinstance(rule, str) or not _valid_rule_spec(rule, rules):
                errors.append(f"{name}: unsupported secret rule {rule!r}")
                continue
        else:
            errors.append("env.secrets: expected variable names or single-key rule objects")
            continue
        if name in seen:
            errors.append(f"{name}: duplicate secret declaration")
            continue
        seen.add(name)
        declarations.append((name, rule))
    return declarations, errors


def declared_secret_names(raw_secrets: object) -> list[str]:
    declarations, _ = parse_secret_declarations(raw_secrets)
    return [name for name, _ in declarations]


def _single_template_issue(value: str) -> str | None:
    body = value[3:] if value.startswith("sk-") else value
    if re.fullmatch(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}", body):
        return "UUID requires a dedicated generator"
    segments = body.split("-")
    if not value.startswith("sk-") and len(segments) > 1 and re.fullmatch(r"[A-Za-z]+", segments[0]):
        return "ambiguous fixed prefix"
    if any(not re.fullmatch(r"[A-Za-z0-9]+", segment) for segment in segments):
        return "unsupported format; use a random seed and references or a dedicated generator"
    if sum(map(len, segments)) < 12:
        return "random portion must contain at least 12 characters"
    return None


def template_issue(value: str, rule: str | None = None, rules: dict[str, dict] | None = None) -> str | None:
    if rule is None:
        parts = [part.strip() for part in value.split(",")] if "," in value else [value]
        if any(not part for part in parts):
            return "empty item in comma-separated secret list"
        for part in parts:
            if issue := _single_template_issue(part):
                return issue
        return None
    if rules is None:
        try:
            rules = load_secret_rules()
        except (OSError, ValueError, KeyError, jsonschema.ValidationError):
            return "metadata/secret-rules.json: missing or invalid secret rules dictionary"
    if not _valid_rule_spec(rule, rules):
        return f"unsupported secret rule {rule!r}"
    spec = rules[rule.partition(":")[0]]
    if spec["generator"] == "random_bytes":
        urlsafe = spec["encoding"] == "base64url"
        try:
            raw = base64.b64decode(value.encode("ascii"), altchars=b"-_" if urlsafe else None, validate=True)
        except (binascii.Error, ValueError):
            return f"{rule} rule requires a valid {spec['encoding']} default template"
        encoded = base64.urlsafe_b64encode(raw) if urlsafe else base64.b64encode(raw)
        if not raw or encoded.decode("ascii") != value:
            return f"{rule} template must be non-empty canonical {spec['encoding']}"
        if "bytes" in spec and len(raw) != spec["bytes"]:
            return f"{rule} template must decode to exactly {spec['bytes']} bytes"
        return None
    if spec["generator"] == "jwt":
        segments = value.split(".")
        if len(segments) != 3 or any(not seg for seg in segments):
            return "jwt rule requires a three-segment JWT default template"
        try:
            for index, seg in enumerate(segments[:2]):
                padded = seg + "=" * (-len(seg) % 4)
                decoded = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8"))
                if not isinstance(decoded, dict):
                    return "jwt header and payload must be JSON objects"
                if index == 0 and decoded.get("alg") != spec["algorithm"]:
                    return f"jwt template must use {spec['algorithm']}"
        except Exception:
            return "jwt rule requires decodable JSON header and payload segments"
        return None
    return f"unsupported secret rule {rule!r}"


def references(value: str) -> list[str]:
    return [match.group(1) or match.group(2) for match in REFERENCE.finditer(value)]


def check_secret_templates(target: Path) -> dict:
    metadata = json.loads((target / "variables.json").read_text(encoding="utf-8"))
    values = dotenv_values(target / ".env", interpolate=False)
    try:
        rules = load_secret_rules()
    except (FileNotFoundError, ValueError, KeyError, jsonschema.ValidationError):
        return {
            "ok": False,
            "status": "invalid",
            "fields": [],
            "errors": ["metadata/secret-rules.json: missing or invalid secret rules dictionary"],
        }
    raw_secrets = (metadata.get("env") or {}).get("secrets")
    declarations, parse_errors = parse_secret_declarations(raw_secrets, rules)
    result = {"ok": True, "status": "not_applicable", "fields": [], "errors": list(parse_errors)}
    if parse_errors:
        return {**result, "ok": False, "status": "invalid"}

    rule_map = dict(declarations)
    declared_names = [name for name, _ in declarations]

    def resolve(field: str, visiting: set[str]) -> str:
        if field in visiting:
            raise ValueError("circular reference")
        if field in PLATFORM_FIELDS and field in values:
            return "generated-platform-value"
        value = values.get(field)
        if not value:
            raise ValueError("missing or empty reference: " + field)
        resolved = REFERENCE.sub(lambda match: resolve(match.group(1) or match.group(2), visiting | {field}), value)
        if "$" in resolved:
            raise ValueError("unsupported variable reference")
        return resolved

    targets = list(dict.fromkeys(declared_names + sorted(PLATFORM_FIELDS & values.keys())))
    managed = set(targets)
    for field in targets:
        value = values.get(field) or ""
        rule = rule_map.get(field)
        refs = list(references(value))
        if rule and rule.startswith("jwt:"):
            signing_key = rule.split(":", 1)[1]
            if signing_key not in refs:
                refs.append(signing_key)
        kind = (
            "platform"
            if field in PLATFORM_FIELDS
            else f"rule:{rule}"
            if rule
            else "reference"
            if references(value)
            else "random_template"
        )
        field_entry = {"name": field, "kind": kind, "references": refs}
        result["fields"].append(field_entry)
        if field in PLATFORM_FIELDS:
            continue
        if rule and rule.startswith("jwt:"):
            signing_key = rule.split(":", 1)[1]
            if signing_key not in values or not values.get(signing_key):
                result["errors"].append(f"{field}: missing or empty jwt signing key: {signing_key}")
                continue
            if signing_key not in managed:
                result["errors"].append(f"{field}: jwt signing key {signing_key} must be declared in env.secrets")
                continue
        try:
            resolve(field, set())
        except ValueError as error:
            result["errors"].append(field + ": " + str(error))
            continue
        if (kind == "random_template" or rule is not None) and (issue := template_issue(value, rule, rules)):
            result["errors"].append(field + ": " + issue)
    result["ok"] = not result["errors"]
    result["status"] = "invalid" if result["errors"] else "checked" if targets else "not_applicable"
    return result
