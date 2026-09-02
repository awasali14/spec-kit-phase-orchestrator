---
description: "Use /speckit.phase-orchestrator.phase or $speckit-phase-orchestrator-phase to run Spec Kit tasks.md through isolated regression-baseline, test, implementation, verification, remediation, and documentation agents with parent-owned gated commits."
---

# Spec Kit Phase Orchestrator 2.1

Run an existing Spec Kit `tasks.md` through context-isolated stage agents. This
companion workflow must not replace, bypass, or modify official
`/speckit.implement` or `$speckit-implement`.

## Arguments

Accept these forms:

```text
next <tasks.md path> [--docs-dir <directory>] [--no-commit]
phase <number> <tasks.md path> [--docs-dir <directory>] [--no-commit]
phase <start> to <end> <tasks.md path> [--docs-dir <directory>] [--no-commit]
all <tasks.md path> [--docs-dir <directory>] [--no-commit]
```

Also accept an explicit Markdown execution-document path in natural language.
It overrides the generated path and `--docs-dir`. Preserve `next`, explicit
`phase`, `all`, `--docs-dir`, explicit documentation paths, and `--no-commit`.

## Parent-Only Invariants

The current agent is the parent orchestrator and owns every Git operation,
stage transition, remediation count, and `all` queue decision.

1. Launch each stage in a fresh isolated context, sequentially. Never reuse a
   stage agent and never run two phase stages concurrently.
2. Workers must not stage, commit, push, spawn workers, run this orchestrator,
   or cross phase boundaries.
3. Give later agents only compact structured handoffs: phase/task IDs,
   relevant paths, prior SHA, reviewed manifest, validation summaries,
   regression-baseline evidence, deferred findings, and expected failures.
   Never pass full traces, transcripts, parent plans, remediation-cycle state,
   or another role's instructions.
4. The parent may commit but must never push.
5. Stop when isolated agents are unavailable. Do not collapse the stages into
   the parent context.

### Complete Task-File Analysis

Before building its plan or launching the first worker, the parent must read
and analyze the complete original `tasks.md` directly, not only parser
summaries for the selected phase. This gate applies equally to `next`, a single
`phase`, an inclusive phase range, and `all`.

The parent must understand every phase, task boundary, dependency,
execution-order note, and completion state; identify earlier prerequisites and
later work that must remain out of scope; and inspect selected work in detail
for relevant paths, validation expectations, skills, and MCP routing. Keep
this complete-file analysis parent-only. Worker handoffs remain compact and
phase-specific and must not contain future-phase tasks, the full parent plan,
or frozen queue state.

## Resolve And Select

1. Parse the prompt and locate the repository root and `tasks.md`, then satisfy
   the complete task-file analysis gate before planning any worker.
2. Validate the selector and run the installed parser with `--json` and the
   matching selector:

   ```text
   python3 .specify/extensions/phase-orchestrator/scripts/phase_tasks.py <tasks.md> --mode next --json
   python3 .specify/extensions/phase-orchestrator/scripts/phase_tasks.py <tasks.md> --phase <number> --json
   python3 .specify/extensions/phase-orchestrator/scripts/phase_tasks.py <tasks.md> --phase <start> --through-phase <end> --json
   python3 .specify/extensions/phase-orchestrator/scripts/phase_tasks.py <tasks.md> --mode all --json
   ```

3. For a range, require positive integers with `start <= end` and require every
   phase number in the inclusive range to exist. Phase 1 has no predecessor.
   When `start > 1`, require only that every task checkbox in Phase `start - 1`
   is checked; do not require predecessor orchestration documentation or a
   workflow-complete marker, and do not require documentation for any still
   earlier phase outside the range. Freeze the exact inclusive phase-number
   queue before launching the first worker and never add a phase or continue
   beyond `end`.
4. Pass `--docs-dir` through. For an explicit Markdown path with `next`, first
   resolve the candidate, then rerun that number with `--phase <number>
   --docs-path <path>`. With `all`, require one unambiguous explicit path per
   phase; otherwise stop for clarification rather than reusing a file. Reject
   one explicit documentation path for a multi-phase range. Pass an explicit
   single-phase path directly with `--docs-path <path>`.
5. Select `next`, ranges, and `all` by `workflow_complete`, not checkbox completion.
   A phase with `task_complete: true` but `documentation_complete: false`
   resumes at `next_stage: verification`.
