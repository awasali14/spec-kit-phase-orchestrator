---
description: "Use /speckit.phase-orchestrator.phase or $speckit-phase-orchestrator-phase to run Spec Kit tasks.md through isolated regression-baseline, test, implementation, verification, remediation, and documentation agents with parent-owned gated commits."
---

# Spec Kit Phase Orchestrator 2.0

Run an existing Spec Kit `tasks.md` through context-isolated stage agents. This
companion workflow must not replace, bypass, or modify official
`/speckit.implement` or `$speckit-implement`.

## Arguments

Accept these forms:

```text
next <tasks.md path> [--docs-dir <directory>] [--no-commit]
phase <number> <tasks.md path> [--docs-dir <directory>] [--no-commit]
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

## Resolve And Select

1. Parse the prompt and locate the repository root and `tasks.md`.
2. Run the installed parser with `--json` and the matching selector:

   ```text
   python3 .specify/extensions/phase-orchestrator/scripts/phase_tasks.py <tasks.md> --mode next --json
   python3 .specify/extensions/phase-orchestrator/scripts/phase_tasks.py <tasks.md> --phase <number> --json
   python3 .specify/extensions/phase-orchestrator/scripts/phase_tasks.py <tasks.md> --mode all --json
   ```

3. Pass `--docs-dir` through. For an explicit Markdown path with `next`, first
   resolve the candidate, then rerun that number with `--phase <number>
   --docs-path <path>`. With `all`, require one unambiguous explicit path per
   phase; otherwise stop for clarification rather than reusing a file. Pass an
   explicit phase path directly with `--docs-path <path>`.
4. Select `next` and `all` by `workflow_complete`, not checkbox completion.
   A phase with `task_complete: true` but `documentation_complete: false`
   resumes at `next_stage: verification`.
5. In `all`, execute one phase through every gate and its workflow-complete
   documentation marker before reparsing and selecting the next phase.
6. If the explicit phase is already workflow complete, report that state and
   do not rerun it unless the user explicitly asks.

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

Use
`.specify/extensions/phase-orchestrator/references/worker-prompt-template.md`
and `schemas/phase-handoff.schema.json` contract v2 as the source of truth for
the parent-to-worker handoff. The schema does not govern the worker's stage
report. Every report must include `stage`, `phase_number`, `status`,
`changed_paths`, `validation`, and `commit_eligible`; `expected_failures`,
`findings`, and `caveats` may be empty or omitted. Every non-empty finding must
use the typed finding contract in the worker prompt. Populate `stage`, assigned
IDs, phase scope, relevant paths, prior SHA, prior manifest and validation,
regression-baseline evidence, deferred findings, expected failures,
and conditional commit eligibility. Sanitize the prompt and append only the
chosen role section. Keep remediation-cycle state in the parent context; never
include it in a worker handoff.

Route and require official `/speckit.implement` or `$speckit-implement`
discipline for both test and implementation stages. Route it to remediation
only when useful. Route other relevant skills and automatically selected
frontend/backend skills and MCPs only to the phase stages that need them.
Include the selected MCPs, applicable MCP opt-outs, and Exa-first web-search
policy in each handoff. Keep operational notes similarly scoped.
Do not leak parent orchestration context. Only the documentation stage receives
the phase document path/template or Mermaid instructions.

## Stage Sequence

Run this state machine for one selected phase:

```text
baseline_verification before mutation, or durable baseline reuse on resume
  -> test when non-empty
  -> implementation when non-empty
  -> verification (always, fresh, read-only)
  -> remediation on failure
  -> verification after every remediation result (fresh, read-only)
  -> verified implementation/remediation commit when eligible
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
2. Identify suitable regression commands from the phase scope, repository
   configuration, and existing validation. Run them with non-writing settings
   and record the exact command, a compact non-secret environment fingerprint,
   status, failing test identities, and normalized material failure signatures.
3. A pre-existing regression does not stop this stage. Record unavailable or
   non-comparable baseline evidence explicitly and continue; it makes any later
   failure of that command ineligible for deferral.
4. Preserve this evidence through every later handoff in the phase. The final
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
   rerun the focused gate as needed. If a syntax, collection, fixture,
   infrastructure, environment, flaky, or unrelated failure remains after
   available in-scope correction, require the worker to restore assigned
   checkboxes to their baseline unchecked state and report the gate as failed.
   After reviewing that final report, the parent stops the workflow without
   committing the test-stage changes.
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
   The worker's suspicion is not a final blocker decision.
