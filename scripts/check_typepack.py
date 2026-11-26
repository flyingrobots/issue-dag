#!/usr/bin/env python3
"""Check the issue-dag@2 typepack with the pinned Wesley.

The check requires:
- Wesley at the pinned version (PINNED_VERSION, built from PINNED_COMMIT);
- the shape to lower, using only input types, custom scalars and enums, with no default value and no
  directive on a type or a field (the shape dialect, versions.md A6);
- the laws to name the shape's own hash (`schema.hash`), and `wesley law lint` to accept them.

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


def law_schema_hash(laws_text):
    """The `schema.hash` the laws file binds itself to, or None."""
    m = LAW_HASH_RE.search(laws_text)
    return m.group("hash") if m else None


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


def problems(wesley, law_hash, shape=TYPEPACK / "shape.graphql", laws=TYPEPACK / "laws.weslaw.yaml"):
    """Why the typepack fails the check; empty when it passes. `wesley(args)` returns (status, stdout)."""
    status, out = wesley(["--version"])
    if status != 0 or out.strip() != PINNED_VERSION:
        return [f"Wesley {out.strip() or '(unknown)'} is not the pinned {PINNED_VERSION} ({PINNED_COMMIT})"]
    found = []
    status, out = wesley(["schema", "lower", "--schema", str(shape), "--json"])
    if status != 0:
        found.append(f"wesley schema lower rejected the shape: {out.strip()}")
    else:
        found += dialect_problems(json.loads(out))
    status, out = wesley(["schema", "hash", "--schema", str(shape)])
    shape_hash = "sha256:" + out.strip() if status == 0 else None
    if shape_hash is None:
        found.append("wesley schema hash failed")
    elif law_hash != shape_hash:
        found.append(f"the laws name schema hash {law_hash}, but the shape's hash is {shape_hash}")
    status, out = wesley(["law", "lint", "--law", str(laws), "--json"])
    if status != 0:
        found.append(f"wesley law lint rejected the laws: {out.strip()}")
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--wesley", required=True, help="path to the wesley binary")
    ns = parser.parse_args()

    def run(args):
        p = subprocess.run([ns.wesley, *args], capture_output=True, text=True)
        return p.returncode, p.stdout if p.returncode == 0 else (p.stdout + p.stderr)

    found = problems(run, law_schema_hash((TYPEPACK / "laws.weslaw.yaml").read_text()))
    for line in found:
        print(f"check_typepack: {line}", file=sys.stderr)
    if not found:
        print(f"check_typepack: issue-dag@2 passes with Wesley {PINNED_VERSION} ({PINNED_COMMIT})")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
