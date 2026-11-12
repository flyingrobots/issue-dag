# Differences between the `/2` specification and the Python compiler

This note is informative. It lists every known difference between the `/2`
documents of this repository and the reference implementation, the Python
Taskalisk compiler at `flyingrobots/taskalisk@8e4cb73`
(`skills/taskalisk/scripts/taskalisk.py`). The corpus work
(`flyingrobots/taskalisk#26`) classifies each one as intended legacy
behaviour (the rule changes to match), a defect (the implementation is
wrong), or a compatibility exception (recorded with its scope). Until then
the specification states the rule and this note records the difference.

Differences 1 to 7 were observed on 2026-11-12 by calling the compiler's
parser and validator on constructed bodies, and difference 9 by running the
compiler against its offline fake. Differences 8 and 10 to 15 come from
reading the code.

None of these differences changes the verdict on any document in the
[census of 2026-11-12](../evidence/2026-11-12-frontmatter-shapes.md): the
specification and the Python accept the same 282 documents.

## Format

| # | Input | Specification | Python | Rule |
| --- | --- | --- | --- | --- |
| 1 | A container with `.blocked_by: []`, `.blocked_by: 0` or an empty `.blocked_by:` | Invalid | Valid: it tests whether the value is falsy, not whether the key is present | V6 |
| 2 | A container with a `.type` outside the enum, such as `.type: zzz` | Invalid | Valid: `.type` is not checked on a container | V6 |
| 3 | `.size_hours`, a reference number or a meter count above 2147483647 | Invalid | Valid: integers are unbounded | L1, L3, L4 |
| 4 | A CR not followed by LF, or U+000B, U+000C, U+001C to U+001E, U+0085, U+2028 or U+2029, inside the block | Invalid | Each is a line break (`str.splitlines`); the result depends on the pieces | C4 |
| 5 | Unicode whitespace other than SP, HT, CR and LF, such as U+00A0, before the opening fence, in a blank line, before a comment or around a value | An ordinary character: before the fence, the body has no frontmatter; elsewhere, part of the line | Whitespace (`\s`, `str.strip`) | C1, C5, C6 |
| 6 | A list item spelled as an integer, such as `.holds: [007]` | The item is the string `007` | The item becomes `7` (`str(int(...))`); `-0` becomes `0` | C8 |
| 7 | A list as the value of `.dag`, `.kind`, `.type` or `.status`, such as `.type: [bug]` | Invalid | The validator raises `TypeError`; the run ends with a traceback and no outcome | V1, V4, V5, V8 |
| 8 | An item of `.blocked_by` or `.children` equal to the issue's address but not to its `.id`, or the reverse | V7 compares with `.id`; X1 reports the address mismatch | The self-reference check compares with the address | V7, X1 |

Difference 1 is the one Decision 7 of the Taskalisk decision record names:
the rule as written stands, and the Python's behaviour is a defect. Difference
8 changes only which message an already invalid document receives.

## Planning profile

| # | Situation | Specification | Python | Rule |
| --- | --- | --- | --- | --- |
| 9 | A document names, in `.blocked_by`, an open issue of the home repository that has no frontmatter, in a run without roots | The issue is an opaque node; the dependent is blocked | The issue is listed as unmodeled and is not a node; the dependent's prerequisite is unknown and the run is invalid | D7, X3 |
| 10 | A `.blocked_by` lists the same closed `not_planned` prerequisite twice | One pair listed for review | One pair per occurrence | G3 |

Difference 9 also contradicts `docs/frontmatter-model.md` in Taskalisk,
which says a referenced issue without frontmatter becomes an opaque node. The
specification follows the written rule. It was observed by running the
compiler against the offline fake (`tests/fake_gh.py`) on 2026-11-12: exit 1,
`Unresolved prerequisites`.

## Edge edit

| # | Behaviour | Contract | Python | Rule |
| --- | --- | --- | --- | --- |
| 11 | Order of validation and write | Validate the edited graph in memory, then write | Write the new body, then recompile | E6 |
| 12 | After a failed recompile | Nothing to undo: nothing was written | Write the old body back, which can overwrite a newer edit | E9 |
| 13 | Final reread before the write | Required | Absent | E7 |
| 14 | Writer identity | Checked against the trust policy | Not checked | E7 |
| 15 | Line ends of the block on rewrite | Unchanged | Every line of the block is rejoined with LF | E4 |

Differences 11 to 14 are the subject of `flyingrobots/taskalisk#1`.

## Outside the profile

The Python's `--verify-dag` mode, which compiles a hand-written JSON graph
with soft edges, confidence thresholds and `(merged)` hints, and its
`--repo` inventory mode are not part of the format or the profile. Neither
reads issue frontmatter.
