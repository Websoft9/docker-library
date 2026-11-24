from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import requests

from libs import http
from libs.credentials import resolve_secret
from libs.repo import repo_path


DEFAULT_CATALOG_URL = "https://artifact.websoft9.com/appstore/release/catalog/catalog_en.json"
DEFAULT_PRODUCT_URL = "https://artifact.websoft9.com/appstore/release/catalog/product_en.json"
DEFAULT_TAXONOMY_OUTPUT = "metadata/catalog-taxonomy.json"
DEFAULT_CATALOG_DIR = "metadata/.catalog"
CONTENTFUL_GRAPHQL_URL = "https://graphql.contentful.com/content/v1/spaces/ffrhttfighww"
CONTENTFUL_GRAPHQL_TOKEN_ENV = "CONTENTFUL_GRAPHQL_TOKEN"

CATALOG_FIELD_KEYS = ("trademark", "summary", "overview", "description", "websiteurl", "screenshots")

PRODUCT_ENTRY_QUERY = """
query($locale: String!, $key: String!) {
  productCollection(locale: $locale, where: {key: $key}, limit: 1) {
    items {
      sys { id }
      key
      trademark
      summary
      overview
      description
      websiteurl
      screenshots
      catalogCollection(limit: 15) {
        items {
          key
          title
          catalogCollection(limit: 5) {
            items {
              key
              title
              position
            }
          }
        }
      }
    }
  }
}
"""


def _read_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def _display_path(path: Path) -> str:
    """Return a repo-relative path when possible, else the absolute path."""
    try:
        return str(path.relative_to(repo_path()))
    except ValueError:
        return str(path)


def catalog_schema() -> dict:
    return _read_json(repo_path("metadata", "catalog.schema.json"))


def product_artifact_schema() -> dict:
    return _read_json(repo_path("metadata", "product-artifact.schema.json"))


def validate_catalog_data(app_name: str, data: dict) -> None:
    validator = jsonschema.Draft202012Validator(catalog_schema())
    errors = sorted(validator.iter_errors(data), key=lambda item: list(item.path))
    if errors:
        joined = "; ".join(
            f"{'.'.join(str(part) for part in error.path) or 'catalog'}: {error.message}"
            for error in errors
        )
        raise ValueError(f"invalid catalog file for {app_name}: {joined}")


def load_catalog(app_name: str, catalog_dir: str = DEFAULT_CATALOG_DIR) -> dict:
    path = repo_path(*Path(catalog_dir).parts, f"{app_name}.json")
    if not path.exists():
        return {}
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"invalid catalog file for {app_name}: root must be an object")
    validate_catalog_data(app_name, payload)
    return payload


def write_catalog(app_name: str, payload: dict, catalog_dir: str = DEFAULT_CATALOG_DIR) -> str:
    validate_catalog_data(app_name, payload)
    path = repo_path(*Path(catalog_dir).parts, f"{app_name}.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return _display_path(path)


def taxonomy_path(path_value: str = DEFAULT_TAXONOMY_OUTPUT) -> Path:
    return repo_path(*Path(path_value).parts)


def load_taxonomy(path_value: str = DEFAULT_TAXONOMY_OUTPUT) -> dict:
    path = taxonomy_path(path_value)
    if not path.exists():
        raise FileNotFoundError(f"catalog taxonomy snapshot not found: {path.relative_to(repo_path())}")
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise ValueError("catalog taxonomy snapshot must be an object")
    return payload


def validate_catalog_bindings(catalog_data: dict, taxonomy: dict) -> list[dict]:
    bindings = catalog_data.get("catalogBindings") or []
    if not bindings:
        return []

    parent_children = {
        category.get("key"): {child.get("key") for child in category.get("children") or [] if child.get("key")}
        for category in taxonomy.get("categories") or []
        if category.get("key")
    }
    errors = []
    for binding in bindings:
        parent = binding.get("parentKey")
        child = binding.get("childKey")
        if parent not in parent_children:
            errors.append(f"unknown parentKey '{parent}'")
            continue
        if child not in parent_children[parent]:
            errors.append(f"unknown childKey '{child}' under parentKey '{parent}'")
    if errors:
        raise ValueError("invalid catalogBindings: " + "; ".join(errors))
    return bindings


def fetch_catalog(url: str = DEFAULT_CATALOG_URL) -> list[dict]:
    response = http.get(url)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list):
        raise ValueError("catalog artifact must be a JSON array")
    return payload


