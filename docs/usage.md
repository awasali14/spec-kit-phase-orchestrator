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
/speckit.phase-orchestrator.phase phase 1 to 6 specs/002-feature/tasks.md
/speckit.phase-orchestrator.phase all specs/002-feature/tasks.md
/speckit.phase-orchestrator.phase phase 3 specs/002-feature/tasks.md --docs-dir Documentation/custom-feature
/speckit.phase-orchestrator.phase phase 3 specs/002-feature/tasks.md --no-commit
```

`next` selects the first phase whose workflow is incomplete. A phase with all
task checkboxes checked but missing final verified documentation resumes at
verification instead of being skipped.

`phase <number>` selects the requested phase only, even when earlier phases are
still incomplete.

`phase <start> to <end>` freezes an inclusive sequential queue. Both values
must be positive, every phase number in the range must exist, and `start` must
not exceed `end`. Phase 1 needs no prerequisite. For later starts, Phase
`start - 1` must have every task checkbox checked, but it need not have an
orchestrator document or workflow marker. Checked-but-undocumented phases
inside the range still resume at verification, and workflow-complete phases
inside the range are skipped unless rerunning is explicitly requested. The
queue never continues beyond `end`.

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
python3 .specify/extensions/phase-orchestrator/scripts/phase_tasks.py specs/002-feature/tasks.md --phase 1 --through-phase 6 --json
python3 .specify/extensions/phase-orchestrator/scripts/phase_tasks.py specs/002-feature/tasks.md --mode all --json
```

The JSON output includes the selected phase, complete structural task records and source digest, generated Markdown documentation path, `task_complete`,
`documentation_complete`, `workflow_complete`, `next_stage`, and a
workflow-aware phase queue for `all`.

Before selecting or planning workers in any mode, the parent reads and analyzes
the complete original `tasks.md`. That full-file analysis and frozen range or
queue state stay parent-only; workers receive compact phase-specific handoffs.

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
6. Parent-owned implementation and per-cycle remediation progress commits.
7. Documentation agent and commit after a phase-safe final verdict.

Later agents receive compact handoffs containing phase/task IDs, relevant
paths, baseline and prior validation summaries, stage validation expectations,
deferred findings, expected failures, and prior SHA/manifests. Current-stage
results and verdicts come only from the worker report. Remediation-cycle and
commit-control state remain parent-only, as do selector mode and phase-lifecycle
state. Every handoff includes the matching stage report schema contract and
form. Workers do not receive full traces, cycle counts, commit mode flags, or
queue/continuation metadata.

The test agent changes only assigned test tasks. It may report an intentional
RED result only when the failure is attributable to missing assigned
implementation. Syntax, collection, fixture, infrastructure, and unrelated
failures are reported after available in-scope correction; the parent then
stops the stage without a commit. The implementation agent inspects
committed tests directly, or the reviewed test manifest under `--no-commit`,
and runs the complete focused phase-test gate. If it cannot reach green, it
returns typed unresolved findings for independent verification rather than
making the final blocker decision. Verification is strictly read-only and
independently analyzes the actual phase diff, follows changed behavior through
callers, references, fixtures, parameterizations, and tests, and reports
focused, independent-phase, exact-baseline, and complete bounded
affected-subsystem validation. Commands in `tasks.md` are minimum coverage. It
continues all safe planned commands after a failure, aggregates related
in-phase findings, and records excluded surfaces as caveats. Every remediation
outcome is freshly verified. Before trusting any result, the parent
validates the completed report against the report schema and cross-checks it
against the assignment and observed Git manifest. Eligible implementation and
remediation work is committed immediately as a reversible checkpoint; later
verification still controls routing and documentation eligibility. Each later
verifier preserves the expanded verification surface established by the first.