6. In a range or `all`, execute one phase through every gate and its
   workflow-complete documentation marker before reparsing and selecting the
   next phase. For a range, reparse the current phase state, resume at its
   reported `next_stage`, and advance only to the next number in the frozen
   queue. Do not advance merely because task checkboxes are checked.
7. If an explicitly selected phase or a phase inside a range is already
   workflow complete, report or skip that phase and do not rerun it unless the
   user explicitly asks. Stop successfully when the frozen range reaches its
   ending phase.

## Baseline And Manifest Gate

Before the first phase and again before every stage:

1. Record `HEAD`, `git status --porcelain=v1 -z`, staged and unstaged diffs,
   untracked paths, and a compact content fingerprint for every dirty path.
2. Treat all pre-existing dirty paths as protected. Stop before a stage when
   its required path overlaps a protected path; do not overwrite, stage, or
   restore the user's work.
3. Record the stage's allowed phase paths and expected task-file checkbox
   edits. After the agent returns, derive an exact changed-path manifest from
   the new baseline delta.
4. Reject unrelated paths, unexpected generated artifacts, changes outside the
   phase, and any change to a protected path. Leave unrelated pre-existing
   files untouched.
   Prefer project-supported non-writing validation flags or environment
   settings so caches, coverage, snapshots, and reports are not created.
5. Confirm the index matches its pre-stage baseline until the parent
   intentionally stages exact eligible paths. Never use broad staging such as
   `git add .`, `git add -A`, a directory, or a wildcard.
6. A successful stage with no intentional changes records `no_changes` and
   proceeds without a commit.

Under `--no-commit`, run the same baselines, agents, validation, review, and
eligibility gates, but never stage or commit. Track a reviewed manifest for
each stage, treat earlier reviewed stage changes as the next stage's known
baseline, keep the original index unchanged, and leave all accumulated changes
unstaged at the end.

## Capability And MCP Routing

Before using tools or building any stage handoff, inspect the skills and MCP
servers exposed by the current agent integration. Parse the user's MCP opt-outs
first. A global instruction such as `do not use MCP` disables every MCP, while
a provider-specific instruction such as `do not use Supabase MCP` or `do not
use Exa` excludes only that provider. Explicit user exclusions take precedence
over every default below and must be propagated to every affected worker.

1. When the parent needs web search, use Exa first when it is available and not
   excluded. If Exa is unavailable or fails, use another available web-search
   tool and record the fallback.
2. When selected work concerns a database, identify the project's database
   from the task scope and repository context, look for a related available MCP,
   and use it when present and not excluded. Do not hardcode a database
   provider. If no related database MCP is available, continue with suitable
   project tools.
3. Infer frontend and backend scope from the assigned tasks, relevant paths,
   and project stack. Automatically select relevant available frontend or
   backend skills and MCPs instead of limiting routing to capabilities named by
   the invoker.
4. Route only capabilities relevant to the current stage. Confirm that a
   selected capability is actually exposed before use; report an unavailable
   capability or web-search fallback rather than claiming it was used.

## Build Stage Handoffs

Use `.specify/extensions/phase-orchestrator/references/worker-prompt-template.md`,
`schemas/phase-handoff.schema.json`, and `schemas/phase-report.schema.json` as
the v2 contracts. Every handoff must include `report_contract` with the report
schema ID, schema version `2.0.0`, and the same fixed stage as the assignment.
Send the matching stage-specific report form from the worker prompt with every
handoff and require every array field, using `[]` when empty.

After the worker returns, validate the completed report against
`phase-report.schema.json` before trusting its status, validation, evidence, or
findings. Then cross-check its stage, phase number, assigned task IDs, and exact
changed paths against the assignment and the parent-observed Git manifest.
Cross-check regression comparability, downstream safety, supplied remediation
finding IDs, and protected paths because those relationships span documents or
repository state and cannot be proven by the standalone report schema. Reject
the report before any transition or commit when either validation layer fails.

Only verification-stage findings may carry a non-null `disposition`; findings
from every other stage remain provisional with `disposition: null`. Preserve
that null disposition when routing a non-verifier finding into verification. A
remediation handoff receives only verifier-classified findings. Populate only
the selected stage, assigned IDs, phase identity and requirements, scope,
relevant paths, prior SHA, prior manifest and validation, regression-baseline
evidence, deferred findings, expected failures, validation expectations, and
report contract. Never put current-stage results or a verdict in the handoff.
Sanitize the prompt and append only the chosen role and report form. Keep
selector, lifecycle, queue, commit-control, and remediation-cycle state parent-only.

