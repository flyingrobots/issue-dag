"""scripts/check_typepack.py holds the issue-dag@2 typepack to a pinned Wesley and to the shape dialect
of versions.md A6 (flyingrobots/taskalisk#97). These tests run offline with a fake Wesley; CI runs the
check against the real one."""
import importlib.util
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_typepack", ROOT / "scripts" / "check_typepack.py")
check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check)

HASH = "c790407a445c00f60026e3e0e30a7ba30f48eb2f69d95ebc9466d5d5cb952388"
LAW_HASH = "sha256:" + "b" * 64
RECORD = {"version": check.PINNED_VERSION, "commit": check.PINNED_COMMIT, "schema_hash": f"sha256:{HASH}",
          "law_hash": LAW_HASH, "bound_laws": 2}
SHAPE = "scalar IssueRef\nenum Kind { task container }\ninput Frontmatter {\n  dag: String!\n  kind: Kind!\n}\n"


def field(name, base="String", **extra):
    return dict({"name": name, "type": {"base": base, "nullable": True, "isList": False}, "directives": {}}, **extra)


def lowered(*types):
    return {"version": "1.0.0", "types": list(types)}


GOOD = lowered({"name": "Frontmatter", "kind": "INPUT_OBJECT", "directives": {}, "fields": [field("dag")]},
               {"name": "IssueRef", "kind": "SCALAR", "directives": {}, "fields": []},
               {"name": "Kind", "kind": "ENUM", "directives": {}, "fields": []})


class FakeWesley:
    """Answers the Wesley calls the check makes, from canned results."""

    def __init__(self, lower=GOOD, schema_hash=HASH, validate=None, version=check.PINNED_VERSION,
                 lower_status=0, hash_status=0):
        self.lower, self.schema_hash, self.version = lower, schema_hash, version
        self.lower_status, self.hash_status = lower_status, hash_status
        self.validate = validate if validate is not None else (
            0, {"schemaHash": f"sha256:{HASH}", "lawHash": LAW_HASH, "boundEntryCount": 2})
        self.calls = []

    def __call__(self, args):
        self.calls.append(args[:2])
        if args[0] == "--version":
            return 0, self.version + "\n"
        if args[:2] == ["schema", "lower"]:
            return (0, json.dumps(self.lower)) if self.lower_status == 0 else (1, "WESLEY_PARSE_ERROR")
        if args[:2] == ["schema", "hash"]:
            return (0, self.schema_hash + "\n") if self.hash_status == 0 else (1, "WESLEY_PARSE_ERROR")
        if args[:2] == ["law", "validate"]:
            status, body = self.validate
            return status, json.dumps(body) if isinstance(body, dict) else body
        raise AssertionError(f"unexpected call {args}")


def run(wesley=None, record=RECORD, shape=SHAPE):
    return check.problems(wesley or FakeWesley(), record, shape)


