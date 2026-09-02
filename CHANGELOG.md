# Changelog

## 2.1.0 - Unreleased

### Changed

1. Expanded baseline discovery from named commands to callers, references,
   fixtures, parameterizations, tests, and complete bounded suites for every
   affected subsystem, with explicit caveats for excluded surfaces.
2. Required the first verifier to analyze the actual phase diff, complete all
   safe planned validation, aggregate related in-phase failures, and preserve
   the expanded verification surface through every remediation cycle.
3. Made repair scope precede origin attribution so proven in-phase failures and
   defective tests can be remediated with incomplete baseline evidence, while
   requiring comparable baseline evidence for
   `phase_introduced_regression` and deferral.
4. Added deterministic validation execution policy: prefer an authorized
   outside-sandbox route, fall back to the exact sandbox command, and require an
   authoritative outside rerun before attributing a plausible sandbox failure
   to product code. When a worker cannot obtain approval, the parent requests
   permission and relaunches a fresh worker for the same stage. Only a denied or
   still-unavailable parent request becomes an environment blocker; neither the
   blocker nor relaunch consumes a remediation attempt.
5. Added the Git-tracked development `issues-tracker.md`, excluded it from the
   installed extension payload, and documented that publication boundary.
6. Kept the workflow-completion marker at `v2` and the unchanged report and
   handoff wire contracts at schema version `2.0.0`.

## 2.0.0 - Superseded pre-release

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
8. Added a dedicated Draft 2020-12 worker-report schema, stage-specific report
   forms in every handoff, and parent validation against the assignment and
   observed manifest before reports are trusted.
9. Added a fresh read-only pre-phase regression baseline, typed verifier
   attribution, parent-owned finding dispositions, strict pre-existing
   regression comparison, and conservative downstream-safety checks.
10. Routed unresolved implementation and every remediation result through fresh
    verification, while recording implementation and each scope-clean
    remediation stage as separate reversible progress commits.
11. Kept remediation-cycle and commit-control state parent-only, and clarified
    that test and remediation workers may iterate on in-scope failures before
    returning their final stage reports; handoffs now carry validation
    expectations without pre-populated current-stage results or verdicts, and
    omit parent-owned selector, phase-lifecycle, and queue state. Provisional
    non-verifier findings now pass unchanged into verification, while
    remediation accepts only verifier-classified findings.
12. Formalized per-stage commit eligibility, including valid `unresolved`
    implementation/remediation checkpoints, a maximum normal history of five
    commits, and unchanged `--no-commit` and read-only-stage behavior.
13. Added inclusive `phase <start> to <end>` execution with contiguous-range
    validation, checkbox-only predecessor acceptance, a fixed ending boundary,
    and workflow-complete gating for every selected phase.
14. Required parent-only analysis of the complete `tasks.md` before planning or
    launching workers in every invocation mode.

## 1.0.0 - 2026-06-03

### Added

1. Initial `speckit.phase-orchestrator.phase` command.
2. Support for `next`, `phase <number>`, and `all` prompt modes.
3. `tasks.md` phase parser.
4. Phase handoff example.
5. Six-phase sample `tasks.md`.
6. Documentation for agent-agnostic usage.
