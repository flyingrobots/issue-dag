#!/usr/bin/env python3
"""Check the issue-dag@2 typepack with the pinned Wesley.

The check requires:
- Wesley at the pinned version. `wesley --version` prints only the package version, so a build of
  that version from another commit would pass locally; CI builds exactly PINNED_COMMIT.
- The shape to lower, using only input types, custom scalars and enums, with no default value and
  no directive (the shape dialect, versions.md A6). Wesley's lowered form keeps enum values as plain
  strings and drops directive definitions, so the shape's source is read for directives as well.
- `wesley law validate` to bind the laws to the shape: every reference a law makes resolves, and the
  schema hash it reports is the shape's own hash.
- The shape hash, the law hash and the number of bound laws to equal the ones recorded in
  typepacks/issue-dag@2/WESLEY.json, so the record cannot drift from what Wesley computes.

Usage: python3 scripts/check_typepack.py --wesley <path to the wesley binary>
Exit 0 when every check holds, 1 otherwise. The result is printed, never assumed.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TYPEPACK = ROOT / "typepacks" / "issue-dag@2"
PINNED_VERSION = "0.3.0-alpha.1"
PINNED_COMMIT = "280d3d7b1abbaf40dbf5663ab3c5c1d6e58abbed"
DIALECT_KINDS = {"INPUT_OBJECT", "SCALAR", "ENUM"}
LAW_HASH_RE = re.compile(r'^schema:\s*\{[^}]*\bhash:\s*"(?P<hash>[^"]*)"', re.M)
# SDL source with its strings and comments removed: what is left is names and punctuation.
SDL_STRING_OR_COMMENT_RE = re.compile(r'"""[\s\S]*?"""|"(?:\\.|[^"\\\n])*"|#[^\n]*')


def law_schema_hash(laws_text):
    """The `schema.hash` the laws file binds itself to, or None."""
    m = LAW_HASH_RE.search(laws_text)
    return m.group("hash") if m else None


def source_problems(shape_text):
    """Directives the lowered form cannot show: on an enum value, or a directive definition."""
    code = SDL_STRING_OR_COMMENT_RE.sub(" ", shape_text)
    found = []
    if "@" in code:
        found.append("the shape's source uses a directive (@), which the dialect does not allow")
    if re.search(r"\bdirective\b", code):
        found.append("the shape's source defines a directive, which the dialect does not allow")
    return found


def dialect_problems(lowered):
    found = []
    for t in lowered.get("types", []):
        name, kind = t.get("name"), t.get("kind")
        if kind not in DIALECT_KINDS:
            found.append(f"type {name} is {kind}; the dialect allows only input types, scalars and enums")
        if t.get("directives"):
            found.append(f"type {name} carries a directive, which the dialect does not allow")
        for f in t.get("fields") or []:
            if "defaultValue" in f:
                found.append(f"field {name}.{f.get('name')} has a default value, which the dialect does not allow")
            if f.get("directives"):
                found.append(f"field {name}.{f.get('name')} carries a directive, which the dialect does not allow")
    return found


def problems(wesley, record, shape_text, shape=TYPEPACK / "shape.graphql", laws=TYPEPACK / "laws.weslaw.yaml"):
    """Why the typepack fails the check; empty when it passes. `wesley(args)` returns (status, stdout);
    `record` is WESLEY.json; `shape_text` is the shape's source."""
    status, out = wesley(["--version"])
    if status != 0 or out.strip() != PINNED_VERSION:
        return [f"Wesley {out.strip() or '(unknown)'} is not the pinned {PINNED_VERSION} ({PINNED_COMMIT})"]
    found = source_problems(shape_text)
    status, out = wesley(["schema", "lower", "--schema", str(shape), "--json"])
    if status != 0:
        found.append(f"wesley schema lower rejected the shape: {out.strip()}")
    else:
        found += dialect_problems(json.loads(out))
    status, out = wesley(["schema", "hash", "--schema", str(shape)])
    shape_hash = "sha256:" + out.strip() if status == 0 else None
    if shape_hash is None:
        found.append("wesley schema hash failed")
    elif shape_hash != record.get("schema_hash"):
        found.append(f"the shape's hash is {shape_hash}, but WESLEY.json records {record.get('schema_hash')}")
    status, out = wesley(["law", "validate", "--schema", str(shape), "--law", str(laws), "--json"])
    if status != 0:
        found.append(f"wesley law validate rejected the laws against the shape: {out.strip()}")
        return found
    bound = json.loads(out)
    if shape_hash is not None and bound.get("schemaHash") != shape_hash:
        found.append(f"the laws are bound to schema hash {bound.get('schemaHash')}, not the shape's {shape_hash}")
    if bound.get("lawHash") != record.get("law_hash"):
        found.append(f"the law hash is {bound.get('lawHash')}, but WESLEY.json records {record.get('law_hash')}")
    if bound.get("boundEntryCount") != record.get("bound_laws"):
        found.append(f"{bound.get('boundEntryCount')} laws are bound, but WESLEY.json records {record.get('bound_laws')}")
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--wesley", required=True, help="path to the wesley binary")
    ns = parser.parse_args()

    def run(args):
        p = subprocess.run([ns.wesley, *args], capture_output=True, text=True)
        return p.returncode, p.stdout if p.returncode == 0 else (p.stdout + p.stderr)

    record = json.loads((TYPEPACK / "WESLEY.json").read_text())
    found = problems(run, record, (TYPEPACK / "shape.graphql").read_text())
    for line in found:
        print(f"check_typepack: {line}", file=sys.stderr)
    if not found:
        print(f"check_typepack: issue-dag@2 passes with Wesley {PINNED_VERSION} ({PINNED_COMMIT})")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