Route and require official `/speckit.implement` or `$speckit-implement`
discipline for both test and implementation stages. Route it to remediation
only when useful. Route other relevant skills and automatically selected
frontend/backend skills and MCPs only to the phase stages that need them.
Include the selected MCPs, applicable MCP opt-outs, and Exa-first web-search
policy in each handoff. Keep operational notes similarly scoped.
Append the complete Validation Execution Environment policy to every
baseline-verification, test, implementation, verification, and remediation
handoff. Documentation workers do not receive it because they do not run
project validation.
Do not leak parent orchestration context. Only the documentation stage receives
the phase document path/template or Mermaid instructions.

## Validation Execution Environment

Apply this policy whenever the parent or a baseline-verification, test,
implementation, verification, or remediation worker runs project validation:

1. Prefer execution outside the Codex sandbox when an already-authorized
   outside route is available.
2. If outside execution is not currently permitted, run the exact command
   inside the sandbox instead of stopping immediately.
3. Use a sandbox pass or ordinary assertion/product failure normally.
4. When the sandbox failure is plausibly caused by filesystem or socket
   permission, blocked network/service/database/container access, restricted
   subprocess execution, or sandbox termination, do not classify it as a code
   regression or in-phase defect.
5. The worker running the validation requests user permission to rerun the
   exact command outside the sandbox. When permission is granted, that worker
   runs the command before returning, treats the outside result as
   authoritative, and records both the exact command and environment used.
6. If the worker cannot request permission, permission is denied, or outside
   execution remains unavailable, it returns an environment blocker with the
   command, sandbox evidence, and a caveat that the exact outside rerun was
   unavailable. A verifier uses an `inconclusive` finding with disposition
   `block`. Baseline-verification, test, implementation, and remediation
   workers use disposition `null`, preserving the original rule that only a
   verifier owns a blocking disposition. Do not consume a remediation attempt
   or attribute a product defect from that result; do not add report fields.
7. After validating a worker's environment-blocker report and observed
   manifest, the parent must not stop immediately. The parent asks the user to
   authorize the exact outside command. When permission is granted, relaunch a
   fresh isolated worker for that same stage and assignment, require the exact
   outside rerun, and continue the normal stage gate from its new report. Keep
   any scope-clean reviewed changes from the blocked stage as known same-stage
   state, never as protected unrelated work, and do not commit them before the
   relaunched worker completes. Neither the blocker nor this relaunch consumes
   a remediation attempt. Stop and report the environment blocker only when
   the parent-level permission request is denied or outside execution remains
   unavailable.

## Stage Sequence

Run this state machine for one selected phase:

```text
baseline_verification before mutation, or durable baseline reuse on resume
  -> test when non-empty
  -> implementation when non-empty
  -> implementation progress commit when eligible
  -> verification (always, fresh, read-only)
  -> remediation on failure
  -> remediation progress commit when eligible
  -> verification after every remediation result (fresh, read-only)
  -> documentation after a phase-safe pass (always)
```

Skip an empty test or implementation stage. Establish the regression baseline
before the first mutating stage of each phase, then always verify and document.
Starting from parser `next_stage` may skip already completed task stages, but
must still run a fresh verification before documentation. On a resumed phase,
reuse durable pre-change evidence when available. Otherwise record the
baseline as unavailable; do not run current-state validation and mislabel it
as a pre-phase baseline. Later regression failures then have uncertain
attribution and cannot be deferred.

When a phase contains test-authoring tasks but no implementation tasks, do not
broaden the phase to make intentional RED tests green. A correctly executing
RED result attributable only to implementation outside the phase satisfies the
test-authoring-only phase contract. The final verifier records the affected
validation as `expected_red`, returns an overall passing phase verdict, skips
remediation, and permits documentation.

### Regression Baseline Stage

Launch a fresh `baseline_verification` agent before phase mutations.

