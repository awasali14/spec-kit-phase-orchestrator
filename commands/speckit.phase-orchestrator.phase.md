---
description: Run an existing Spec Kit tasks.md one phase at a time with clean agent context.
---

# Speckit Phase

You are running the Spec Kit Phase Orchestrator extension.

This command is a companion workflow. It does not replace, bypass, or modify
the official /speckit.implement command.

## Supported Prompt Arguments

Use one of these forms:

1. `next <tasks.md path> [--docs-dir <directory>]`
2. `phase <number> <tasks.md path> [--docs-dir <directory>]`
3. `all <tasks.md path> [--docs-dir <directory>]`

Examples:

```text
/speckit.phase-orchestrator.phase next specs/002-feature/tasks.md
/speckit.phase-orchestrator.phase phase 3 specs/002-feature/tasks.md
/speckit.phase-orchestrator.phase all specs/002-feature/tasks.md
/speckit.phase-orchestrator.phase phase 3 specs/002-feature/tasks.md --docs-dir Documentation/custom-feature
```

Users may also provide an explicit documentation file path or receipt file path
in natural language. Those user-provided paths win over generated defaults.

## Workflow

1. Parse the prompt arguments.
2. Locate the target `tasks.md`.
3. Run
   `python3 .specify/extensions/phase-orchestrator/scripts/phase_tasks.py <tasks.md> --mode next --json`,
   `python3 .specify/extensions/phase-orchestrator/scripts/phase_tasks.py <tasks.md> --phase <number> --json`, or
   `python3 .specify/extensions/phase-orchestrator/scripts/phase_tasks.py <tasks.md> --mode all --json`.
   When the prompt includes `--docs-dir`, pass it through to the parser.
4. If the user provided a documentation directory, documentation path, or
   receipt path outside `--docs-dir`, use it exactly in the phase handoff.
   Otherwise use the parser-generated root
   `Documentation/{feature-slug}/phase-{number}-{phase-slug}-...` paths.
5. Select exactly one phase to execute.
6. Build the worker/local handoff from:
   - the parser JSON,
   - `.specify/extensions/phase-orchestrator/references/worker-prompt-template.md`,
   - `.specify/extensions/phase-orchestrator/references/phase-doc-template.md`, and
   - `.specify/extensions/phase-orchestrator/references/mermaid-style.md`.
7. Sanitize the handoff before giving it to a worker. Parent orchestration
   details are not worker instructions.
8. If subagents or isolated worker contexts are supported, use exactly one
   worker for the selected phase.
9. If subagents are not supported, execute locally using the same phase scope.
10. Complete only the selected phase's incomplete tasks.
11. Mark completed task checkboxes as `[X]`.
12. Run focused validation.
13. Write the phase receipt and phase documentation.
14. Re-run the parser for the same phase and confirm the expected task state.
15. Stop after one phase unless the prompt used `all`.
16. In `all` mode, the parent repeats this workflow one phase at a time and
    re-runs the parser after each completed phase. Do not pass `all` mode or
    continuation instructions to the worker as executable instructions.

## Worker Prompt Rules

Use `.specify/extensions/phase-orchestrator/references/worker-prompt-template.md`
to create the worker prompt. The worker prompt must include:

1. The selected phase number, title, purpose/checkpoint/independent test when
   available, and incomplete task IDs.
2. Test-first tasks and implementation/setup tasks from the parser output.
3. Scope rules that stop the worker after the selected phase.
4. Documentation and receipt paths.
5. Focused validation expectations.
6. Relevant invoker-supplied skills for the selected phase, including concise
   summaries of any parent-read references that the worker needs.
7. The official implementation workflow/skill when available
   (`/speckit.implement` or `$speckit-implement`) for implementation discipline
   and task tracking.
8. Previous completed phase documentation paths when supplied or discovered.
9. MCP notes according to the availability policy in the worker prompt template.

The worker prompt must not include:

1. Parent-only worker-spawn configuration.
2. Model or effort directives such as `Codex 5.3`, `medium effort`, fallback
   model-selection text, or orchestration advice.
3. Instructions to run this phase-orchestrator command again.
4. Instructions to spawn subagents.
5. Instructions to stage or commit.
6. `all` mode, phase queue, post-phase validation, or parent continuation
   instructions as executable worker instructions.

Model and effort selection belongs to the parent process that creates the
worker. It is configuration, not executable phase work.

## Skill And MCP Handling

If the user supplies skills grouped by phase or use case, pass only the
selected phase's skill instructions and relevant use-case notes into the worker
prompt. Keep unrelated phase skill lists out of the worker prompt.

Always preserve relevant phase skills supplied by the invoker, including
use-case notes such as UI, copy, data, infrastructure, or evaluation guidance.
Include concise parent-read reference summaries when the parent already
inspected material the worker needs.

When Exa MCP or an equivalent code-context/web MCP is available, include its
availability note in every worker prompt. Include database-specific MCP notes
only when the selected phase tasks or skills mention database-layer work such
as database, Supabase, Postgres, SQL, migrations, RLS, grants, or storage
policies.

## Safety Rules

1. Do not modify official `/speckit.implement`.
2. Do not work on another phase unless `all` mode is active and the previous
   phase completed cleanly.
3. Do not stage or commit unrelated files.
4. If unrelated changes are mixed into the same file as phase changes, stop
   and ask the user how to proceed.
5. If validation fails, document the failure and stop.
6. If instructions are ambiguous, ask before implementing.
7. Do not classify fixture/helper/setup tasks as tests merely because their
   paths live under `tests/`.
8. Do not mention databases, MCP servers, or external services unless the
   selected phase tasks, user-requested skills, or available context make them
   relevant.

## Worker Final Summary

The worker or local execution final summary must include:

1. Completed task IDs.
2. Changed files.
3. Validation commands and results.
4. Documentation path.
5. Receipt path.
6. Caveats, blockers, or validation gaps.