4. Review the exact manifest and keep all implementation changes unstaged and
   uncommitted, whether the focused gate is green or unresolved. Treat that
   reviewed manifest as known phase state for the read-only verifier. Do not
   mark unchecked implementation tasks when the focused gate did not pass.
5. Implementation becomes commit eligible only after a phase-safe final
   verification. The parent later stages the exact accumulated implementation
   and remediation path union and selects `feat(<scope>):`, `fix(<scope>):`, or
   `chore(<scope>):` from the assigned task intent.

### Verification Stage

Launch a fresh verification agent after task stages and after every remediation
result, including `unresolved` or failed focused validation.

1. Make it strictly read-only. It must not modify checkboxes, source, tests,
   snapshots, caches, coverage, reports, or documentation.
2. Require a structured report with separate focused, independent-phase, and
   suitable regression results, plus scope/artifact findings and one verdict.
   The verifier, not an implementation or remediation worker, owns technical
   attribution and proposes `remediate`, `defer`, or `block`; the parent applies
   downstream-safety and attempt-cap policy to the final transition.
3. Confirm the working tree and index exactly match the pre-verification
   baseline. Reject any verifier-created path. A verifier never commits.
4. Compare every baseline regression command using the same command and a
   comparable environment. A regression is phase introduced or worsened when
   the baseline passed but the current command fails, or when the current result
   adds failing test identities or materially changes a baseline failure
   signature. Send it to remediation when an in-scope repair is possible.
5. Classify a regression as `preexisting_unrelated_regression` with proposed
   disposition `defer` only when its failing test identities and material
   signatures are unchanged, no failures were added, focused and
   independent-phase validation pass, and attribution evidence is confirmed.
   Return `downstream_safe: null` until the parent checks the remaining queue.
   Missing, non-comparable, or contradictory evidence is `inconclusive` and
   blocks.
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
   test-authoring-only `expected_red`, continue to the verified commit gate. On
   `remediate`, launch remediation when fewer than two attempts have run. On
   `block`, or when no attempt remains, stop without broadening the phase.

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
   worker does not itself make the final stop decision.
4. Review every scope-clean remediation manifest and keep it unstaged and
   uncommitted. Launch a fresh read-only verifier regardless of the remediation
   validation result. Treat reviewed remediation changes as known phase state,
   not protected unrelated work.
5. Each remediation plus its fresh verification consumes one attempt. Permit at
   most two complete cycles. After attempt one, repeat only for a verifier
   disposition of `remediate`; after attempt two, any non-phase-safe verdict
   stops the workflow.

### Verified Implementation Commit Gate

After a phase-safe final verification:

1. Review the exact union of implementation and remediation manifests. Reject
   any path that did not pass the existing manifest and protection gates.
2. With commits enabled, stage that exact path union once. Use the appropriate
   `feat(<scope>):`, `fix(<scope>):`, or `chore(<scope>):` subject based on the
   assigned implementation-task intent, not merely the presence of remediation.
3. Record task IDs, exact files, focused and final verification, baseline
   comparison, resolved and deferred findings, remediation count, and prior SHA
   in the body. When no eligible paths remain, record `no_changes`.
4. Under `--no-commit`, leave the reviewed union unstaged. On a blocking verdict
   or exhausted cap, leave every implementation/remediation change unstaged and
   uncommitted; an earlier eligible test commit may remain.

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
5. Re-run the parser for the same phase and require `task_complete`,
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
when a typed finding or stage report is missing required fields, contradicts the
stage contract, or lacks enough evidence for the parent gate. Stop after the
verifier confirms a required failure cannot be resolved without crossing phase
scope, attributes a regression as uncertain, cannot prove downstream safety for
a proposed deferral, or returns a non-phase-safe verdict after attempt two.

Report selected phase, stage outcomes, task IDs, per-stage manifests, commits
or `--no-commit`, regression-baseline and attribution evidence, validation
summaries, expected failures, deferred findings, remediation count,
documentation path, workflow-completion state, protected unrelated files left
untouched, and blockers. Never claim a push.
