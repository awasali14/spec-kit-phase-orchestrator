---
description: Run an existing Spec Kit tasks.md one phase at a time with clean agent context.
---

# Speckit Phase

You are running the Spec Kit Phase Orchestrator extension.

This command is a companion workflow. It does not replace, bypass, or modify
the official /speckit.implement command.

## Supported Prompt Arguments

Use exactly one of these forms:

1. `next <tasks.md path>`
2. `phase <number> <tasks.md path>`
3. `all <tasks.md path>`

Examples:

```text
/speckit.phase-orchestrator.phase next specs/002-feature/tasks.md
/speckit.phase-orchestrator.phase phase 3 specs/002-feature/tasks.md
/speckit.phase-orchestrator.phase all specs/002-feature/tasks.md
```

## Workflow

1. Parse the prompt arguments.
2. Locate the target `tasks.md`.
3. Run `python3 scripts/phase_tasks.py <tasks.md> --mode next --json`,
   `python3 scripts/phase_tasks.py <tasks.md> --phase <number> --json`, or
   `python3 scripts/phase_tasks.py <tasks.md> --mode all --json`.
4. Select exactly one phase to execute.
5. If subagents or isolated worker contexts are supported, use exactly one
   worker for the selected phase.
6. If subagents are not supported, execute locally using the same phase scope.
7. Complete only the selected phase's incomplete tasks.
8. Mark completed task checkboxes as `[X]`.
9. Run focused validation.
10. Write a phase receipt and phase documentation.
11. Stop after one phase unless the prompt used `all`.

## Safety Rules

1. Do not modify official `/speckit.implement`.
2. Do not work on another phase unless `all` mode is active and the previous
   phase completed cleanly.
3. Do not stage or commit unrelated files.
4. If unrelated changes are mixed into the same file as phase changes, stop
   and ask the user how to proceed.
5. If validation fails, document the failure and stop.
6. If instructions are ambiguous, ask before implementing.
