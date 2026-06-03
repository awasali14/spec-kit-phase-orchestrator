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
implementation tasks, and a queue of selected phases for `all`.

## Validation And Documentation

Each phase should run focused validation before task checkboxes are marked
complete. A phase should also produce a receipt and a short phase execution
document that records completed task IDs, changed files, validation commands,
and issues.

If validation fails, the workflow should document the failure and stop.