A verifier decides repair scope before baseline origin. A proven, repairable
in-phase failure or defective test goes to remediation even when baseline
evidence is incomplete. A regression may be called phase-introduced or deferred
only when the pre-phase and current commands and
environments are comparable, failing test identities and material signatures
are unchanged, focused and independent-phase gates pass, and the parent proves
later queued phases do not depend on the affected behavior. The current phase
is excluded because it remains parser-incomplete until documentation. A new or
worsened regression is remediated within phase scope; uncertain scope, required
cross-phase repair, or an unproven out-of-phase failure stops the workflow. A
test-authoring-only phase may still complete with attributable expected RED.

Whenever a validation-running stage executes a project command, it prefers an
already-authorized route outside the Codex sandbox. If none is currently
permitted, it runs the exact command inside. Passing results and ordinary
assertion/product failures are used normally. A plausibly sandbox-related
failure is never attributed to the code until the exact command is rerun
outside with user permission. The worker requests approval first. If it cannot
obtain approval, the parent asks the user and relaunches a fresh worker for the
same stage when approved. The outside result is authoritative. Only a denied or
still-unavailable parent request produces an environment blocker with the
command and a compact signature. Neither the blocker nor relaunch consumes a
remediation attempt. Documentation workers do not run project validation and
are unaffected by this policy.

The documentation agent receives aggregate stage reports, SHAs, manifests,
baseline comparisons, and deferred findings. It changes only the resolved phase
execution document and records `<!-- phase-orchestrator:workflow-complete v2 -->`
after a phase-safe final verdict.

## Parent-Owned Git Gates

Before every stage, the parent records HEAD and the working-tree baseline.
After an eligible successful gate, it reviews and stages only exact paths:

- `test(scope): add phase N coverage`, with the expected RED explained when
  applicable.
- One intent-based `feat`, `fix`, or `chore` commit for the implementation
  stage's exact paths after a valid `passed` or `unresolved` result.
- `fix(scope): remediate phase N findings` for each eligible remediation cycle.
- `docs(scope): document phase N execution` for final documentation.

Commit bodies record stage status, task or finding IDs, exact files, validation,
expected or unresolved evidence when applicable, and prior SHA.
Baseline/verifier workers never commit, and the orchestrator never pushes.

A phase with test, implementation, and documentation changes normally produces
three commits and may produce up to five when both remediation cycles change
files. Blocking verification does not erase earlier progress checkpoints.

Use `--no-commit` or clear wording such as "do not commit" to opt out. In that
case, every stage and gate still runs, the parent tracks a manifest per stage,
and accumulated reviewed changes remain unstaged.

If a stage creates unrelated/generated artifacts or overlaps a file that was
dirty in its baseline, stop without touching unrelated pre-existing changes.

## Task Classification

The parser inventories task IDs, full text, sections, and checkbox state. The
parent classifies tasks by primary deliverable, records a brief rationale, and
saves a durable assignment manifest. Commands used to verify work do not
determine its primary deliverable. Test filenames and headings cannot override
task meaning.

The parent runs `scripts/validate_assignments.py` before dispatch to check exact
coverage and source freshness. All phase IDs are recorded once, including checked
IDs; only unchecked IDs are dispatched. Parser `next_stage: classification`
indicates pending assignment validation. Role groups now come exclusively from
the assignment validator; `tests_first_tasks` is removed.

Resume reuses assignments. A worker raises a suspected mismatch by ending its
turn with a clarification question, separate from its final stage report. The
parent reviews it and either continues the same worker with an explanatory
follow-up or corrects the assignment for the appropriate role.
Confirmed mistakes or source edits require an archived revision,
a correction reason, reconciliation of checkbox evidence, and validation before a
fresh worker starts. See the command's Parent-Owned Task Assignments section for
the manifest format, storage path, and correction procedure.

## Validation And Documentation

Each owning stage marks its assigned task checkboxes only after its gate.
Documentation records aggregate stage results, exact changed paths, validation,
commit SHAs, remediation attempts, caveats, the workflow-complete marker, and a
styled Phase Flow Mermaid diagram unless the user explicitly opts out.