1. Make it strictly read-only and never commit eligible. Assign no task IDs.
2. Treat commands in `tasks.md` as minimum coverage. Identify changed or
   removed behavior, search its callers, references, fixtures,
   parameterizations, and tests, and map every affected subsystem. Identify
   suitable regression commands from the phase scope, repository configuration,
   and existing validation, then run the complete bounded suite for every
   affected subsystem with non-writing settings. Record the exact command, a
   compact non-secret environment fingerprint, status, failing test identities,
   and normalized material failure signatures.
3. A pre-existing regression does not stop this stage. Record unavailable or
   non-comparable baseline evidence explicitly and continue; it makes any later
   failure of that command ineligible for deferral.
4. Report every excluded or untested affected surface as a caveat. Preserve the
   affected-subsystem map, complete command surface, and evidence through every
   later handoff in the phase. The final
   verifier must rerun the exact baseline commands; it may add other suitable
   regression commands, but a newly failing command without comparable baseline
   evidence has uncertain attribution.
5. Stop only for the normal safety and contract violations, including mutation,
   an invalid report, or unavailable isolation. A baseline result is evidence,
   not a passing gate.

### Test Stage

Assign only incomplete `test_tasks`.

1. The test agent may change assigned tests, explicitly assigned test-only
   support, and its task checkboxes. It must not implement production behavior.
   It must use the supplied official `/speckit.implement` or
   `$speckit-implement` discipline for the assigned test work.
2. Require the complete focused gate before checkboxes are marked. Do not run
   independent-phase or regression validation in this stage; reserve those for
   the verifier.
3. Accept either green or intentional RED. RED is eligible only when tests
   collect and execute correctly and every failure is attributable to missing
   assigned implementation.
4. Require the worker to correct failures within the assigned test scope and
   rerun the focused gate as needed. Plausibly sandbox-related environment
   failures follow the Validation Execution Environment policy and return
   `blocked`, not `failed`. If another syntax, collection, fixture,
   infrastructure, environment, flaky, or unrelated failure remains after
   available in-scope correction, require the worker to restore assigned
   checkboxes to their baseline unchecked state and report the gate as failed.
   After reviewing that final non-environment report, the parent stops the
   workflow without committing the test-stage changes.
5. Review the exact manifest. With commits enabled, stage only those paths and
   commit an eligible intentional change as:

   ```text
   test(<scope>): add phase <N> coverage
   ```

   The body must record stage, assigned task IDs, exact files, validation,
   expected RED failures and attribution when applicable, and prior SHA.

### Implementation Stage

Assign only incomplete `implementation_tasks`.

1. The implementation agent uses the supplied official `/speckit.implement` or
   `$speckit-implement` discipline and inspects the reviewed tests directly:
   when a test stage ran, from its commit in commit mode or its reviewed manifest
   under `--no-commit`. When the test stage was empty, it identifies existing
   phase-scoped tests from the assigned tasks and repository context.
2. It implements only assigned implementation/setup tasks and marks only those
   checkboxes after the complete focused phase-test gate passes.
3. The complete focused gate must include tests authored by the preceding test
   stage, when present, and any other relevant phase-scoped tests. Require green
   results when it can. If it cannot reach green or suspects a defective test,
   cross-phase requirement, or other unresolved cause, return `unresolved` with
   typed findings instead of changing completed test work or crossing scope.
   The worker's classification is provisional and uses `disposition: null`; it
   is not a final blocker decision.
4. Validate the completed report against the report schema and assignment, then
   review the exact manifest. A schema-valid, internally consistent,
   scope-clean `passed` or `unresolved` result with intentional changes is an
   eligible reversible progress checkpoint. Do not mark unchecked
   implementation tasks when the focused gate did not pass.
5. With commits enabled, immediately stage only the implementation stage's
   exact changed paths and commit before launching the verifier. Select
   `feat(<scope>):`, `fix(<scope>):`, or `chore(<scope>):` from the assigned
   implementation-task intent. Record stage/status, task IDs, exact files,
   focused validation, unresolved findings when present, and prior SHA in the
   body. A later blocking verification leaves this progress commit in history.
   Under `--no-commit`, keep the reviewed manifest unstaged as known phase
   state for the verifier.

### Verification Stage

Launch a fresh verification agent after task stages and after every remediation
result, including `unresolved` or failed focused validation.

1. Make it strictly read-only. It must not modify checkboxes, source, tests,
   snapshots, caches, coverage, reports, or documentation.
