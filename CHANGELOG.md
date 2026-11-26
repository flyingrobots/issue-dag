# Changelog

Changes to the `issue-dag` specification: the format, its planning profiles, the admission policy,
the observation bundle and the conformance corpus. The corpus digest of each change is recorded in
`corpus/DIGEST` and in the version table of `versions.md`. Changes before
flyingrobots/taskalisk#110 are not recorded here; see the history of this repository.

## Unreleased

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
