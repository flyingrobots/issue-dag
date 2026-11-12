# Census of frontmatter shapes, 2026-11-12

This record is informative. It lists every distinct shape of frontmatter block
found in five repositories, with the verdict of
[`issue-dag/2`](../formats/issue-dag-2.md) on each and the rules that decide it.

## Method

On 2026-11-12 every issue of `flyingrobots/taskalisk`, `flyingrobots/geordi`,
`flyingrobots/echo`, `flyingrobots/bunny` and `git-stunts/git-warp` was
listed in every state, at most 600 per repository, with `gh issue list`. These
are the five repositories of the measurement of 2026-11-10, which found 237
documents. All five are public.

| Repository | Issues listed |
| --- | --- |
| `flyingrobots/taskalisk` | 31 |
| `flyingrobots/geordi` | 110 |
| `flyingrobots/echo` | 520 |
| `flyingrobots/bunny` | 179 |
| `git-stunts/git-warp` | 600 (the limit; older issues were not read) |
| Total | 1,440 |

282 of the 1,440 bodies have a frontmatter block. The other 1,158 have none
under rules C1 to C3; the specification and the Python compiler agree on
which bodies have a block.

A *shape* is the set of the following features of one block: for each format
key, the form of its value (a bare string, an integer, an empty list or a
non-empty list); for free keys, the same forms; and the presence of comment
lines, blank lines, indented lines, quoted values or lines of another form.
Every block was then judged twice: by the Python compiler's parser and
validator at `flyingrobots/taskalisk@8e4cb73`, and by a separate reading
written from this specification's text alone. The two verdicts agreed on all
282 documents.

## Features common to every block

- The body begins with the opening fence, with nothing before it.
- Lines end in LF.
- The opening fence is exactly `` ```yaml ``.
- `.dag` is the first line, and its value is `issue-dag/2`.
- No line is indented, quoted, blank or a comment.
- Every reference has the form of rule L1 and matches its issue (X1).
- No container has `.blocked_by` or `.type`.

## Shapes

Value forms: *s* a bare string, *i* an integer, *[]* an empty list, *[…]* a
non-empty list. A free value marked *s#* contains a `#`.

| Count | `.kind` | Format keys and value forms | Free keys | Verdict | Deciding rules |
| ---: | --- | --- | --- | --- | --- |
| 78 | task | `.type` s, `.blocked_by` […], `.size_hours` i | s | Valid | V5, V8, M3 |
| 62 | task | `.type` s, `.blocked_by` […] | none | Valid | V5 |
| 61 | task | `.type` s, `.blocked_by` [] | none | Valid | V5 (an empty list is present) |
| 26 | task | `.type` s, `.blocked_by` […], `.size_hours` i | none | Valid | V5, V8 |
| 12 | task | `.type` s, `.blocked_by` [] | s, s#, […] | Valid | V5, M3, C5 (`#` inside a value is not a comment) |
| 8 | container | `.children` […] | s | Valid | V6, M3 |
| 6 | task | `.type` s, `.blocked_by` [], `.size_hours` i | s | Valid | V5, V8, M3 |
| 6 | task | `.type` s, `.blocked_by` […] | s, […] | Valid | V5, M3 |
| 5 | task | `.type` s, `.blocked_by` [], `.size_hours` i | none | Valid | V5, V8 |
| 4 | task | `.type` s, `.blocked_by` [] | s, […] | Valid | V5, M3 |
| 4 | task | `.type` s, `.blocked_by` [] | s, s# | Valid | V5, M3, C5 |
| 3 | task | `.type` s, `.blocked_by` [] | s | Valid | V5, M3 |
| 3 | task | `.type` s, `.blocked_by` […], `.holds` […] | none | Valid | V5, V8, L2 |
| 1 | task | `.type` s, `.blocked_by` […] | s | Valid | V5, M3 |
| 1 | container | `.children` […] | none | Valid | V6 |
| 1 | task | `.type` s, `.blocked_by` […], `.size_hours` i, `.status` s | none | Valid | V5, V8 |
| 1 | task | `.type` s, `.blocked_by` [], `.holds` […] | none | Valid | V5, V8, L2 |
| **282** | | | | **all valid** | |

Every block also satisfies C1, C2, C6, C7, V1, V2, V3, V4 and V7. The largest
`.size_hours` is 24, well inside L4, and is the one block that receives the
V10 warning. The free keys in use are `area`, `source` and `related`.

## Limits

- The 237 documents of 2026-11-10 are not separately identified. The census
  covers the same repositories two days later; an issue edited in between is
  judged as it is now.
- The git-warp listing reached its limit of 600; older issues there were not
  read. Repositories outside these five were not read.
- A shape records value forms, not values. Rules that depend on a value, such
  as L1 for each reference and X1, were checked per document by both readers,
  not by the shape.
