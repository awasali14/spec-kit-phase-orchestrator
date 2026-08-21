# Examples

This page is the complete examples reference for Spec Kit Phase Orchestrator.
The installed extension does not require the repository's development fixtures.

## Choose A Mode

- Use `next` when you want the first workflow-incomplete phase. It also resumes
  phases whose tasks are checked but whose final verified documentation is
  incomplete.
- Use `phase <number>` when you intentionally want one specific phase, even if
  an earlier phase is incomplete.
- Use `all` when all remaining phases are well-defined and may run sequentially.
  Each phase must pass all staged gates before the next phase starts.

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
    "task_complete": false,
    "documentation_complete": false,
    "workflow_complete": false,
    "next_stage": "test",
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
document directory. An explicit Markdown path overrides that default. In
`all` mode, `selected_phases` is workflow-aware, but the parent still completes
every gate for one phase before starting the next.

## Representative Stage Handoffs

The parent records the Git baseline and launches a fresh read-only
regression-baseline worker before phase mutations. It records exact suitable regression
commands, a compact environment fingerprint, failing test identities, and
material failure signatures, then converts the parser result into compact,
role-specific handoffs. A shortened test handoff looks like this:

```text
Stage: test
Selected phase: Phase 3
Assigned task IDs: T005, T006
Relevant paths: tasks.md and the two assigned test paths
Prior SHA: <sha>

Implement only the assigned test tasks. Mark their checkboxes only after the
test gate. An intentional RED is eligible only when missing assigned
implementation explains the failure. Correct failures within the assigned test
scope; if an ineligible failure remains, restore assigned checkboxes and report
the gate as failed to the parent.
```

After the parent reviews and, by default, commits eligible test changes, the
implementation handoff contains `T007`, `T008`, relevant paths, the prior SHA,
test manifest, baseline evidence, validation summary, and expected RED. It
instructs the agent to inspect committed tests directly and run the complete
focused phase-test gate. Its manifest remains uncommitted; an unresolved result
continues to the verifier with typed suspected findings.

The verifier receives only the phase scope, manifests, SHAs, baseline evidence,
deferred findings, and validation summaries. It remains read-only, reruns exact
baseline commands, and returns typed focused, independent-phase, regression,
attribution, and disposition evidence. A phase-introduced regression is first
remediated within scope. A pre-existing failure is deferred only when it is
unchanged, unrelated, and safe for remaining phases. Uncertainty blocks.

Every remediation result, including unresolved focused validation, receives a
fresh verifier. After two non-phase-safe cycles, the workflow stops with all
implementation/remediation changes uncommitted. After a phase-safe verdict, the
parent creates one intent-based commit for their exact accumulated path union.

Only the documentation handoff contains the execution-document and Mermaid
instructions. Every worker is forbidden to stage, commit, push, spawn workers,
run the orchestrator, or cross phase boundaries. The official
`/speckit.implement` or `$speckit-implement` workflow remains unchanged and is
routed only where relevant.

## Expected Results

After the staged workflow completes Phase 3 successfully:

1. `T005`–`T008` are checked in `tasks.md` only after focused validation.
2. Focused tests are reported with their exact commands and results, for
   example `npm test -- applicationDocumentWorkspaceRoute` — passed.
3. A fresh read-only verifier passes focused and independent-phase validation
   and either passes regression validation or strictly proves and records a
   deferrable pre-existing regression.
4. The resolved Markdown execution document records aggregate stage reports,
   exact-path manifests, SHAs, validation, caveats, remediation history, the
   required styled Mermaid flow, and
   `<!-- phase-orchestrator:workflow-complete v2 -->`.
5. By default, the parent creates only eligible exact-path commits: test
   coverage, one verified intent-based implementation/remediation commit, and
   final documentation.
6. With `--no-commit`, the same stages and gates run with per-stage manifests,
   but accumulated reviewed changes remain unstaged and uncommitted.

Empty test or implementation stages are skipped; baseline verification, fresh
final verification, and documentation are never skipped. Unsafe RED failures,
uncertain regression attribution, unproven downstream safety, required scope
crossing, a third remediation need, missing final documentation,
generated/unrelated artifacts, or overlap with a pre-existing dirty file stop
the workflow. In `all` mode, no later phase starts after that failure.

For a phase containing only test-authoring tasks, correctly executing failures
attributable solely to implementation outside that phase are accepted as
expected RED. Verification records the expected RED, passes the phase contract,
and does not ask remediation to implement work from another phase.
