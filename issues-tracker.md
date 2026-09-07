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
8. Keep parent orchestration policy separate from direct worker instructions,
   and use installed `.specify/extensions/phase-orchestrator/` paths for
   extension-internal files referenced by runtime commands and templates.

9. Keep the parser structural and give the parent full task-classification
   authority. Classify by primary deliverable, record a short rationale, and
   validate exact assignment coverage mechanically. Reuse durable assignments
   on resume, with explicit revisions and completion reconciliation when a
   mistake or source change requires correction. Validation commands do not
   determine a task's role or substitute for its requested deliverable.

## Issue Index

| ID | Date | Status | Affected stage | Summary | Resolution reference |
| --- | --- | --- | --- | --- | --- |
| PO-001 | 2026-08-27 | Closed | Baseline, verification, routing | Baseline impact analysis and first verification were too narrow; baseline evidence incorrectly took precedence over in-phase remediation. | Phase Orchestrator 2.1.0 reliability update; `PO-001` record below |
| PO-002 | 2026-08-27 | Closed | All validation-running stages | Sandbox restrictions could be misclassified as code failures or consume remediation attempts. | Phase Orchestrator 2.1.0 validation environment policy; `PO-002` record below |
| PO-003 | 2026-09-02 | Closed | Handoffs, validation routing, verification | Compressed wording blurred parent/worker instructions, parent permission ordering, and the evidence requirement for phase-introduced regressions. | `PO-003` record below |
| PO-004 | 2026-09-02 | Closed | Runtime extension references | Agent-facing contracts mixed source-repository-relative paths with installed extension paths. | `PO-004` record below |
| PO-005 | 2026-09-03 | Open | Baseline, test, validation environment routing, parent transition | Sandbox-specific test hangs were treated as one confirmed pre-existing non-environment failure after the outside baseline rerun failed before collection. | Open; sandbox specificity confirmed, stronger-model orchestration rerun and narrow extension refinement pending |

| PO-006 | 2026-09-07 | Closed | Parser, parent classification, task dispatch, resume | T010 migration was routed as test work because its verification command named a test file; parser classification overrode the parent's correct interpretation. | Structural inventory plus parent-owned assignments implemented; 89 tests passed; live orchestration validation pending |

Allowed statuses are `Open` and `Closed`.

## Issue Records

### PO-001 — Complete impact analysis and scope-first remediation

- **Status:** Closed
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

- **Status:** Closed
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

### PO-003 — Explicit parent, worker, and transition wording

- **Status:** Closed
- **Source:** Production-test follow-up prompt review on 2026-09-02.
- **Observed behavior:** “Append the complete policy” could be read as copying
  parent-facing numbered rules verbatim into a worker prompt; the environment
  stop condition could be read as allowing the parent to stop before requesting
  user authorization; and “`phase_introduced_regression` may not” omitted what
  was prohibited and could be mistaken for a remediation restriction.
- **Root cause:** Concise wording crossed role boundaries, left permission
  ordering implicit in a final boolean condition, and used an elided comparison
  in the verification report guidance.
- **Decision:** The orchestrator appends the direct worker-facing validation
  block, never its numbered parent policy. A parent-level authorization request
  is mandatory before an environment blocker may stop the workflow. A
  `phase_introduced_regression` requires comparable non-null baseline evidence
  but remains remediable when its repair is in scope.
- **Changes:** Named the exact worker-facing block and prohibited verbatim use
  of the parent policy; made the authorization-before-stop sequence explicit;
  replaced the ambiguous “may not” sentence with an explicit evidence rule and
  in-scope remediation outcome.
- **Clarified existing behavior:** A sandbox-related `blocked` test report
  enters the parent authorization and same-stage relaunch path. A final
  non-environment test failure stops only after the parent validates evidence
  that the focused gate is neither green nor eligible expected RED. These two
  points required explanation but no contract change.
- **Validation evidence:** Manually reviewed the complete handoff builder,
  parent validation policy, test gate, verifier role, worker-facing environment
  block, structured report guidance, and disposition ownership together.
  Existing string-based contract tests cannot establish that this wording is
  interpreted with the intended role and transition semantics.
- **Regression guard:** Review generated worker prompts and parent transitions
  semantically whenever these sections change; automated phrase checks remain
  supplementary only.

