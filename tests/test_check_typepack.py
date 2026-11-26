"""scripts/check_typepack.py holds the issue-dag@2 typepack to a pinned Wesley and to the shape dialect
of versions.md A6 (flyingrobots/taskalisk#97). These tests run offline with a fake Wesley; CI runs the
check against the real one."""
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_typepack", ROOT / "scripts" / "check_typepack.py")
check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check)

HASH = "c790407a445c00f60026e3e0e30a7ba30f48eb2f69d95ebc9466d5d5cb952388"


def field(name, base="String", **extra):
    return dict({"name": name, "type": {"base": base, "nullable": True, "isList": False}, "directives": {}}, **extra)


def lowered(*types):
    return {"version": "1.0.0", "types": list(types)}


GOOD = lowered({"name": "Frontmatter", "kind": "INPUT_OBJECT", "directives": {}, "fields": [field("dag")]},
               {"name": "IssueRef", "kind": "SCALAR", "directives": {}, "fields": []},
               {"name": "Kind", "kind": "ENUM", "directives": {}, "fields": []})


class FakeWesley:
    """Answers the four Wesley calls the check makes, from canned results."""

    def __init__(self, lower=GOOD, schema_hash=HASH, lint_ok=True, version=check.PINNED_VERSION):
        self.lower, self.schema_hash, self.lint_ok, self.version = lower, schema_hash, lint_ok, version

    def __call__(self, args):
        if args[0] == "--version":
            return 0, self.version + "\n"
        if args[:2] == ["schema", "lower"]:
            return 0, json.dumps(self.lower)
        if args[:2] == ["schema", "hash"]:
            return 0, self.schema_hash + "\n"
        if args[:2] == ["law", "lint"]:
            return (0, json.dumps({"lawHash": "sha256:" + "0" * 64})) if self.lint_ok else (1, "WESLAW_INVALID_DOCUMENT")
        raise AssertionError(f"unexpected call {args}")


LAW_HASH = f'sha256:{HASH}'


class CheckTypepackTest(unittest.TestCase):
    def test_a_typepack_in_the_dialect_with_its_hash_passes(self):
        self.assertEqual(check.problems(FakeWesley(), LAW_HASH), [])

    def test_a_default_value_is_outside_the_dialect(self):
        bad = lowered({"name": "Frontmatter", "kind": "INPUT_OBJECT", "directives": {}, "fields": [field("size", "Int", defaultValue=3)]})
        self.assertTrue(any("default" in p for p in check.problems(FakeWesley(lower=bad), LAW_HASH)))

    def test_a_field_directive_is_outside_the_dialect(self):
        bad = lowered({"name": "Frontmatter", "kind": "INPUT_OBJECT", "directives": {}, "fields": [field("dag", directives={"deprecated": True})]})
        self.assertTrue(any("directive" in p for p in check.problems(FakeWesley(lower=bad), LAW_HASH)))

    def test_a_type_directive_is_outside_the_dialect(self):
        bad = lowered({"name": "Frontmatter", "kind": "INPUT_OBJECT", "directives": {"key": True}, "fields": [field("dag")]})
        self.assertTrue(any("directive" in p for p in check.problems(FakeWesley(lower=bad), LAW_HASH)))

    def test_an_output_type_is_outside_the_dialect(self):
        bad = lowered({"name": "Frontmatter", "kind": "OBJECT", "directives": {}, "fields": [field("dag")]})
        self.assertTrue(any("OBJECT" in p for p in check.problems(FakeWesley(lower=bad), LAW_HASH)))

    def test_laws_bound_to_another_shape_fail(self):
        self.assertTrue(any("hash" in p for p in check.problems(FakeWesley(), "sha256:" + "1" * 64)))

    def test_laws_wesley_rejects_fail(self):
        self.assertTrue(any("law lint" in p for p in check.problems(FakeWesley(lint_ok=False), LAW_HASH)))

    def test_another_wesley_version_is_refused(self):
        problems = check.problems(FakeWesley(version="0.4.0"), LAW_HASH)
        self.assertEqual(len(problems), 1)
        self.assertIn("pinned", problems[0])

    def test_the_recorded_identity_names_the_pinned_wesley(self):
        record = json.loads((ROOT / "typepacks" / "issue-dag@2" / "WESLEY.json").read_text())
        self.assertEqual((record["version"], record["commit"]), (check.PINNED_VERSION, check.PINNED_COMMIT))
        self.assertEqual(record["schema_hash"], LAW_HASH)

    def test_the_committed_laws_name_the_committed_shape_hash(self):
        self.assertEqual(check.law_schema_hash((ROOT / "typepacks" / "issue-dag@2" / "laws.weslaw.yaml").read_text()), LAW_HASH)

    def test_no_typepack_file_calls_itself_unvalidated(self):
        for path in (ROOT / "typepacks" / "issue-dag@2").iterdir():
            with self.subTest(path.name):
                self.assertNotIn("UNVALIDATED", path.read_text().upper())


if __name__ == "__main__":
    unittest.main()
