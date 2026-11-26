# Changelog

Changes to the `issue-dag` specification: the format, its planning profiles, the admission policy,
the observation bundle and the conformance corpus. The corpus digest of each change is recorded in
`corpus/DIGEST` and in the version table of `versions.md`. Changes before
flyingrobots/taskalisk#110 are not recorded here; see the history of this repository.

## Unreleased

### Added

- **Which part of a reference was not found** (flyingrobots/taskalisk#126).
  - OB17 (new): the unavailable slot of an issue that resolves to no issue may hold `not_found`,
    one of `owner`, `repository` and `number`, beside its reason. A reader rejects another value,
    and `not_found` anywhere else. A slot without it records no cause, as before. The cause is
    `not_found` alone, never read out of the reason. OB4 and OB8 point to it.
  - D10: the run is incomplete whatever the cause. D11 to D13 (new) name the causes: owner,
    repository and issue number not found. A cause is no finding. A private repository looks the
    same as a missing one, which is why D10 does not make it a finding (commentary).
  - OB16: an incomplete run also reports the cause of the slot with the least reason; of slots with
    that reason, no cause first, then by the bytes of the value.
  - F5: findings with one identity are one finding, so a task that names the same unknown
    prerequisite twice receives one X3 finding.
  - CC6: the member `cause` (`D11`, `D12`, `D13` or null), in normative cases only. A
    characterisation case lists X3 as often as the implementation reports it. CC8: findings compare
    as lists with repeats.
  - Cases `graph/d11-owner-not-found`, `graph/d12-repository-not-found`,
    `graph/d13-issue-number-not-found`, `graph/d10-not-found-with-no-cause`,
    `graph/d13-cause-is-not-read-from-the-reason`, `graph/d12-not-found-named-by-two-documents`,
    `graph/ob16-least-cause-of-one-reason`, `graph/ob16-no-cause-before-a-cause` and
    `graph/ob16-cause-goes-with-the-least-reason` (the last three also `-roots-reversed`), and
    `graph/x3-unknown-prerequisite-named-twice`. The Python differs on twelve: it reports no reason
    and no cause (difference 26, extended), and one X3 per occurrence (difference 27, new; both
    compatibility exceptions).
  - Corpus digest `sha256:4f008167c292e543961fbdd3604bfc96267323e86ce52fa37c5ccccb22674ab3`.

- **Which lookup a run reports when several could not be made** (flyingrobots/taskalisk#117).
  - OB16 (new): a run over a bundle reads every slot the rules reach; a missing slot (OB5) is
    reported before an unavailable one; of missing slots, the least path from `observations`
    (member name by member name, in UTF-8 bytes); of unavailable slots, the least reason. Draft
    flags (S2) are reached only when discovery and admission made every lookup, and then all are
    read. The order of the roots never changes the slot reported.
  - OB8: an issue's `body` member may be absent when the run does not read it (OB14).
  - CC6: the outcome `unusable` for a bundle that lacks a slot the run reads, with `missing`, the
    slot reported as a path from `observations`; and `unavailable`, the reason an incomplete run
    reports, in normative cases only. Only a normative case and its twin may expect `unusable`.
  - Cases `graph/ob16-missing-over-unavailable`, `graph/ob16-least-of-two-missing`,
    `graph/ob16-missing-codeowners-before-missing-issue`, `graph/ob16-least-of-two-unavailable`,
    `graph/ob16-least-draft-flag-on-the-last-node`, `graph/ob16-least-draft-flag-on-the-first-node`,
    `graph/ob16-unavailable-issue-before-draft-flag`, `graph/ob16-missing-issue-before-a-later-body`,
    `graph/ob16-missing-pull-requests-before-missing-issue`,
    `graph/ob16-missing-codeowners-before-missing-pull-requests` and
    `graph/ob16-least-of-two-permissions`, each also with `-roots-reversed`. The Python differs on
    sixteen (differences 25 and 26, compatibility exceptions): it stops at the first lookup it
    cannot make and reports no recorded reason.
  - Corpus digest `sha256:5d8d5e863206acbbf6cf1e3aab5afaf4d9131cca85554c3e56e554a3d955598e`.

### Changed

- **Profile and bundle gaps found by the Rust graph core** (flyingrobots/taskalisk#110).
  - I4, I5: a pull request's draft flag is required only when S2 reads it, for a linked pull
    request of an open node; a pull request that closes no open node never makes the run
    incomplete through its draft flag. Case `graph/i5-draft-flag-of-a-pull-request-closing-no-node`;
    the Python differs (difference 23, defect).
  - D8: a key repeated under C7 contributes no reference to discovery, so a repeated `.blocked_by`
    naming an unavailable issue gives an invalid run, not an incomplete one. Case
    `graph/d8-repeated-blocked-by-is-not-followed`; the Python differs (difference 24, defect).
  - AD3, AD4: the bot prefix `app/` and suffix `[bot]` match without regard to ASCII case, in
    logins and in allowlist entries, as the Python does. Cases `graph/ad3-bot-suffix-ignores-case`,
    `graph/ad3-app-prefix-ignores-case`, `graph/ad3-app-prefix-in-any-case-is-a-bot` and
    `graph/ad4-entry-suffix-ignores-case` and `graph/ad4-entry-prefix-ignores-case`.
  - OB1, OB15 (new): an object that gives a member twice, at any depth, or an `observations`
    member outside those OB6 to OB11 define, makes the bundle invalid. The corpus cannot hold an
    invalid bundle, so these rules have no case.
  - CC6: `unknown_capacity` and each skip's `semaphores` name each semaphore once, in ascending
    order of UTF-8 bytes. Case `graph/b3-names-in-byte-order`.
  - The title of each `--python` twin states what the compiler does (its disagreement note), not
    the normative claim it disagrees with.
  - Corpus digest `sha256:aed5aeaa3f09b4a22da06a3c41184e25f1d0f0ac4dd465ccd2345866b102a543`.