### PO-004 — Installed paths in runtime agent contracts

- **Status:** Closed
- **Source:** Runtime-reference audit prompted by the 2026-09-02 wording review.
- **Observed behavior:** A draft handoff instruction initially named the source
  path `references/worker-prompt-template.md` instead of its installed path. A
  wider audit found the same existing pattern for the handoff/report schemas and
  for Mermaid-style and parser references in the phase-document template.
- **Root cause:** Runtime agent instructions and source-repository documentation
  used the same shorthand even though their path roots differ after extension
  installation.
- **Decision:** Commands and reference templates executed or read in a target
  project use `.specify/extensions/phase-orchestrator/` paths for internal
  extension files. Development plans, repository documentation, tests, and
  source examples may retain source-relative paths when they describe this
  repository rather than an installed runtime.
- **Changes:** Corrected the orchestrator’s worker-template, handoff-schema, and
  report-schema references and the phase-document template’s Mermaid-style and
  parser references. Left source-oriented documentation unchanged.
- **Validation evidence:** Audited extension-internal path references across
  commands, worker/document templates, schemas, documentation, examples, tests,
  and publication material; classified each occurrence by runtime versus source
  context before editing.
- **Regression guard:** Repeat the runtime/source classification during prompt
  reviews and verify installed paths in the release-archive installation test.

### PO-005 — Ambiguous hang attribution stopped the workflow without a comparable outside result

- **Status:** Open
- **Source session:** Phase 1 production-style orchestration using a GPT-5.6 Sol
  parent at medium reasoning effort and isolated GPT-5.6 Terra workers at max
  reasoning effort, reviewed on 2026-09-03.
- **Run locator:** Source branch `codex/phase-orchestrator-sol-terra-v210` at
  commit `90a7376110a89755556838ac534cca94218e9e5c`. The actual Codex run used the
  detached worktree `/home/awasali14/.codex/worktrees/f011/backend` at that same
  commit; the named branch is checked out separately at
  `/home/awasali14/worktrees/backend-phase-orchestrator-sol-terra-v210`.
- **Audited prompt artifacts:** The run's exact v2.1.0 prompts are preserved in
  the detached run worktree under `Documentation/worker-prompts/`:
  `master-invoke-prompt-sol-medium-terra-max-v2.1.0.txt`,
  `phase-1-baseline-verification-v2.1.0.txt`,
  `phase-1-test-v2.1.0.txt`, and
  `phase-1-test-retry-1-v2.1.0.txt`. The original and retry test assignments
  have the same SHA-256 digest,
  `b56828a3cff29d5b85fd29af734acd0c01a07c77dff214322967806c416db42d`.
- **Observed behavior:** The read-only baseline recorded an authenticated Apply
  test hanging inside the Codex sandbox at
  `TestValidation::test_missing_body_fields`, with the stack waiting in the
  `SyncASGIClient` event loop. Its attempted outside-sandbox rerun launched
  pytest but failed during output-capture initialization with
  `FileNotFoundError`, before test collection or execution. The result was
  therefore unavailable and non-comparable, and the baseline correctly
  continued because baseline evidence is not a passing gate. During the later
  Phase 1 test stage, a different authenticated Apply test,
  `TestAuthFailures::test_non_uuid_sub_returns_401`, hung inside the sandbox.
  The worker classified it as a confirmed pre-existing unrelated regression,
  and the parent accepted the report and stopped the workflow under the
  ordinary non-environment test-failure branch. The exact later command was
  never successfully rerun outside the sandbox.
- **Follow-up evidence (2026-09-03):** Controlled read-only reruns used
  `PYTHONDONTWRITEBYTECODE=1`, disabled the pytest cache, bounded each process,
  and preserved identical Git/index/cache fingerprints. Outside the Codex
  sandbox, `TestValidation::test_missing_body_fields` passed in 0.16 seconds,
  `TestAuthFailures::test_non_uuid_sub_returns_401` passed in 0.15 seconds, and
  the complete T001 command finished in 2.08 seconds with 25 passed, 9 skipped,
  and only the 4 intentional pre-T002 failures. Inside the sandbox, each
  isolated test collected and then hung; faulthandler showed the same
  `asyncio.run()`/AnyIO worker-wait pattern, and each bounded process required
  termination. This confirms the observed hangs are sandbox-specific for these
  controlled runs and are not ordinary code regressions.
