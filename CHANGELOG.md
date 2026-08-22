# Changelog

## 2.0.0 - Unreleased

### Changed

1. Replaced the single phase worker with sequential, context-isolated test,
   implementation, verification, conditional remediation and re-verification,
   and documentation stages.
2. Added stage-specific parent-owned commit gates, exact-path staging, dirty
   baseline protection, and manifest tracking for `--no-commit` runs.
3. Made verification independent and read-only, limited remediation to two
   attempts, and required fresh verification before documentation.
4. Added workflow-completion and next-stage parser state so checked phases with
   missing verified documentation resume safely.
5. Upgraded the phase handoff contract to v2 with stage, prior-state,
   validation-expectation, expected-failure, and scope data.
6. Added a durable workflow-complete phase-document marker and aggregate staged
   execution record.
7. Required implementation workers to pass tests authored by the preceding test
   stage, when present, and any other relevant phase-scoped tests; added scoped
   expected-RED completion for test-authoring-only phases; and made official
   implementation discipline mandatory in both stages.
8. Replaced the nonexistent stage-report schema assumption with a lightweight
   required-field contract and deferred remediation commits until fresh
   re-verification passes.
9. Added a fresh read-only pre-phase regression baseline, typed verifier
   attribution, parent-owned finding dispositions, strict pre-existing
   regression comparison, and conservative downstream-safety checks.
10. Routed unresolved implementation and every remediation result through fresh
    verification, and deferred the exact accumulated implementation/remediation
    commit until a phase-safe verdict.
11. Kept remediation-cycle and commit-control state parent-only, and clarified
    that test and remediation workers may iterate on in-scope failures before
    returning their final stage reports; handoffs now carry validation
    expectations without pre-populated current-stage results or verdicts, and
    omit parent-owned selector, phase-lifecycle, and queue state. Provisional
    non-verifier findings now pass unchanged into verification, while
    remediation accepts only verifier-classified findings.

## 1.0.0 - 2026-06-03

### Added

1. Initial `speckit.phase-orchestrator.phase` command.
2. Support for `next`, `phase <number>`, and `all` prompt modes.
3. `tasks.md` phase parser.
4. Phase handoff example.
5. Six-phase sample `tasks.md`.
6. Documentation for agent-agnostic usage.