def normalize_catalog(entries: list[dict], source_url: str) -> dict:
    categories = []
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        key = str(entry.get("key") or "").strip()
        if not key or key in seen:
            continue
        seen.add(key)
        children = []
        linked = entry.get("linkedFrom") or {}
        collection = linked.get("catalogCollection") or {}
        for item in collection.get("items") or []:
            if not isinstance(item, dict):
                continue
            child_key = str(item.get("key") or "").strip()
            if not child_key:
                continue
            children.append({
                "key": child_key,
                "title": item.get("title"),
                "position": item.get("position"),
            })
        categories.append({
            "key": key,
            "title": entry.get("title"),
            "position": entry.get("position"),
            "children": children,
        })
    return {
        "version": 1,
        "source": source_url,
        "locale": "en",
        "categories": categories,
    }


def _extract_repo_catalog_fields(product_entry: dict) -> dict:
    payload = {key: product_entry.get(key) for key in CATALOG_FIELD_KEYS if product_entry.get(key) is not None}
    screenshots = payload.get("screenshots")
    if isinstance(screenshots, list):
        normalized = []
        for item in screenshots:
            if isinstance(item, dict) and item.get("value"):
                normalized.append(item["value"])
            elif isinstance(item, str):
                normalized.append(item)
        payload["screenshots"] = normalized
    bindings = []
    catalog_collection = (product_entry.get("catalogCollection") or {}).get("items") or []
    for child in catalog_collection:
        if not isinstance(child, dict):
            continue
        child_key = str(child.get("key") or "").strip()
        parents = (child.get("catalogCollection") or {}).get("items") or []
        for parent in parents:
            if not isinstance(parent, dict):
                continue
            parent_key = str(parent.get("key") or "").strip()
            if parent_key and child_key:
                bindings.append({"parentKey": parent_key, "childKey": child_key})
    if bindings:
        dedup = []
        seen = set()
        for item in bindings:
            key = (item["parentKey"], item["childKey"])
            if key in seen:
                continue
            seen.add(key)
            dedup.append(item)
        payload["catalogBindings"] = dedup
    return payload


def fetch_product(url: str = DEFAULT_PRODUCT_URL) -> list[dict]:
    response = http.get(url)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list):
        raise ValueError("product artifact must be a JSON array")
    return payload


def validate_product_entries(entries: list[dict]) -> dict:
    validator = jsonschema.Draft202012Validator(product_artifact_schema())
    errors = sorted(validator.iter_errors(entries), key=lambda item: list(item.path))
    if errors:
        joined = "; ".join(
            f"{'.'.join(str(part) for part in error.path) or 'product'}: {error.message}"
            for error in errors[:10]
        )
        raise ValueError(f"invalid published product artifact: {joined}")
    return {
        "entry_count": len(entries),
        "sample_fields": sorted(entries[0].keys()) if entries else [],
        "schema_valid": True,
    }


