---
description: Run Spec Kit tasks.md phases with isolated subagent handoffs.
---

# Speckit Phase

You are running the Spec Kit Phase Orchestrator extension.

This command is a companion workflow. It does not replace, bypass, or modify
the official /speckit.implement command.

## Supported Prompt Arguments

Use one of these forms:

1. `next <tasks.md path> [--docs-dir <directory>] [--no-commit]`
2. `phase <number> <tasks.md path> [--docs-dir <directory>] [--no-commit]`
3. `all <tasks.md path> [--docs-dir <directory>] [--no-commit]`

Examples:

```text
/speckit.phase-orchestrator.phase next specs/002-feature/tasks.md
/speckit.phase-orchestrator.phase phase 3 specs/002-feature/tasks.md
/speckit.phase-orchestrator.phase all specs/002-feature/tasks.md
/speckit.phase-orchestrator.phase phase 3 specs/002-feature/tasks.md --docs-dir Documentation/custom-feature
/speckit.phase-orchestrator.phase phase 3 specs/002-feature/tasks.md --no-commit
```

Users may also provide an explicit Markdown documentation file path in natural
language. That user-provided path wins over generated defaults.

## Workflow

1. Parse the prompt arguments.
2. Locate the target `tasks.md`.
3. Run
   `python3 .specify/extensions/phase-orchestrator/scripts/phase_tasks.py <tasks.md> --mode next --json`,
   `python3 .specify/extensions/phase-orchestrator/scripts/phase_tasks.py <tasks.md> --phase <number> --json`, or
   `python3 .specify/extensions/phase-orchestrator/scripts/phase_tasks.py <tasks.md> --mode all --json`.
   When the prompt includes `--docs-dir`, pass it through to the parser.
4. If the user provided a documentation directory or documentation path outside
   `--docs-dir`, use it exactly in the phase handoff. Otherwise use the
   parser-generated Markdown documentation path under
   `Documentation/{feature-slug}/`.
5. Select exactly one phase to execute.
6. Build the worker handoff from:
   - the parser JSON,
   - `.specify/extensions/phase-orchestrator/references/worker-prompt-template.md`,
   - `.specify/extensions/phase-orchestrator/references/phase-doc-template.md`, and
   - `.specify/extensions/phase-orchestrator/references/mermaid-style.md`.
7. Sanitize the handoff before giving it to a worker. Parent orchestration
   details are not worker instructions.
8. If subagents or isolated worker contexts are supported, use exactly one
   worker for the selected phase.
9. If subagents or isolated worker contexts are not supported, abort and
   inform the user about it.
10. Write the phase documentation.
11. Re-run the parser for the same phase and confirm the expected task state.
12. Confirm expected task completion and that the phase documentation file
    exists.
13. Confirm the Markdown phase execution document includes a Mermaid block
    unless the user explicitly opted out.
14. Review `git status --short` and the phase diff.
15. Run the parent post-phase gate described below: commit selected-phase files
    by default, or skip staging/commit when the user provided `--no-commit` or
    clearly said not to commit.
16. Stop after one phase unless the prompt used `all`.
17. In `all` mode, the parent repeats this workflow one phase at a time and
    re-runs the parser after each completed phase. Do not pass `all` mode or
    continuation instructions to the worker as executable instructions.

## Worker Prompt Rules

1. Use `.specify/extensions/phase-orchestrator/references/worker-prompt-template.md`
   as the source of truth for the worker prompt.
2. Populate the template from the parser output and selected-phase context,
   including phase metadata, incomplete task IDs, test-first tasks,
   implementation/setup tasks, documentation path, validation expectations,
   previous phase docs, the official implementation workflow/skill
   (`/speckit.implement` or `$speckit-implement`), relevant invoker-supplied
   skills, parent-read summaries, MCP/tool notes, and the Mermaid style
   reference path.
3. Sanitize the handoff according to the template's sanitization rules before
   giving it to a worker.

The worker prompt must not include:

1. Parent-only worker-spawn configuration.
2. Model or effort directives such as `GPT 5.4`, `medium effort`, fallback
   model-selection text, or orchestration advice.
3. Instructions to run this phase-orchestrator command again.
4. Instructions to spawn subagents.
5. Parent-only post-phase gate actions.
6. `all` mode, phase queue, post-phase validation, or parent continuation
   instructions as executable worker instructions.

Model and effort selection belongs to the parent process that creates the
worker. It is configuration, not executable phase work.

## Skill And MCP Handling

1. If the user supplies skills grouped by phase or use case, pass only the
   selected phase's skill instructions and relevant use-case notes into the
   worker prompt. Keep unrelated phase skill lists out of the worker prompt.
2. Always include the official implementation workflow/skill
   (`/speckit.implement` or `$speckit-implement`) in the worker prompt. This is
   required implementation discipline, not an optional invoker-supplied skill.
3. Always preserve relevant phase skills supplied by the invoker, including
   use-case notes such as UI, copy, data, infrastructure, or evaluation
   guidance. Include concise parent-read reference summaries when the parent
   already inspected material the worker needs.
4. When Exa MCP or an equivalent code-context/web MCP is available, include its
   availability note in every worker prompt. Include database-specific MCP notes
   only when the selected phase tasks or skills mention database-layer work
   such as database, Supabase, Postgres, SQL, migrations, RLS, grants, or
   storage policies.

## Mermaid Reference Handling

Before handing work to a worker, ensure the worker prompt points to
`.specify/extensions/phase-orchestrator/references/mermaid-style.md` as the
source for the required Mermaid `classDef` and `linkStyle` lines. The parent
does not need to paste the style snippet into the worker prompt.

## Safety Rules

1. Do not modify official `/speckit.implement`.
2. Do not work on another phase unless `all` mode is active and the previous
   phase completed cleanly.
3. If unrelated changes are mixed into the same file as phase changes, stop
   and ask the user how to proceed.
4. If validation fails, document the failure and stop.
5. If instructions are ambiguous, ask before implementing.
6. Do not classify fixture/helper/setup tasks as tests merely because their
   paths live under `tests/`.
7. Do not mention databases, MCP servers, or external services unless the
   selected phase tasks, user-requested skills, or available context make them
   relevant.

## Parent Post-Phase Commit

After a worker reports completion, the parent orchestrator owns the post-phase
gate:

1. Re-run the parser for the same phase.
2. Confirm the expected task IDs are complete.
3. Confirm the Markdown documentation file exists.
4. Confirm the Markdown phase execution document includes a Mermaid block
   unless the user explicitly opted out.
5. Review `git status --short` and the phase diff.
6. Stage only selected-phase files.
7. Create one professional Conventional Commit.

Use a concise subject such as:

```text
feat(scope): complete phase 3 workspace entry
```

Include this information in the commit body:

```text
Completed tasks: T007, T008, T009
Changed files:
- path/to/file
Validation:
- npm test -- focused: passed
Documentation: Documentation/.../phase-3-...-execution.md
```

If the user includes `--no-commit` or clearly says not to commit, skip staging
and commit creation, then report changed files for manual review. Never push;
the user owns pushing to remotes.

## Worker Final Summary

The worker final summary must include:

1. Completed task IDs.
2. Modified and added/created files.
3. Validation commands and results.
4. Documentation path.
5. Caveats, blockers, or validation gaps.
