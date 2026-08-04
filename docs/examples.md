# Examples

This page is the complete examples reference for Spec Kit Phase Orchestrator.
The installed extension does not require the repository's development fixtures.

## Choose A Mode

- Use `next` when you want the first phase with unchecked tasks.
- Use `phase <number>` when you intentionally want one specific phase, even if
  an earlier phase is incomplete.
- Use `all` when all remaining phases are well-defined and may run sequentially.
  Each phase still gets its own worker, validation gate, document, and commit.

Prefer `next` or an explicit phase when requirements are unclear, the working
tree needs review, or a phase may require a decision. In `all` mode, any blocker,
failed validation, missing document, or unsafe Git state stops the queue.

## Invoke The Command

Slash-command integrations such as Claude Code and Cursor use:

```text
/speckit.phase-orchestrator.phase next specs/002-application-document-workspace/tasks.md
/speckit.phase-orchestrator.phase phase 3 specs/002-application-document-workspace/tasks.md
/speckit.phase-orchestrator.phase all specs/002-application-document-workspace/tasks.md
```

Codex uses the installed skill name:

```text
$speckit-phase-orchestrator-phase next specs/002-application-document-workspace/tasks.md
$speckit-phase-orchestrator-phase phase 3 specs/002-application-document-workspace/tasks.md
$speckit-phase-orchestrator-phase all specs/002-application-document-workspace/tasks.md
```

Write generated execution documents to a custom directory with `--docs-dir`:

```text
/speckit.phase-orchestrator.phase phase 3 specs/002-application-document-workspace/tasks.md --docs-dir Documentation/custom-feature
```

Leave the validated changes unstaged and uncommitted with `--no-commit`:

```text
$speckit-phase-orchestrator-phase phase 3 specs/002-application-document-workspace/tasks.md --no-commit
```

An explicit Markdown path in natural language also works and takes precedence:

```text
/speckit.phase-orchestrator.phase phase 3 specs/002-application-document-workspace/tasks.md and write the execution document to Documentation/reviews/workspace-entry.md
```

## Compact `tasks.md` Sample

Save this as `specs/002-application-document-workspace/tasks.md` to reproduce
the examples without any other sample files:

```markdown
# Tasks: Application Document Workspace

## Phase 1: Setup

**Purpose**: Prepare shared project structure.

- [X] T001 Create the feature folder in `src/features/application-documents/`
- [ ] T002 Add route constants in `src/routes/applicationDocumentRoutes.js`

## Phase 2: Foundational

**Purpose**: Add shared service contracts.

- [ ] T003 Create the service interface in `src/services/applicationDocumentService.js`
- [ ] T004 Add shared error handling in `src/utils/applicationDocumentErrors.js`

## Phase 3: User Story 1 - Start Or Resume A Package (Priority: P1)

**Independent Test**: A user can start or resume a saved document package.

### Tests for Phase 3

- [ ] T005 [P] [US1] Add the route integration test in `tests/integration/applicationDocumentWorkspaceRoute.test.jsx`
- [ ] T006 [P] [US1] Add the entry hook test in `tests/unit/useApplicationDocumentEntry.test.js`

### Implementation for Phase 3

- [ ] T007 [US1] Add the entry hook in `src/hooks/useApplicationDocumentEntry.js`
- [ ] T008 [US1] Add the protected route in `src/App.jsx`
```

With this state, `next` selects Phase 1, explicit `phase 3` selects Phase 3,
and `all` queues Phases 1–3 in order.

## Representative Parser Output

The installed command runs the parser from the extension payload. From a
project root, the equivalent explicit Phase 3 check is:

```bash
python3 .specify/extensions/phase-orchestrator/scripts/phase_tasks.py \
  specs/002-application-document-workspace/tasks.md --phase 3 --json
```

Representative fields are:

```json
{
  "tasks_path": "specs/002-application-document-workspace/tasks.md",
  "feature_slug": "application-document-workspace",
  "mode": "phase",
  "requested_phase": 3,
  "phase_count": 3,
  "selected_phase": {
    "number": 3,
    "title": "User Story 1 - Start Or Resume A Package (Priority: P1)",
    "documentation_path": "Documentation/application-document-workspace/phase-3-user-story-1-start-or-resume-a-package-priority-p1-execution.md",
    "complete": false,
    "incomplete_task_ids": ["T005", "T006", "T007", "T008"],
    "counts": {
      "total": 4,
      "completed": 0,
      "incomplete": 4,
      "test_tasks": 2,
      "implementation_tasks": 2
    },
    "tests_first_tasks": [
      {"id": "T005", "section": "Tests for Phase 3"},
      {"id": "T006", "section": "Tests for Phase 3"}
    ],
    "implementation_tasks": [
      {"id": "T007", "section": "Implementation for Phase 3"},
      {"id": "T008", "section": "Implementation for Phase 3"}
    ]
  }
}
```

Adding `--docs-dir Documentation/custom-feature` changes only the generated
document directory. In `all` mode, `selected_phases` contains the remaining
phase queue, but the parent still hands off only one selected phase at a time.

## Representative Worker Handoff

The parent converts the parser result into a sanitized, single-phase prompt.
A shortened Phase 3 handoff looks like this:

```text
You are a sequential Spec Kit phase worker for this repository.

Tasks file: specs/002-application-document-workspace/tasks.md
Mode: phase
Selected phase: Phase 3: User Story 1 - Start Or Resume A Package (Priority: P1)
Independent test: A user can start or resume a saved document package.

Assigned incomplete task IDs:
T005, T006, T007, T008

Tests-first tasks:
- T005 Add the route integration test.
- T006 Add the entry hook test.

Implementation/setup tasks:
- T007 Add the entry hook.
- T008 Add the protected route.

Official implementation workflow/skill:
Use /speckit.implement or $speckit-implement for implementation discipline and
task tracking. Keep its use scoped to Phase 3 only.

Documentation:
- Write the Markdown phase execution document to:
  Documentation/application-document-workspace/phase-3-user-story-1-start-or-resume-a-package-priority-p1-execution.md
- Use the installed phase document and Mermaid style references.

Do not run the phase orchestrator, spawn workers, work on another phase, stage,
commit, or push. Stop after Phase 3 and report validation and changed files.
```

The actual handoff retains full task text, validation expectations, relevant
skills, and applicable tool notes. It excludes parent model settings, the
`all`-mode queue, worker-spawn instructions, and post-phase Git actions.

## Expected Results

After the worker completes Phase 3 successfully:

1. `T005`–`T008` are checked in `tasks.md` only after focused validation.
2. Focused tests are reported with their exact commands and results, for
   example `npm test -- applicationDocumentWorkspaceRoute` — passed.
3. The resolved Markdown execution document exists and records task IDs,
   changed files, validation, caveats, and the required styled Mermaid flow.
4. The parent re-runs the parser, reviews `git status --short` and the diff,
   and confirms the phase and documentation gates.
5. By default, the parent stages only Phase 3 files and creates one Conventional
   Commit such as `feat(workspace): complete phase 3 entry flow`.
6. With `--no-commit`, the same gates run, but files remain unstaged and no
   commit is created. The orchestrator never pushes in either case.

If focused validation fails, the documentation is missing, or unrelated work
is mixed into a required file, the parent reports the issue and stops. In
`all` mode, no later phase starts after that failure.
