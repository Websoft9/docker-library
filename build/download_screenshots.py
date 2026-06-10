#!/usr/bin/env python3
"""Download legacy screenshots from Contentful product JSON URLs."""
import json
import os
import sys
import urllib.request
from pathlib import Path

OUTPUT_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dist/catalog-source/screenshots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

for product_file in sorted(Path("dist/catalog-source").glob("product_*.json")):
    if not product_file.exists():
        continue
    with open(product_file, encoding="utf-8") as fh:
        data = json.load(fh)

    urls = set()
    for item in data:
        for s in item.get("screenshots", []):
            u = s.get("value") or s.get("imageurl")
            if u:
                urls.add(u)

    for url in sorted(urls):
        try:
            name = url.rsplit("/", 1)[-1].split("?")[0]
            if "." not in name:
                name = f"{abs(hash(url)):012x}.png"
            path = OUTPUT_DIR / name
            if not path.exists():
                print(f"Downloading: {url}", file=sys.stderr)
                urllib.request.urlretrieve(url, path)
        except Exception as exc:
            print(f"Warning: screenshot {url}: {exc}", file=sys.stderr)