class CheckTypepackTest(unittest.TestCase):
    def test_a_typepack_in_the_dialect_bound_to_its_shape_passes(self):
        self.assertEqual(run(), [])

    def test_the_laws_are_validated_against_the_shape(self):
        wesley = FakeWesley()
        run(wesley)
        self.assertIn(["law", "validate"], wesley.calls)

    def test_a_law_naming_a_field_the_shape_lacks_fails(self):
        refused = (1, "WESLAW_UNRESOLVED_REFERENCE: Frontmatter has no field blokked_by")
        self.assertTrue(any("law validate" in p for p in run(FakeWesley(validate=refused))))

    def test_laws_bound_to_another_shape_fail(self):
        other = (0, {"schemaHash": "sha256:" + "1" * 64, "lawHash": LAW_HASH, "boundEntryCount": 2})
        self.assertTrue(any("hash" in p for p in run(FakeWesley(validate=other))))

    def test_a_law_hash_that_drifted_from_the_record_fails(self):
        self.assertTrue(any("law hash" in p for p in run(record=dict(RECORD, law_hash="sha256:" + "c" * 64))))

    def test_a_bound_law_count_that_drifted_from_the_record_fails(self):
        self.assertTrue(any("laws" in p for p in run(record=dict(RECORD, bound_laws=3))))

    def test_a_shape_hash_that_drifted_from_the_record_fails(self):
        self.assertTrue(any("hash" in p for p in run(record=dict(RECORD, schema_hash="sha256:" + "d" * 64))))

    def test_a_default_value_is_outside_the_dialect(self):
        bad = lowered({"name": "Frontmatter", "kind": "INPUT_OBJECT", "directives": {}, "fields": [field("size", "Int", defaultValue=3)]})
        self.assertTrue(any("default" in p for p in run(FakeWesley(lower=bad))))

    def test_a_field_directive_is_outside_the_dialect(self):
        bad = lowered({"name": "Frontmatter", "kind": "INPUT_OBJECT", "directives": {}, "fields": [field("dag", directives={"deprecated": True})]})
        self.assertTrue(any("directive" in p for p in run(FakeWesley(lower=bad))))

    def test_a_type_directive_is_outside_the_dialect(self):
        bad = lowered({"name": "Frontmatter", "kind": "INPUT_OBJECT", "directives": {"key": True}, "fields": [field("dag")]})
        self.assertTrue(any("directive" in p for p in run(FakeWesley(lower=bad))))

    def test_an_output_type_is_outside_the_dialect(self):
        bad = lowered({"name": "Frontmatter", "kind": "OBJECT", "directives": {}, "fields": [field("dag")]})
        self.assertTrue(any("OBJECT" in p for p in run(FakeWesley(lower=bad))))

    def test_a_directive_wesley_does_not_lower_is_found_in_the_source(self):
        """Wesley keeps enum values as plain strings and drops directive definitions, so the source is read too."""
        for shape in ("enum Kind { task @deprecated container }\n", "directive @foo on FIELD_DEFINITION\n",
                      'input F { a: String @x(reason: "y") }\n'):
            with self.subTest(shape):
                self.assertTrue(any("directive" in p for p in run(shape=shape)))

    def test_an_at_sign_in_a_comment_or_a_string_is_not_a_directive(self):
        for shape in ("# a comment naming @deprecated\nscalar IssueRef\n", '"""see @owner and directive"""\nscalar IssueRef\n',
                      'scalar IssueRef # owner/repo@x\n'):
            with self.subTest(shape):
                self.assertEqual(check.source_problems(shape), [])

    def test_a_shape_wesley_cannot_lower_or_hash_fails(self):
        self.assertTrue(any("lower" in p for p in run(FakeWesley(lower_status=1))))
        self.assertTrue(any("hash" in p for p in run(FakeWesley(hash_status=1))))

    def test_another_wesley_version_is_refused(self):
        problems = run(FakeWesley(version="0.4.0"))
        self.assertEqual(len(problems), 1)
        self.assertIn("pinned", problems[0])

    def test_the_recorded_identity_names_the_pinned_wesley(self):
        record = json.loads((ROOT / "typepacks" / "issue-dag@2" / "WESLEY.json").read_text())
        self.assertEqual((record["version"], record["commit"]), (check.PINNED_VERSION, check.PINNED_COMMIT))
        self.assertEqual(check.law_schema_hash((ROOT / "typepacks" / "issue-dag@2" / "laws.weslaw.yaml").read_text()),
                         record["schema_hash"])

    def test_no_document_calls_the_typepack_unvalidated(self):
        # Phrases that call the typepack unchecked; "unvalidated" elsewhere (e.g. run parameters) is fine.
        stale = re.compile(r"(?i)unvalidated\s+(?:sketch|typepack|shape|laws)|typepack[^.]*\bunvalidated\b|\(unvalidated\)|not\s+been\s+run\s+through\s+Wesley|sha256:not-computed")  # a phrase may wrap
        for path in sorted(ROOT.rglob("*")):
            if path.is_file() and path.suffix in (".md", ".graphql", ".yaml", ".json") and ".git" not in path.parts:
                with self.subTest(str(path.relative_to(ROOT))):
                    self.assertIsNone(stale.search(path.read_text()), "the typepack is validated now")


if __name__ == "__main__":
    unittest.main()
