#!/usr/bin/env python3
"""Update only the generated changelog section of an existing GitHub Release."""
from __future__ import annotations

import argparse
from pathlib import Path


START = "<!-- generated-changelog:start -->"
END = "<!-- generated-changelog:end -->"


def merge_notes(body: str, changelog: str) -> str:
    block = f"{START}\n{changelog.strip()}\n{END}"
    if START not in body and END not in body:
        return f"{body.rstrip()}\n\n{block}\n".lstrip("\n")
    if body.count(START) != 1 or body.count(END) != 1 or body.index(END) < body.index(START):
        raise ValueError("Invalid generated changelog markers in Release body")
    before, remainder = body.split(START, 1)
    _, after = remainder.split(END, 1)
    return before + block + after


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--body", required=True)
    parser.add_argument("--changelog", required=True)
    args = parser.parse_args()
    print(merge_notes(Path(args.body).read_text(), Path(args.changelog).read_text()), end="")