2. On the first verification, independently inspect the actual phase diff and
   discover affected subsystems by following changed or removed behavior to its
   callers, references, fixtures, parameterizations, and tests. Treat commands
   in `tasks.md` as minimum coverage. Require a structured report with separate
   focused, independent-phase, exact-baseline, and complete bounded
   affected-subsystem results, plus scope/artifact findings, caveats for every
   excluded or untested affected surface, and one verdict. Continue all planned
   commands after failures unless execution becomes unsafe, and aggregate all
   related in-phase failures into one report before remediation. On every later
   verification, require the verifier to preserve and rerun this expanded
   verification surface; it may expand but never narrow it.
   The verifier, not an implementation or remediation worker, owns technical
   attribution and proposes `remediate`, `defer`, or `block`; the parent applies
   downstream-safety and attempt-cap policy to the final transition.
3. Confirm the working tree and index exactly match the pre-verification
   baseline. Reject any verifier-created path. A verifier never commits.
4. Apply scope-first decision precedence. First decide whether the requirement
   and repair belong to the current phase. A proven, repairable in-phase issue
   is `phase_scoped_failure` or `defective_test` with disposition `remediate`,
   even with `baseline_evidence: null` and uncertain or not-applicable origin
   attribution. Never block in-phase remediation solely because baseline
   coverage was incomplete. Then compare every baseline regression command
   using the same command and a comparable environment to determine origin. A
   regression is phase introduced or worsened when
   the baseline passed but the current command fails, or when the current result
   adds failing test identities or materially changes a baseline failure
   signature. `phase_introduced_regression` requires comparable non-null
   baseline evidence. Send it to remediation when an in-scope repair is possible.
5. Classify a regression as `preexisting_unrelated_regression` with proposed
   disposition `defer` only when its failing test identities and material
   signatures are unchanged, no failures were added, focused and
   independent-phase validation pass, and attribution evidence is confirmed.
   Return `downstream_safe: null` until the parent checks the remaining queue.
   Missing, non-comparable, or contradictory evidence prevents confirmed
   origin attribution and deferral. It does not override a separately proven
   in-phase issue. Use `inconclusive` with disposition `block` for uncertain
   scope, a required cross-phase repair, or an unproven out-of-phase failure.
6. Before accepting `defer`, the parent reruns the parser in `all` mode for
   metadata and compares the finding's affected paths and components with every
   later queued workflow-incomplete phase's task text and paths, purpose,
   checkpoint, and independent test; exclude the current selected phase, which
   remains parser-incomplete until documentation. When no later queued phase
   exists, downstream safety is satisfied. Any dependency, overlap, missing
   metadata, or ambiguity sets `downstream_safe` to false, changes the
   disposition to `block`, and stops. When the check passes, set
   `downstream_safe` to true, accept the deferral, and record it immediately for
   documentation and the final aggregate report.
7. On `passed`, `passed_with_deferred_findings`, or an accepted
   test-authoring-only `expected_red`, continue to documentation. On
   `remediate`, launch remediation when fewer than two attempts have run. On
   an environment `block`, first complete the parent permission and fresh
   same-stage relaunch policy above. On any other `block`, or when no attempt
   remains, stop without broadening the phase; retain any earlier eligible
   progress commits.

### Remediation And Fresh Re-verification

1. Launch a fresh remediation agent with only the verifier's compact findings,
   phase scope, relevant paths, baseline comparison, validation summary, prior
   SHA/manifest, and deferred findings. Keep the remediation-cycle count in the
   parent context.
2. It may change phase-scoped code, tests, fixtures, and necessary phase task
   checkboxes. It may correct a completed phase-scoped test only when the
   verifier classified that test as defective. It must not broaden scope or
   weaken the requirement merely to obtain green.
3. Iterate on the assigned findings and run focused validation as needed.
   Report each supplied finding as resolved or unresolved. Reserve
   independent-phase and regression gates for the fresh verifier. Return
   `unresolved` only when a finding or red result remains after available
   in-scope remediation, or when resolving it would require crossing scope; the
   worker does not itself make the final stop decision. It also reports any
   newly discovered relevant issue rather than fixing it outside the supplied
   scope, using a provisional classification and `disposition: null` until the
   fresh verifier independently classifies it.