- **Primary attribution:** Shared model/orchestration judgment failure across
  both roles. The Terra-max test worker strengthened “same client/event-loop
  hang class” into “confirmed pre-existing unrelated regression” even though
  the failing test identities differed and no comparable outside result
  existed. The Sol-medium parent independently owned the transition and
  cross-evidence gate, but accepted that classification instead of rejecting
  the report's confirmed attribution or treating it as uncertain and requesting
  a fresh diagnostic outside run. The worker supplied the faulty
  classification; the parent failed to catch it and selected the stopping
  branch. Today's controlled comparison confirms that their combined decision
  was technically wrong and caused a valid workflow to stop. It does not by
  itself prove that the named model selection, rather than these particular
  reasoning instances, is generally responsible.
- **Responsibility split:** Test worker—unsupported technical attribution and
  failure to enter the environment-blocker/outside-rerun path. Parent
  orchestrator—insufficient report/evidence challenge and incorrect final stage
  transition. The baseline worker's outside attempt was inconclusive because
  pytest failed before collection, but its read-only baseline was permitted to
  finish with that non-comparable evidence.
- **Severity:** Major workflow decision failure for this run: it stopped Phase 1
  before implementation even though the complete T001 gate outside the sandbox
  completes with an eligible intentional RED result. This severity describes the outcome,
  not a general reliability rating for either model.
- **Contributing extension gap:** The validation-environment policy correctly
  prefers already-authorized outside execution and requires exact outside
  reruns for plausible sandbox restrictions, but it does not explicitly say how
  to classify hangs, event-loop stalls, generic timeouts, or a pytest bootstrap
  failure that prevents an outside comparison. It also does not explicitly
  prohibit confirmed pre-existing attribution when different test identities
  merely share a similar hang signature. That ambiguity made the worker's
  ordinary-failure classification easier for the parent to accept.
- **Why the orchestrator did not keep fixing and retrying:** The baseline worker
  was read-only, the Phase 1 test worker could modify only T001/T003 test scope,
  and the parent may not replace an isolated implementation or diagnostic
  worker by fixing unrelated runtime code itself. The extension does not require
  indefinite retry. Once the test worker chose the non-environment unrelated
  failure classification, the existing test-stage rule required unchecked task
  boxes, a failed report, no test commit, and a workflow stop. The issue is the
  evidence classification and parent acceptance that selected that branch, not
  a missing instruction to retry forever.
- **Outside-attempt clarification:** The extension run did make one genuine
  outside-sandbox attempt during the baseline. That attempt was not evidence
  about the application because pytest failed during output-capture startup,
  before collection. The baseline was allowed to finish with non-comparable
  evidence. The later test worker then encountered a different sandbox hang,
  classified it as non-environmental, and therefore never entered the policy's
  outside-rerun branch for the exact later command. The problem is not that no
  outside attempt occurred at all; it is that the failed baseline attempt did
  not produce a comparable result and the later classification prevented the
  required diagnostic from being retried where it mattered.
- **Current decision:** Keep this issue open. Do not describe every hang as an
  automatic sandbox blocker. Require stronger evidence before treating
  different failing test identities as the same confirmed pre-existing
  regression, and make the non-comparable outside-bootstrap case visible in the
  parent transition decision.
- **Proposed extension improvement:** Add narrow guidance for hang and timeout
  attribution: distinguish an ordinary reproducible product/test-harness
  deadlock from a plausible environment blocker; require matching test identity
  plus comparable material signature for confirmed pre-existing deferral; and
  when an outside rerun fails before collection, preserve the result as
  non-comparable and require the parent to decide explicitly whether a fresh
  diagnostic worker should retry the exact later command outside. Do not create
  an unbounded retry loop.
- **Next validation:** Repeat the Phase 1 test stage with stronger model
  selection, exact audited prompts, and the same scope boundaries. Supply the
  now-confirmed inside/outside evidence and require the parent to challenge any
  unsupported `confirmed` attribution, select the environment-blocker/outside
  rerun path when the sandbox signature recurs, and continue from the eligible
  intentional RED result. The exact replacement parent and worker models remain
  to be selected.
