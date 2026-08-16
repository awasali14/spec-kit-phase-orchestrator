---
description: "Use /speckit.phase-orchestrator.phase or $speckit-phase-orchestrator-phase to run Spec Kit tasks.md through isolated test, implementation, verification, remediation, and documentation agents with parent-owned gated commits."
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
   expected failures, and remediation attempt. Never pass full traces,
   transcripts, parent plans, or another role's instructions.
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
and `schemas/phase-handoff.schema.json` contract v2 as the source of truth.
Populate `stage`, assigned IDs, phase scope, relevant paths, prior SHA,
prior manifest and validation, expected failures, remediation attempt, and
conditional commit eligibility. Sanitize the prompt and append only the chosen
role section.

Route official implementation discipline, relevant skills,
and automatically selected frontend/backend skills and MCPs only to the phase
stages that need them. Include the selected MCPs, applicable MCP opt-outs, and
Exa-first web-search policy in each handoff. Keep tool notes similarly scoped.
Do not leak parent orchestration context. Only the documentation stage receives
the phase document path/template or Mermaid instructions.

## Stage Sequence

Run this state machine for one selected phase:

```text
test when non-empty
  -> implementation when non-empty
  -> verification (always, fresh, read-only)
  -> remediation on failure
  -> verification (fresh, read-only)
  -> documentation after final pass (always)
```

Skip an empty test or implementation stage. Always verify and document.
Starting from parser `next_stage` may skip already completed task stages, but
must still run a fresh verification before documentation.

### Test Stage

Assign only incomplete `test_tasks`.

1. The test agent may change assigned tests, explicitly assigned test-only
   support, and its task checkboxes. It must not implement production behavior.
2. Require the complete focused gate before checkboxes are marked. Do not run
   independent-phase or regression validation in this stage; reserve those for
   the verifier.
3. Accept either green or intentional RED. RED is eligible only when tests
   collect and execute correctly and every failure is attributable to missing
   assigned implementation.
4. Syntax, collection, fixture, infrastructure, environment, flaky, and
   unrelated failures stop the workflow. Require assigned checkboxes to match
   their baseline unchecked state, correcting only those checkbox edits when
   necessary. Do not commit.
5. Review the exact manifest. With commits enabled, stage only those paths and
   commit an eligible intentional change as:

   ```text
   test(<scope>): add phase <N> coverage
   ```

   The body must record stage, assigned task IDs, exact files, validation,
   expected RED failures and attribution when applicable, and prior SHA.

### Implementation Stage

Assign only incomplete `implementation_tasks`.

1. The implementation agent inspects the reviewed tests directly: from the
   prior commit in commit mode, or the prior reviewed manifest under
   `--no-commit`.
2. It implements only assigned implementation/setup tasks and marks only those
   checkboxes after focused validation.
3. Require green focused validation. Failed implementation changes are not
   commit eligible; stop with them unstaged.
4. Review the exact manifest. With commits enabled, stage exact paths and use
   the appropriate `feat(<scope>):`, `fix(<scope>):`, or `chore(<scope>):`
   subject. The body must record stage, task IDs, exact files, green validation,
   and prior SHA.

### Verification Stage

Launch a fresh verification agent after task stages and after every successful
remediation.

1. Make it strictly read-only. It must not modify checkboxes, source, tests,
   snapshots, caches, coverage, reports, or documentation.
2. Require a structured report with separate focused, independent-phase, and
   suitable regression results, plus scope/artifact findings and one verdict.
3. Confirm the working tree and index exactly match the pre-verification
   baseline. Reject any verifier-created path. A verifier never commits.
4. On pass, continue to documentation. On failure, continue to remediation if
   fewer than two remediation attempts have run.

### Remediation And Fresh Re-verification

1. Launch a fresh remediation agent with only the verifier's compact findings,
   phase scope, relevant paths, validation summary, prior SHA/manifest, and
   attempt number.
2. It may change phase-scoped code, tests, fixtures, and necessary phase task
   checkboxes. It must not broaden scope.
3. Require its focused validation to pass before any parent commit. Reserve
   the full independent-phase and regression gates for the fresh verifier.
   Failed remediation changes remain unstaged and uncommitted, and the
   workflow stops.
4. After an eligible remediation, review and stage only exact paths. Commit:

   ```text
   fix(<scope>): resolve phase <N> validation findings
   ```

   Record stage, affected task IDs, exact files, resolved findings, green
   validation, remediation attempt, and prior SHA in the body.
5. Launch a fresh read-only verifier. Permit at most two complete
   remediation/re-verification cycles. If the second re-verification fails,
   stop and leave all failed post-commit changes unstaged and uncommitted.

### Documentation Stage

Launch only after the final fresh verification passes.

1. Give the documentation agent aggregate compact stage reports, commit SHAs,
   reviewed manifests, validation summaries, expected RED failures, and
   remediation history.
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
   when the document records a passing final verification.
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
RED, failed implementation/remediation gate, verifier mutation, missing
isolation, schema-invalid report, documentation mutation outside its file, or
exhausted remediation cap.

Report selected phase, stage outcomes, task IDs, per-stage manifests, commits
or `--no-commit`, validation summaries, expected failures, remediation count,
documentation path, workflow-completion state, protected unrelated files left
untouched, and blockers. Never claim a push.
