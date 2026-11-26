# Contributing

Thank you for helping. This repository is the specification of the `issue-dag` formats, their
planning profiles and their version policy. Changes to it change what two independent
implementations must agree on, so they follow a few rules.

## How a change lands

- Open a pull request. Nothing is pushed to `main`.
- A normative statement carries a label (such as `C3` or `G4`); everything else is informative.
  Keep that separation: never put a requirement in commentary.
- A conformance case tests only rules that have a normative statement here (`versions.md` A9):
  a case is evidence for a rule, never its definition. When you add or change a rule the corpus
  can test, adding a case for it is welcome.
- A change that alters how an existing document is read is a new version, judged under
  [Versions and compatibility](versions.md), not an edit in place.
- If the reference implementation behaves differently, record the difference in
  [notes/python-differences.md](notes/python-differences.md); do not silently pick a side.

## Checks

- `python3 -m unittest discover -s tests` runs the offline tests.
- `python3 scripts/check_typepack.py --wesley <path>` checks the typepack with the pinned Wesley
  (see `typepacks/issue-dag@2/WESLEY.json`). CI builds that Wesley and runs it.

## License

By contributing you agree that your contribution is licensed under the
[Apache License 2.0](LICENSE).