def fetch_product_entry(
    app_name: str,
    locale: str = "en-US",
    token: str | None = None,
    env_file: str | None = None,
) -> dict:
    """Fetch one published product entry live from Contentful GraphQL."""
    resolved = resolve_secret(CONTENTFUL_GRAPHQL_TOKEN_ENV, "contentful", token, env_file)
    if not resolved:
        raise FileNotFoundError(
            f"missing {CONTENTFUL_GRAPHQL_TOKEN_ENV}; set the env var, add .secrets/contentful.env, or pass --token"
        )
    try:
        response = http.post_with_retries(
            CONTENTFUL_GRAPHQL_URL,
            json_body={"query": PRODUCT_ENTRY_QUERY, "variables": {"locale": locale, "key": app_name}},
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {resolved}"},
            timeout=(5.0, 60.0),
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        status = getattr(getattr(error, "response", None), "status_code", None)
        if status in {401, 403}:
            raise ValueError(
                f"Contentful rejected the token (HTTP {status}); {CONTENTFUL_GRAPHQL_TOKEN_ENV} must be a "
                "Content Delivery/GraphQL API token, not the Management token used by catalog-push"
            ) from error
        raise ValueError(f"Contentful request failed: {error}") from error
    payload = response.json()
    if payload.get("errors"):
        raise ValueError(f"Contentful GraphQL error: {json.dumps(payload['errors'], ensure_ascii=False)}")
    items = ((payload.get("data") or {}).get("productCollection") or {}).get("items") or []
    if not items:
        raise FileNotFoundError(f"app not found in Contentful: {app_name} ({locale})")
    return items[0]


def pull_catalog(
    app_name: str,
    source: str = "contentful",
    product_url: str = DEFAULT_PRODUCT_URL,
    locale: str = "en-US",
    token: str | None = None,
    env_file: str | None = None,
    catalog_dir: str = DEFAULT_CATALOG_DIR,
    apply: bool = False,
    only_diff: bool = False,
) -> dict:
    if source == "contentful":
        entry = fetch_product_entry(app_name, locale=locale, token=token, env_file=env_file)
        source_ref = f"{CONTENTFUL_GRAPHQL_URL} ({locale})"
    elif source == "artifact":
        entries = fetch_product(product_url)
        entry = next((item for item in entries if isinstance(item, dict) and item.get("key") == app_name), None)
        if not entry:
            raise FileNotFoundError(f"app not found in published product artifact: {app_name}")
        source_ref = product_url
    else:
        raise ValueError(f"unsupported catalog pull source: {source}")

    incoming = _extract_repo_catalog_fields(entry)
    current = load_catalog(app_name, catalog_dir)
    diff = {}
    keys = sorted(set(current) | set(incoming))
    for key in keys:
        if current.get(key) != incoming.get(key):
            diff[key] = {"current": current.get(key), "incoming": incoming.get(key)}

    payload = {
        "app": app_name,
        "source": source_ref,
        "source_kind": source,
        "catalog_path": _display_path(repo_path(*Path(catalog_dir).parts, f"{app_name}.json")),
        "dry_run": not apply,
        "changed": bool(diff),
        "diff": diff,
    }
    if only_diff or not apply:
        payload["action"] = "diff" if only_diff else "preview"
        if not only_diff:
            payload["incoming"] = incoming
        return payload

    write_catalog(app_name, incoming, catalog_dir)
    payload["action"] = "written"
    return payload


def refresh_catalog(
    url: str = DEFAULT_CATALOG_URL,
    output: str = DEFAULT_TAXONOMY_OUTPUT,
    apply: bool = False,
    check_product_schema: bool = False,
    product_url: str = DEFAULT_PRODUCT_URL,
) -> dict:
    entries = fetch_catalog(url)
    snapshot = normalize_catalog(entries, url)
    output_path = repo_path(*Path(output).parts)
    payload = {
        "source": url,
        "output": str(output_path.relative_to(repo_path())),
        "dry_run": not apply,
        "category_count": len(snapshot["categories"]),
    }
    if check_product_schema:
        product_entries = fetch_product(product_url)
        payload["product_check"] = {
            "source": product_url,
            **validate_product_entries(product_entries),
        }
    if apply:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        payload["action"] = "written"
    else:
        payload["action"] = "preview"
        payload["snapshot"] = snapshot
    return payload
