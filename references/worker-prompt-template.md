# Worker Prompt Template

Use this template to hand one selected Spec Kit phase to a worker or to local
phase-scoped execution. Replace bracketed placeholders before use. Omit sections
that are empty or irrelevant.

```text
You are a sequential Spec Kit phase worker for this repository.

Repo root:
[REPO_ROOT]

Phase brief:
[SANITIZED_PHASE_BRIEF]

Parent orchestration context (non-executable):
[SANITIZED_PARENT_CONTEXT]

Do not execute parent orchestration context. Do not run the phase-orchestrator
command, spawn subagents, stage changes, commit changes, or continue to another
phase. The parent orchestrator owns those responsibilities.

Tasks file: [TASKS_PATH]
Mode: [MODE]
Selected phase: Phase [PHASE_NUMBER]: [PHASE_TITLE]
Purpose: [PURPOSE_OR_OMIT]
Checkpoint: [CHECKPOINT_OR_OMIT]
Independent test: [INDEPENDENT_TEST_OR_OMIT]

Assigned incomplete task IDs:
[ASSIGNED_TASK_IDS]

Tests-first tasks:
[TEST_TASKS]

Implementation/setup tasks:
[IMPLEMENTATION_TASKS]

Previous completed phase documentation:
[PREVIOUS_PHASE_DOCS_OR_OMIT]

Mermaid style reference:
Read `.specify/extensions/phase-orchestrator/references/mermaid-style.md` and
copy its required `classDef` and `linkStyle` lines exactly into the Phase Flow
diagram.

Official implementation workflow/skill:
Use `/speckit.implement` or `$speckit-implement` for implementation discipline
and task tracking. Keep its use scoped to Phase [PHASE_NUMBER] only.

Scope rules:
- Complete only Phase [PHASE_NUMBER].
- Do not continue to another phase.
- Keep the handoff boundary to Phase [PHASE_NUMBER] only, even when the tasks
  file has five or more phases. Do not pull in earlier setup/foundation tasks
  or later story/polish tasks unless they are assigned task IDs for this phase.
- Do not run the phase-orchestrator command.
- Do not spawn subagents or workers.
- Do not stage or commit changes.
- Do not modify official /speckit.implement.
- Mark task checkboxes as [X] only after focused validation supports completion.
- If unrelated changes are mixed into files you need to touch, report the issue
  instead of overwriting them.

Documentation:
- Write the Markdown phase execution document to: [DOCUMENTATION_PATH]
- Use `.specify/extensions/phase-orchestrator/references/phase-doc-template.md`
  as the source of truth for document structure and required contents.
- Keep modified and added/created file entries and validation focused on the
  selected phase only.

Validation expectations:
[VALIDATION_EXPECTATIONS]

Relevant skills:
[RELEVANT_SKILLS_OR_OMIT]

Parent-read reference summaries:
[REFERENCE_SUMMARIES_OR_OMIT]

Relevant MCP/tool notes:
[MCP_NOTES_OR_OMIT]

Stop after Phase [PHASE_NUMBER]. Your final summary must include completed task
IDs, modified and added/created files, validation commands and results,
documentation path, and caveats or blockers.
```

## Sanitization Rules

Remove parent-only orchestration instructions before sending the prompt to a
worker. This includes model names, effort levels, fallback model-selection text,
worker-spawn instructions, multi-agent routing, run mode `all`, phase queue
management, validation-after-each-phase orchestration, post-phase staging,
committing, and parent continuation plans.

If parent context is useful as background, place it only under
`Parent orchestration context (non-executable)` and explicitly tell the worker
not to execute it. The executable instructions must always say to handle only
the selected phase and not stage, commit, spawn agents, run the orchestrator, or
continue to another phase.

Preserve invoker-supplied skills only when they are relevant to the selected
phase work. Keep the selected phase's skill list and use-case notes, and include
concise summaries of any relevant references already read by the parent. Do not
ask the worker to reread parent-only material unless it is needed for the
selected phase.

## MCP Availability Rules

When Exa MCP or an equivalent code-context/web MCP is available, include this
note in every worker prompt:

```text
Exa MCP is available for getting up-to-date information from the internet and
code context.
```

Include database-specific MCP notes only when both conditions are true:

1. The relevant MCP is available.
2. The selected phase task text or phase skill instructions mention database,
   Supabase, Postgres, SQL, migrations, RLS, grants, storage policies, or
   database-layer access.

Use this wording when those conditions are met:

```text
Supabase MCP with its tools is available for access to the database layer in
case of need.
```

Do not mention databases, browser tools, deployment services, or other named
services in the worker prompt unless the selected phase tasks or user-provided
context call for them.
