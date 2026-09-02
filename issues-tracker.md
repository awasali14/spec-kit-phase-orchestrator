# Phase Orchestrator Development Issues Tracker

This Git-tracked document preserves engineering decisions and their evidence.
It is development material, excluded from installed extension payloads through
`.extensionignore`. Release-facing summaries belong in `CHANGELOG.md`.

## Current Extension Direction

These are the authoritative development principles for current work.

1. Analyze the complete `tasks.md`, but keep every worker scoped to one phase
   and one role.
2. Treat named validation commands as minimum coverage. Discover changed or
   removed behavior and verify complete bounded suites for all affected
   subsystems, recording exclusions as caveats.
3. Decide scope before origin: remediate a proven, repairable in-phase issue
   even when baseline evidence is incomplete, then use comparable baseline
   evidence for origin attribution and deferral.
4. Keep baseline and verification workers independent and read-only. The first
   verifier establishes an expanded verification surface that all later
   verifiers must preserve.
5. Prefer an already-authorized outside-sandbox route for project validation;
   otherwise run inside and escalate only plausible environment restrictions.
   Environment blockers are not product defects and do not consume remediation.
6. Keep Git operations and the two-attempt remediation cap parent-owned. Keep
   report and handoff wire schemas at `2.0.0` until their shapes change.
7. Preserve resolved issues and historical decisions. Add a superseding entry
   instead of deleting or rewriting history.

## Issue Index

| ID | Date | Status | Affected stage | Summary | Resolution reference |
| --- | --- | --- | --- | --- | --- |
| PO-001 | 2026-08-27 | Addressed | Baseline, verification, routing | Baseline impact analysis and first verification were too narrow; baseline evidence incorrectly took precedence over in-phase remediation. | Phase Orchestrator 2.1.0 reliability update; `PO-001` record below |
| PO-002 | 2026-08-27 | Addressed | All validation-running stages | Sandbox restrictions could be misclassified as code failures or consume remediation attempts. | Phase Orchestrator 2.1.0 validation environment policy; `PO-002` record below |

Allowed statuses are `Open`, `Addressed`, and `Validated`.

## Issue Records

### PO-001 — Complete impact analysis and scope-first remediation

- **Status:** Addressed
- **Source session:** [Stopped Phase 1 workflow and follow-up analysis](codex://threads/01a03edc-12c2-7be3-85c4-29bdc6f52cc2),
  reviewed on 2026-08-27.
- **Observed behavior:** Baseline workers could select only obvious or named
  commands, the first verifier could stop after narrow gates, and missing
  comparable baseline evidence could block repair of an otherwise proven
  in-phase defect.
- **Root cause:** The contract treated `tasks.md` commands as sufficient,
  emphasized baseline origin attribution before repair scope, and did not make
  the affected-subsystem suite a durable re-verification requirement.
- **Extension gap:** No explicit caller/reference/fixture/parameterization
  discovery, no requirement to continue safe planned commands and aggregate
  failures, and no explicit allowance for in-phase remediation with null
  baseline evidence.
- **Decision:** Treat task commands as minimum coverage; map and run complete
  bounded affected-subsystem suites; preserve that expanded surface through
  re-verification; decide scope before attribution; require baseline evidence
  only for `phase_introduced_regression` and deferral.
- **Changes:** Updated the baseline and verification worker instructions,
  parent routing precedence, report-schema condition, documentation, and
  regression tests without changing report or handoff fields.
- **Validation evidence:** The report schema accepts a confirmed
  `phase_scoped_failure` with `baseline_evidence: null` and remediation, rejects
  `phase_introduced_regression` without baseline evidence, and the documentation
  contract tests assert expanded discovery and preserved re-verification.
- **Regression guard:** `tests/test_phase_tasks.py` checks discovery terms,
  complete affected-suite coverage, aggregation, scope-first precedence, null
  baseline remediation, and required regression baseline evidence.

### PO-002 — Deterministic sandbox-aware validation

- **Status:** Addressed
- **Source session:** [Phase Orchestrator 2.1.0 reliability implementation](codex://threads/01a04208-7997-7d62-9b77-f389d89a6760),
  reviewed on 2026-08-27.
- **Observed behavior:** A project validation command blocked by sandbox
  filesystem, socket, network, service, database, container, subprocess, or
  termination restrictions could be reported as a code regression or spend a
  remediation attempt.
- **Root cause:** Worker handoffs recommended non-writing execution but lacked
  a deterministic outside-first, inside-fallback, exact-rerun policy.
- **Extension gap:** The parent had no required route for permission escalation,
  authoritative outside results, denied-permission blockers, or attempt
  accounting.
- **Decision:** Prefer an already-authorized outside route; otherwise run the
  exact command inside. Use ordinary product results normally. For a plausible
  sandbox restriction, the worker requests permission and performs the exact
  outside rerun before returning. If the worker cannot obtain permission, the
  parent asks the user and relaunches a fresh worker for the same stage when
  approved. Only a denied or still-unavailable parent request returns an
  environment blocker. Verifiers own `block`; all other workers keep
  `disposition: null`. Neither the blocker nor relaunch consumes remediation.
- **Changes:** Added the policy to every validation-running worker handoff and
  parent execution/routing contract; documentation workers remain unaffected.
- **Validation evidence:** Contract tests assert policy propagation, exact
  outside reruns before defect attribution, environment recording,
  stage-specific disposition ownership, parent relaunch, and denied permission
  behavior.
- **Regression guard:** `tests/test_phase_tasks.py` checks all five
  validation-running roles and parent routing language.

## Direction History

- **2026-08-27 — Scope before origin.** A proven, repairable in-phase issue is
  remediated before baseline origin attribution. This supersedes the earlier
  direction that missing or non-comparable baseline evidence always produced an
  inconclusive blocker.
- **2026-08-27 — Complete affected-subsystem verification.** Initial and later
  verification cover complete bounded affected subsystems. This supersedes the
  earlier focused/independent/baseline-only minimum.
- **2026-08-27 — Outside-first with deterministic fallback.** Already-authorized
  outside execution is preferred, sandbox execution is the immediate fallback,
  and only plausible environment failures trigger an exact outside rerun. This
  supersedes undifferentiated validation failure handling.

## Open Follow-ups

- Promote `PO-001` to `Validated` only after a real orchestrator run proves the
  initial verifier discovers the complete affected surface and a proven
  in-phase issue proceeds to remediation despite missing baseline evidence.
- Promote `PO-002` to `Validated` only after production-style runs prove both
  sandbox failure paths: approved worker permission produces an authoritative
  exact outside rerun; when worker approval is unavailable, parent permission
  relaunches the same stage; and denied parent permission produces an
  environment blocker without consuming a remediation attempt.
- Run the final `v2.1.0` release-archive installation test after the tag exists,
  confirming the installed payload excludes this tracker and other development
  files.
- Repeat manual production integration tests on supported agents with at least
  one real sandbox-denied outside rerun path; record results without rewriting
  the decisions above.
