# Usage

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

`next` selects the first phase that still has unchecked tasks.

`phase <number>` selects the requested phase only, even when earlier phases are
still incomplete.

`all` runs the remaining incomplete phases sequentially. Use it when the task
file is clear, validation is reliable, and you want each phase to stop at its
own validation and documentation gate.

Avoid `all` when the feature contains unresolved design choices, risky data
migrations, unclear acceptance criteria, or a dirty git state that needs manual
review.

## Parser

The supporting parser can be run directly:

```bash
python3 scripts/phase_tasks.py examples/sample-tasks.md --mode next --json
python3 scripts/phase_tasks.py examples/sample-tasks.md --phase 3 --json
python3 scripts/phase_tasks.py examples/sample-tasks.md --mode all --json
```

The JSON output includes the selected phase, incomplete task IDs, test tasks,
`tests_first_tasks`, implementation tasks, generated Markdown documentation
path, receipt contract path, and a queue of selected phases for `all`.

By default, Markdown phase documentation is generated under:

```text
Documentation/{feature-slug}/phase-{number}-{phase-slug}-execution.md
```

Receipt contracts are generated separately under:

```text
.specify/phase-orchestrator/receipts/{feature-slug}/phase-{number}-{phase-slug}-receipt.json
```

Use `--docs-dir <directory>` to override the generated directory:

```bash
python3 scripts/phase_tasks.py examples/sample-tasks.md --phase 3 --docs-dir Documentation/custom-feature --json
```

## Post-Phase Commits

After a phase completes cleanly, the parent orchestrator re-runs the parser,
checks expected task completion, confirms the Markdown documentation and
receipt contract files, validates the receipt shape, reviews
`git status --short` and the phase diff, stages only selected-phase files, and
creates one professional Conventional Commit.

Use `--no-commit` or clear wording such as "do not commit" to opt out. In that
case, the parent skips staging and commit creation and reports changed files
for manual review. The orchestrator never pushes to a remote repository.

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

Each phase should run focused validation before task checkboxes are marked
complete. A phase should also produce a short Markdown execution document that
records completed task IDs, selected-phase changed files, focused validation
commands, issues, and a styled Phase Flow Mermaid diagram unless the user
explicitly asks to omit diagrams. The receipt JSON is a validation/contract
artifact, not user-facing documentation.

Receipts must match `schemas/phase-receipt.schema.json` exactly. Use
snake_case fields such as `completed_task_ids` and `changed_files`; do not use
camelCase variants or ad hoc metadata fields.

If validation fails, the workflow should document the failure and stop.
