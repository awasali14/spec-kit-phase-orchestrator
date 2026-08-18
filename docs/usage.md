# Usage

This guide explains command selection, parser output, staged workers, validation
gates, and parent-owned Git behavior for the phase orchestrator.

Spec Kit generates a `tasks.md` file for a feature after planning. Users
usually find it under a feature directory such as `specs/002-feature/tasks.md`.
The file groups implementation work into phases, often including setup,
foundation, user stories, and polish.

Spec Kit Phase Orchestrator reads that existing file and selects phase-scoped
work. It does not create the feature plan and it does not replace
`/speckit.implement`.

## Command Forms

Use one of these prompt forms:

```text
/speckit.phase-orchestrator.phase next specs/002-feature/tasks.md
/speckit.phase-orchestrator.phase phase 3 specs/002-feature/tasks.md
/speckit.phase-orchestrator.phase all specs/002-feature/tasks.md
/speckit.phase-orchestrator.phase phase 3 specs/002-feature/tasks.md --docs-dir Documentation/custom-feature
/speckit.phase-orchestrator.phase phase 3 specs/002-feature/tasks.md --no-commit
```

`next` selects the first phase whose workflow is incomplete. A phase with all
task checkboxes checked but missing final verified documentation resumes at
verification instead of being skipped.

`phase <number>` selects the requested phase only, even when earlier phases are
still incomplete.

`all` runs the remaining workflow-incomplete phases sequentially. Every gate,
including final verification and documentation completion, must pass before it
moves to the next phase.

Avoid `all` when the feature contains unresolved design choices, risky data
migrations, unclear acceptance criteria, or a dirty git state that needs manual
review.

## Parser

The supporting parser can be run directly:

```bash
python3 .specify/extensions/phase-orchestrator/scripts/phase_tasks.py specs/002-feature/tasks.md --mode next --json
python3 .specify/extensions/phase-orchestrator/scripts/phase_tasks.py specs/002-feature/tasks.md --phase 3 --json
python3 .specify/extensions/phase-orchestrator/scripts/phase_tasks.py specs/002-feature/tasks.md --mode all --json
```

The JSON output includes the selected phase, test and implementation task
classification, generated Markdown documentation path, `task_complete`,
`documentation_complete`, `workflow_complete`, `next_stage`, and a
workflow-aware phase queue for `all`.

By default, Markdown phase documentation is generated under:

```text
Documentation/{feature-slug}/phase-{number}-{phase-slug}-execution.md
```

Use `--docs-dir <directory>` to override the generated directory:

```bash
python3 .specify/extensions/phase-orchestrator/scripts/phase_tasks.py specs/002-feature/tasks.md --phase 3 --docs-dir Documentation/custom-feature --json
```

See [`examples.md`](examples.md) for a copyable `tasks.md`, representative
parser output, and an end-to-end worker handoff and result.

## Staged Workflow

The parent runs these stages sequentially in isolated contexts that share the
repository:

1. Read-only regression-baseline agent before phase mutations.
2. Test agent, skipped when no test tasks remain.
3. Implementation agent, skipped when no implementation/setup tasks remain.
4. Read-only verification agent, always run.
5. Remediation agent followed by a fresh read-only verifier for every
   remediation result, with at most two cycles.
6. Verified implementation/remediation commit gate.
7. Documentation agent after a phase-safe final verdict.

Later agents receive compact handoffs containing phase/task IDs, relevant
paths, baseline and current validation summaries, deferred findings, expected
failures, prior SHA/manifests, and the remediation attempt when applicable.
They do not receive full traces.

The test agent changes only assigned test tasks. It may report an intentional
RED result only when the failure is attributable to missing assigned
implementation. Syntax, collection, fixture, infrastructure, and unrelated
failures stop the stage without a commit. The implementation agent inspects
committed tests directly, or the reviewed test manifest under `--no-commit`,
and runs the complete focused phase-test gate. If it cannot reach green, it
returns typed unresolved findings for independent verification rather than
making the final blocker decision. Verification is strictly read-only and
reports focused, independent-phase, and suitable regression validation. Every
remediation outcome is freshly verified. Implementation and remediation remain
uncommitted until a phase-safe verdict.

A regression may be deferred only when the pre-phase and current commands and
environments are comparable, failing test identities and material signatures
are unchanged, focused and independent-phase gates pass, and the parent proves
later queued phases do not depend on the affected behavior. The current phase
is excluded because it remains parser-incomplete until documentation. A new or
worsened regression is remediated within phase scope; uncertainty or required
scope crossing stops the workflow. A test-authoring-only phase may still
complete with attributable expected RED.

The documentation agent receives aggregate stage reports, SHAs, manifests,
baseline comparisons, and deferred findings. It changes only the resolved phase
execution document and records `<!-- phase-orchestrator:workflow-complete v2 -->`
after a phase-safe final verdict.

## Parent-Owned Git Gates

Before every stage, the parent records HEAD and the working-tree baseline.
After an eligible successful gate, it reviews and stages only exact paths:

- `test(scope): add phase N coverage`, with the expected RED explained when
  applicable.
- One intent-based `feat`, `fix`, or `chore` commit for the exact accumulated
  implementation/remediation path union after phase-safe verification.
- `docs(scope): document phase N execution` for final documentation.

Commit bodies record task IDs, files, baseline comparison, validation,
remediation, deferred and expected failures when applicable, and prior SHA.
Baseline/verifier workers never commit, and the orchestrator never pushes.

Use `--no-commit` or clear wording such as "do not commit" to opt out. In that
case, every stage and gate still runs, the parent tracks a manifest per stage,
and accumulated reviewed changes remain unstaged.

If a stage creates unrelated/generated artifacts or overlaps a file that was
dirty in its baseline, stop without touching unrelated pre-existing changes.

## Task Classification

The parser separates incomplete tasks into `test_tasks` and
`implementation_tasks` for worker handoff compatibility.

Tasks are classified as tests when they are under headings like `Tests`,
`Tests First`, or `Tests for Phase N`; when they use explicit test-writing or
test-running wording; or when they target actual test/spec files such as
`.test.*`, `.spec.*`, or `test_*`.

Fixture, fake, helper, mock, setup, utility, factory, and scaffolding tasks are
treated as implementation/setup tasks when their only test signal is a path
under `tests/`.

## Validation And Documentation

Each owning stage marks its assigned task checkboxes only after its gate.
Documentation records aggregate stage results, exact changed paths, validation,
commit SHAs, remediation attempts, caveats, the workflow-complete marker, and a
styled Phase Flow Mermaid diagram unless the user explicitly opts out.
