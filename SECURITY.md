# Security

This repository holds a specification, not running code. A security problem here is a rule that lets
a conforming implementation be misled: for example, a carrier or reference rule that two readers can
decode differently, a trust or admission rule that admits text it should not, or an edge-edit rule
that can lose a concurrent edit without saying so.

## Reporting

Report it privately through GitHub's **Report a vulnerability** form on this repository's Security
tab. Do not open a public issue for it. Say which rule (by its label, such as `C2` or `E6a`) and give
a document or observation bundle that shows the problem.

You can expect an answer within a week. A fix lands as a change to the rule, with a conformance case
that holds it, and the version table says whether documents are affected.

## Scope

The reference implementation, Taskalisk, has its own threat model and security policy in
[flyingrobots/taskalisk](https://github.com/flyingrobots/taskalisk) (`docs/threat-model.md`).