- **Closure criteria:** Close only after both (a) a production-style rerun shows
  that the parent handles different test identities and a failed outside pytest
  bootstrap without overstating attribution, and (b) any agreed narrow extension
  wording and regression guards are implemented and reviewed.

### PO-006 — Parent-owned classification by primary deliverable

- **Status:** Closed for implementation and automated regression coverage;
  production-style orchestration validation remains an open follow-up.
- **Source session:** [Reported T010 misclassification](codex://threads/01a072f2-9cd1-7622-8bfb-1a6a2eb03232).
  The session behavior below comes from the user's supplied engineering
  analysis, accepted for this change on 2026-09-07; the source session was not
  independently reread during implementation.
- **Observed behavior:** T010 requested a production invariant SQL migration,
  followed by a pytest verification command. The Sol parent recognized the
  migration as implementation work but followed the extension's test-task
  classification and delegated it through the Phase 2 test prompt.
- **Root cause:** The previous `is_test_task` function treated a test filename
  anywhere in task text as sufficient to classify the task as test work.
  The workflow made those parser groups authoritative while restricting the
  test worker from implementing production behavior. It confused how to verify
  the deliverable with what to deliver, then prevented the parent's correct
  interpretation from controlling dispatch.
- **Decision:** Retain a small structural parser for IDs, phase membership,
  complete task text, sections, and checkbox state. Give the parent full
  authority to classify tasks by primary deliverable and record a short
  rationale. Freeze validated assignments for dispatch and reuse them on resume,
  with an explicit correction path rather than an unchangeable freeze.
- **Reason for this direction:** Interpretation requires model judgment; exact
  inventory and coverage checks do not. An independently extracted inventory
  lets code detect omitted, duplicated, or unknown assignments even when the
  model's classification output looks plausible. Removing the entire parser
  would discard useful accounting together with the faulty classifier.
  Mechanical validation cannot establish semantic correctness.
- **Implemented changes:** Removed all semantic classification heuristics from
  `scripts/phase_tasks.py`. It now returns structural `tasks`, a source digest,
  and `next_stage: classification` for pending work. Added
  `scripts/validate_assignments.py` to validate phase identity, source freshness,
  exact ID coverage, duplicate IDs, role values, and nonempty rationales.
  The validator produces role groups only from parent-authored assignments.
  Updated the parent command, worker prompt, usage guide, examples, and changelog.
- **Assignment and resume contract:** Save all selected-phase IDs, including
  checked IDs for stable accounting, in the parent-owned
  `.phase-orchestrator/phase-<N>-assignments.json` beside `tasks.md`. Dispatch
  only unchecked tasks. The digest ignores checkbox progress but detects other
  source changes, including surrounding dependency notes. Before dispatch and
  on resume, validate the saved manifest; do not silently reclassify.
- **Correction and completion contract:** A role mismatch pauses dispatch.
  Archive the previous manifest, increment its revision, record the reason,
  reconcile actual deliverables and incorrectly checked tasks, and validate
  before launching a fresh worker. Preserve reviewed scope-clean work and
  existing commits. Reopening work invalidates a stale completion marker and
  requires fresh verification and documentation. Corrections do not consume
  remediation attempts or bypass normal stage gates. Authoring tests must never
  count as completing T010's migration deliverable.
- **Compatibility:** Parser role groups, their counts, and the
  `tests_first_tasks` alias are removed. Pending dispatch comes from the
  assignment validator. Report and handoff wire schemas remain `2.0.0`;
  assignment manifests use their separate `1.0.0` format.
- **Validation evidence:** `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover
  -s tests -q` passed all 89 tests after implementation; `git diff --check`
  passed. New regression coverage includes a migration under a Tests First
  heading with a pytest continuation, invalid/duplicate/missing assignments,
  source drift, checkbox-aware resume, reassignment and reopening, empty and
  documented phases, CLI validation, and parent correction contract checks.
- **Evidence limits:** Automated tests demonstrate accounting and contract
  behavior. They do not prove a live parent model will classify every task
  correctly or follow the correction procedure. No live orchestration trial
  has been run for this change.
- **Regression guard:** `tests/test_assignments.py` and
  `tests/test_phase_tasks.py`; inspect actual parent assignments, worker prompts,
  delivered production changes, and completion evidence in the follow-up run.

- **Follow-up decision — assignment clarification:** Simplified worker mismatch
  handling to an intermediate message with the task and reason. The parent
  reviews it, explains a correct assignment so the same worker can continue,
  or corrects a mistaken assignment and dispatches to the appropriate role.
  This supersedes the special mismatch-report status handling introduced during
  PO-006 implementation. Confirmed corrections still use the recorded manifest
  revision procedure; final stage reports retain their normal purpose.
- **Follow-up correction — tested communication limits:** The Luna/xhigh probe
  received parent input while running and a follow-up on the same worker, but
  reported that its agent messaging tool was unavailable. No intermediate
  worker-to-parent message was observed. This supersedes the intermediate-message
  assumption above: the worker ends its turn with a clarification question;
  the parent answers by continuing that same worker. A clarification response
  is separate from the final stage report and does not complete the stage.

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
- **2026-09-02 — Explicit instruction ownership and ordering.** Parent policy is
  not worker prompt text; direct worker wording is appended from the worker
  template, and parent authorization precedes any environment-blocker stop.
- **2026-09-02 — Runtime paths are installation-rooted.** Agent-facing commands
  and templates resolve extension-internal files through
  `.specify/extensions/phase-orchestrator/`; source-relative paths remain for
  repository-oriented material only.

- **2026-09-07 — Structural inventory, semantic parent authority.** Adopted
  parser inventory → parent interpretation and deliverable-based classification
  → recorded rationale → validated, durable dispatch assignments. This
  supersedes keyword/filename classification as workflow authority. Freeze
  assignments for consistent execution, but permit recorded corrections with
  checkbox and completion-evidence reconciliation. See PO-006.

## Optional Future Directions

### Separate semantic-classification worker (proposed 2026-09-07)

- **Status:** Optional proposal only; not adopted or implemented. Related to
  PO-006, whose current parent-owned classification design remains in effect.
- **User proposal:** Delegate semantic task classification to a dedicated
  worker to reduce the parent orchestrator's workload.
- **Possible responsibility split:** The parser extracts structural inventory;
  a classification worker interprets primary deliverables and proposes roles
  with brief rationales; the validator checks exact coverage and source
  freshness; the parent accepts assignments, resolves contradictions, and owns
  dispatch and corrections. Persist accepted assignments for reuse on resume.
- **Potential benefit:** Move detailed classification and repository
  investigation into a focused worker context, especially for large phases.
- **Tradeoff and rationale:** The parent already reads the complete task file
  for scope and dependencies. A separate worker repeats some of that context
  gathering and adds handoff and review overhead. It may reduce parent workload
  without reducing total work. T010 demonstrated an authority problem rather
  than an inability of the parent to understand the deliverable; delegation is
  therefore an optional scaling choice, not a required fix for that incident.
  Parent review should focus on compact assignments and contradictions rather
  than repeat every classification, while preserving correction authority.
- **Current decision:** Make no runtime changes for this proposal. Stage and
  commit the current extension changes before testing the existing design.
  Evaluate actual classification effort, errors, and correction behavior before
  deciding whether a separate worker is warranted. This records the intended
  sequence; it does not claim staging, committing, or live testing has occurred.

## Open Follow-ups

- After testing the current design, revisit the optional classification-worker
  proposal only if observed parent workload or classification behavior supports
  it; keep it separate from the adopted PO-006 implementation direction.
- Validate the closed `PO-001` behavior after a real orchestrator run proves the
  initial verifier discovers the complete affected surface and a proven
  in-phase issue proceeds to remediation despite missing baseline evidence.
- Validate the closed `PO-002` behavior after production-style runs prove both
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
- Inspect a generated validation-worker prompt in a production-style run to
  confirm it contains the direct environment block and no numbered parent
  orchestration policy.
- During the release-archive installation test, resolve every internal path
  named by the installed command and reference templates from a target project.
- Rerun the PO-005 Phase 1 test stage with stronger model selection and keep
  PO-005 open until its evidence-handling and extension-clarification closure
  criteria are satisfied.
- Validate PO-006 in a production-style run containing a migration task with
  a test verification command. Confirm implementation dispatch, an actual
  migration deliverable, reuse of assignments on resume, and correction of a
  deliberately mistaken assignment without false checkbox completion. Record
  the live evidence separately from the passing automated tests.
