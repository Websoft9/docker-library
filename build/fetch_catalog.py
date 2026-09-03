#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import requests


CONTENTFUL_URL = "https://graphql.contentful.com/content/v1/spaces/ffrhttfighww"
LOCALES = {
    "en-US": "en",
    "zh-CN": "zh",
}
CATALOG_QUERY = """
query($locale: String!) {
  catalog(id: \"2Yp0TY3kBHgG6VDjsHZNpK\", locale: $locale) {
    linkedFrom(allowedLocales: [\"en-US\"]) {
      catalogCollection(limit: 20) {
        items {
          key
          position
          title
          linkedFrom(allowedLocales: [\"en-US\"]) {
            catalogCollection(limit: 20) {
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
}
"""
PRODUCT_QUERY = """
query($locale: String!, $skip: Int!, $production: Boolean) {
  productCollection(locale: $locale, where: {appStore: true, production: $production}, limit: 100, skip: $skip) {
    total
    items {
      sys { id }
      key
      hot
      trademark
      summary
      overview
      websiteurl
      description
      screenshots
      distribution
      vcpu
      memory
      storage
      logo { imageurl }
      relatedAppsCollection(limit: 10) {
        items {
          key
          trademark
        }
      }
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch catalog JSON data from Contentful.")
    parser.add_argument("--channel", required=True, choices=("dev", "rc", "release"))
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--token", default=os.getenv("CONTENTFUL_GRAPHQL_TOKEN"))
    return parser.parse_args()


def run_query(token: str, query: str, variables: dict) -> dict:
    response = requests.post(
        CONTENTFUL_URL,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        json={
            "query": query,
            "variables": variables,
        },
        timeout=120,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("errors"):
        raise SystemExit(json.dumps(payload["errors"], ensure_ascii=False, indent=2))
    return payload["data"]


def fetch_catalog_entries(token: str, locale: str) -> list[dict]:
    data = run_query(token, CATALOG_QUERY, {"locale": locale})
    catalog = data.get("catalog") or {}
    linked = catalog.get("linkedFrom") or {}
    collection = linked.get("catalogCollection") or {}
    return collection.get("items") or []


def fetch_product_entries(token: str, locale: str, production: bool | None) -> list[dict]:
    items: list[dict] = []
    skip = 0
    total = 1
    while skip < total:
        variables = {
            "locale": locale,
            "skip": skip,
            "production": production,
        }
        data = run_query(token, PRODUCT_QUERY, variables)
        collection = data.get("productCollection") or {}
        total = collection.get("total") or 0
        items.extend(collection.get("items") or [])
        skip += 100
    return items


def write_json(path: Path, payload: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def main() -> int:
    args = parse_args()
    if not args.token:
        raise SystemExit("missing Contentful GraphQL token; set --token or CONTENTFUL_GRAPHQL_TOKEN")

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    production = True if args.channel == "release" else None

    for locale, short_code in LOCALES.items():
        catalog_entries = fetch_catalog_entries(args.token, locale)
        product_entries = fetch_product_entries(args.token, locale, production)
        write_json(output_dir / f"catalog_{short_code}.json", catalog_entries)
        write_json(output_dir / f"product_{short_code}.json", product_entries)

    return 0


if __name__ == "__main__":
    sys.exit(main())
