---
description: Run an existing Spec Kit tasks.md one phase at a time with clean agent context.
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

Users may also provide an explicit Markdown documentation file path or receipt
contract path in natural language. Those user-provided paths win over generated
defaults.
If the user includes `--no-commit` or clearly says not to commit, skip
post-phase staging and commit creation.

## Workflow

1. Parse the prompt arguments.
2. Locate the target `tasks.md`.
3. Run
   `python3 .specify/extensions/phase-orchestrator/scripts/phase_tasks.py <tasks.md> --mode next --json`,
   `python3 .specify/extensions/phase-orchestrator/scripts/phase_tasks.py <tasks.md> --phase <number> --json`, or
   `python3 .specify/extensions/phase-orchestrator/scripts/phase_tasks.py <tasks.md> --mode all --json`.
   When the prompt includes `--docs-dir`, pass it through to the parser.
4. If the user provided a documentation directory, documentation path, or
   receipt contract path outside `--docs-dir`, use it exactly in the phase
   handoff. Otherwise use the parser-generated Markdown documentation path
   under `Documentation/{feature-slug}/` and receipt contract path under
   `.specify/phase-orchestrator/receipts/{feature-slug}/`.
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
13. Write the phase documentation and receipt contract.
14. Re-run the parser for the same phase and confirm the expected task state.
15. Confirm expected task completion and that the phase documentation and
    receipt contract files exist.
16. Validate the receipt shape against
    `.specify/extensions/phase-orchestrator/schemas/phase-receipt.schema.json`
    manually or with a lightweight JSON/schema check. At minimum, confirm it is
    parseable JSON with the required snake_case top-level keys
    `schema_version`, `status`, `phase`, `completed_task_ids`,
    `changed_files`, `validation`, `documentation_path`, `receipt_path`, and
    `issues`, and no ad hoc keys such as `completedTaskIds`, `changedFiles`,
    `generatedAt`, `name`, or `priority`.
17. Review `git status --short` and the phase diff.
18. Unless the user provided `--no-commit` or clearly said not to commit, stage
    only selected-phase files and create one professional Conventional Commit.
    The commit body must include completed task IDs, changed files, validation,
    Markdown documentation path, and receipt contract path.
19. If commits are disabled, do not stage files. Report the changed files for
    manual review.
20. Never push. Pushing is always user-owned.
21. Stop after one phase unless the prompt used `all`.
22. In `all` mode, the parent repeats this workflow one phase at a time and
    re-runs the parser after each completed phase. Do not pass `all` mode or
    continuation instructions to the worker as executable instructions.

## Worker Prompt Rules

Use `.specify/extensions/phase-orchestrator/references/worker-prompt-template.md`
to create the worker prompt. The worker prompt must include:

1. The selected phase number, title, purpose/checkpoint/independent test when
   available, and incomplete task IDs.
2. Test-first tasks and implementation/setup tasks from the parser output.
3. Scope rules that stop the worker after the selected phase.
4. Markdown documentation path and receipt contract path.
5. Focused validation expectations.
6. Relevant invoker-supplied skills for the selected phase, including concise
   summaries of any parent-read references that the worker needs.
7. The official implementation workflow/skill when available
   (`/speckit.implement` or `$speckit-implement`) for implementation discipline
   and task tracking.
8. Previous completed phase documentation paths when supplied or discovered.
9. MCP notes according to the availability policy in the worker prompt template.
10. Receipt requirements that match
    `.specify/extensions/phase-orchestrator/schemas/phase-receipt.schema.json`.
11. The actual Mermaid style reference from
    `.specify/extensions/phase-orchestrator/references/mermaid-style.md`,
    including the `classDef` and `linkStyle` lines.
12. Guidance that the Phase Flow Mermaid diagram is required unless the user
    explicitly asked to omit diagrams for this run.

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

## Mermaid Reference Handling

Before handing work to a worker, paste or concisely summarize the actual
`.specify/extensions/phase-orchestrator/references/mermaid-style.md` snippet in
the `Mermaid style reference` section of the worker prompt. Include the
`classDef` and `linkStyle` lines exactly so the worker can copy the
dark/emerald style without guessing.

## Safety Rules

1. Do not modify official `/speckit.implement`.
2. Do not work on another phase unless `all` mode is active and the previous
   phase completed cleanly.
3. Workers must not stage or commit. The parent may stage only selected-phase
   files and create the post-phase commit unless the user opted out.
4. If unrelated changes are mixed into the same file as phase changes, stop
   and ask the user how to proceed.
5. If validation fails, document the failure and stop.
6. If instructions are ambiguous, ask before implementing.
7. Do not classify fixture/helper/setup tasks as tests merely because their
   paths live under `tests/`.
8. Do not mention databases, MCP servers, or external services unless the
   selected phase tasks, user-requested skills, or available context make them
   relevant.
9. Do not push to a remote repository.

## Parent Post-Phase Commit

After a worker or local phase run reports completion, the parent orchestrator
owns the post-phase gate:

1. Re-run the parser for the same phase.
2. Confirm the expected task IDs are complete.
3. Confirm the Markdown documentation and receipt contract files exist.
4. Validate the receipt JSON shape against the receipt schema manually or with
   a lightweight schema check.
5. Confirm the Markdown phase execution document includes a Mermaid block
   unless the user explicitly opted out.
6. Review `git status --short` and the phase diff.
7. Stage only selected-phase files.
8. Create one professional Conventional Commit.

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
Receipt contract: .specify/phase-orchestrator/receipts/.../phase-3-...-receipt.json
```

If the user includes `--no-commit` or clearly says not to commit, skip staging
and commit creation, then report changed files for manual review. Never push;
the user owns pushing to remotes.

## Worker Final Summary

The worker or local execution final summary must include:

1. Completed task IDs.
2. Changed files.
3. Validation commands and results.
4. Documentation path.
5. Receipt path.
6. Caveats, blockers, or validation gaps.