4. Validate the completed report against the report schema and assignment, and
   require one `remediation_results` entry for every supplied finding ID.
   Review the exact manifest. A schema-valid, internally consistent,
   scope-clean `passed` or `unresolved` result with intentional changes is an
   eligible reversible progress checkpoint. With commits enabled, immediately
   stage only that remediation stage's exact changed paths and commit:

   ```text
   fix(<scope>): remediate phase <N> findings
   ```

   Record stage/status, finding IDs, exact files, focused validation, and prior
   SHA in the body. Under `--no-commit`, keep the reviewed manifest unstaged.
   In both modes, launch a fresh read-only verifier regardless of the
   remediation validation result and treat the reviewed changes as known phase
   state, not protected unrelated work.
5. Each remediation plus its fresh verification consumes one attempt. An
   environment blocker does not consume an attempt. Permit at
   most two complete cycles. After attempt one, repeat only for a verifier
   disposition of `remediate`; after attempt two, any non-phase-safe verdict
   stops the workflow.

### Mutating Stage Commit Gates

The parent evaluates each mutating stage independently after report-schema,
assignment, manifest, protection, and scope checks:

1. Test commits only after focused green or attributable expected RED.
2. Implementation and each remediation attempt commit their own exact paths
   immediately after a schema-valid, scope-clean `passed` or `unresolved`
   result. Never combine their manifests into a later certificate commit.
3. Documentation commits only after final phase-safe verification and parser
   completion checks.
4. Baseline and verification never commit. `no_changes`, `--no-commit`, a dirty
   overlap, unrelated/generated artifacts, `blocked`, `failed`, schema-invalid,
   internally inconsistent, or manifest-mismatched results never commit.
5. Every commit uses exact-path staging and records its own prior SHA. A phase
   with test, implementation, and documentation changes normally has three
   commits and may have up to five when both remediation cycles change files.

### Documentation Stage

Launch only after a final phase-safe verdict: `passed`,
`passed_with_deferred_findings`, or an accepted test-authoring-only
`expected_red`.

1. Give the documentation agent aggregate compact stage reports, commit SHAs,
   reviewed manifests, regression-baseline comparisons, validation summaries,
   expected RED failures, deferred findings, and remediation history.
2. It may modify only the resolved phase execution document. It must use
   `.specify/extensions/phase-orchestrator/references/phase-doc-template.md`.
   It must not rerun source, test, independent-phase, or regression commands;
   it records the supplied final-verifier evidence and validates only the
   document structure, marker, Mermaid contract, and exact-path diff.
3. Route
   `.specify/extensions/phase-orchestrator/references/mermaid-style.md` only to
   this agent. Honor an explicit user opt-out of Mermaid.
4. Require the exact durable marker
   `<!-- phase-orchestrator:workflow-complete v2 -->`, which may be written only
   when the document records a phase-safe final verification.
5. Validate the completed documentation report against the report schema and
   assignment, then re-run the parser for the same phase and require `task_complete`,
   `documentation_complete`, and `workflow_complete` all true with
   `next_stage: null`.
6. Confirm only the document changed. With commits enabled, stage that exact
   path and commit:

   ```text
   docs(<scope>): document phase <N> execution
   ```

   Record stage, completed task IDs, document path, aggregate validation,
   final verification, and prior SHA in the body.

## Stop And Report

Stop immediately for a dirty-path overlap, unrelated/generated change, invalid
RED, worker or verifier mutation outside its authority, missing isolation,
documentation mutation outside its file, or an exhausted remediation cap. Stop
when a stage report is schema-invalid, mismatches the assignment or observed
manifest, contradicts the stage contract, or lacks enough evidence for the
parent gate. Stop after the
verifier confirms a required failure cannot be resolved without crossing phase
scope, otherwise confirms uncertain scope, a required cross-phase repair, or an
unproven out-of-phase failure; cannot prove downstream safety for a proposed
deferral; returns an unresolved environment blocker after the outside-rerun
policy; or returns a non-phase-safe verdict after attempt two. Do not stop or
withhold in-phase remediation solely because baseline evidence is incomplete,
and do not merely stop because a verifier attributes a regression as uncertain
when the issue is separately proven to be repairable and in phase.

Report selected phase, stage outcomes, task IDs, per-stage manifests, commits
or `--no-commit`, regression-baseline and attribution evidence, validation
summaries, expected failures, deferred findings, remediation count,
documentation path, workflow-completion state, protected unrelated files left
untouched, and blockers. Never claim a push.
