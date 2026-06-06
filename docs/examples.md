# Examples

This repository includes a six-phase sample tasks file:

```text
examples/sample-tasks.md
```

It contains setup, foundation, three user-story phases, and polish. Phase 1 has
two completed tasks and one incomplete task, so `next` selects Phase 1.

```markdown
# Tasks: Example Application Document Workspace

**Input**: Design documents from `/specs/002-application-document-workspace/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Organization**: Tasks are grouped by phase for incremental implementation.

## Phase 1: Setup

**Purpose**: Prepare shared project structure and test utilities.

- [X] T001 Create application documents folder in `src/features/application-documents/`
- [X] T002 [P] Add test fixtures in `tests/fixtures/applicationDocuments.js`
- [ ] T003 Add route constants in `src/routes/applicationDocumentRoutes.js`

## Phase 2: Foundational

**Purpose**: Add shared service contracts and state primitives.

- [ ] T004 Create document package service interface in `src/services/applicationDocumentService.js`
- [ ] T005 [P] Add package status constants in `src/constants/applicationDocumentStatus.js`
- [ ] T006 Add shared error handling utility in `src/utils/applicationDocumentErrors.js`

## Phase 3: User Story 1 - Start Or Resume A Package (Priority: P1)

**Independent Test**: A user can open a saved scholarship and start or resume a document package.

### Tests for Phase 3

- [ ] T007 [P] [US1] Add route integration test in `tests/integration/applicationDocumentWorkspaceRoute.integration.test.jsx`
- [ ] T008 [P] [US1] Add start/resume hook test in `tests/unit/hooks/useApplicationDocumentEntry.test.js`

### Implementation for Phase 3

- [ ] T009 [US1] Add workspace entry hook in `src/hooks/applicationDocuments/useApplicationDocumentEntry.js`
- [ ] T010 [US1] Add protected workspace route in `src/App.jsx`
- [ ] T011 [US1] Add saved scholarship apply button in `src/pages/SavedScholarshipApplyPage.jsx`

## Phase 4: User Story 2 - Edit Document Answers (Priority: P2)

**Independent Test**: A user can edit answers, save progress, and return later.

### Tests for Phase 4

- [ ] T012 [P] [US2] Add answer editor tests in `tests/unit/components/ApplicationDocumentAnswerEditor.test.jsx`
- [ ] T013 [P] [US2] Add autosave tests in `tests/unit/hooks/useApplicationDocumentAutosave.test.js`

### Implementation for Phase 4

- [ ] T014 [US2] Add answer editor component in `src/components/applicationDocuments/ApplicationDocumentAnswerEditor.jsx`
- [ ] T015 [US2] Add autosave hook in `src/hooks/applicationDocuments/useApplicationDocumentAutosave.js`
- [ ] T016 [US2] Add draft persistence service methods in `src/services/applicationDocumentService.js`

## Phase 5: User Story 3 - Review And Export Package (Priority: P3)

**Independent Test**: A user can review completed documents and export a package.

### Tests for Phase 5

- [ ] T017 [P] [US3] Add review page tests in `tests/unit/pages/ApplicationDocumentReviewPage.test.jsx`
- [ ] T018 [P] [US3] Add export service tests in `tests/unit/services/applicationDocumentExportService.test.js`

### Implementation for Phase 5

- [ ] T019 [US3] Add review page in `src/pages/ApplicationDocumentReviewPage.jsx`
- [ ] T020 [US3] Add export service in `src/services/applicationDocumentExportService.js`
- [ ] T021 [US3] Add export action in `src/components/applicationDocuments/ApplicationDocumentExportButton.jsx`

## Phase 6: Polish And Cross-Cutting Concerns

**Purpose**: Improve quality, accessibility, documentation, and final validation.

- [ ] T022 [P] Add accessibility coverage for workspace controls in `tests/unit/accessibility/applicationDocumentWorkspace.a11y.test.jsx`
- [ ] T023 Update user-facing documentation in `Documentation/application-documents.md`
- [ ] T024 Run focused regression tests for all application document files
- [ ] T025 Remove temporary debug output and unused imports across application document files
```

## Commands

```text
/speckit.phase-orchestrator.phase next examples/sample-tasks.md
/speckit.phase-orchestrator.phase phase 3 examples/sample-tasks.md
/speckit.phase-orchestrator.phase all examples/sample-tasks.md
/speckit.phase-orchestrator.phase phase 3 examples/sample-tasks.md --no-commit
```

## Parser Output

Direct parser command:

```bash
python3 scripts/phase_tasks.py examples/sample-tasks.md --phase 3 --json
```

Relevant output shape:

```json
{
  "tasks_path": "examples/sample-tasks.md",
  "mode": "phase",
  "requested_phase": 3,
  "feature_slug": "example-application-document-workspace",
  "phase_count": 6,
  "selected_phase": {
    "number": 3,
    "title": "User Story 1 - Start Or Resume A Package (Priority: P1)",
    "documentation_path": "Documentation/example-application-document-workspace/phase-3-user-story-1-start-or-resume-a-package-priority-p1-execution.md",
    "receipt_path": ".specify/phase-orchestrator/receipts/example-application-document-workspace/phase-3-user-story-1-start-or-resume-a-package-priority-p1-receipt.json",
    "complete": false,
    "incomplete_task_ids": ["T007", "T008", "T009", "T010", "T011"],
    "test_tasks": [
      {
        "id": "T007",
        "text": "[P] [US1] Add route integration test in `tests/integration/applicationDocumentWorkspaceRoute.integration.test.jsx`"
      }
    ],
    "tests_first_tasks": [
      {
        "id": "T007",
        "text": "[P] [US1] Add route integration test in `tests/integration/applicationDocumentWorkspaceRoute.integration.test.jsx`"
      }
    ],
    "implementation_tasks": [
      {
        "id": "T009",
        "text": "[US1] Add workspace entry hook in `src/hooks/applicationDocuments/useApplicationDocumentEntry.js`"
      }
    ]
  }
}
```

Use `--docs-dir` when a project or user supplies a custom documentation
directory:

```bash
python3 scripts/phase_tasks.py examples/sample-tasks.md --phase 3 --docs-dir Documentation/custom-feature --json
```

That changes only the generated Markdown documentation directory. Receipt
contracts stay under `.specify/phase-orchestrator/receipts/{feature-slug}/`
unless the parent handoff uses an explicit user-provided receipt contract path.

## Five-Phase Handoff Boundary

Use the source-controlled five-phase fixture when checking handoff boundaries:

```bash
python3 scripts/phase_tasks.py examples/five-phase-tasks.md --phase 4 --json
```

The worker handoff for Phase 4 should include only Phase 4 task IDs and task
text. It should not include parent model or effort settings, worker-spawn
instructions, all-mode queue instructions, post-phase staging, or tasks from
Phases 1, 2, 3, or 5 as executable worker instructions.

## Sample Receipt Contract

See `examples/sample-phase-receipt.json` for a completed Phase 3 receipt
contract. The receipt uses the schema-valid snake_case shape:

```json
{
  "schema_version": "1.0",
  "status": "completed",
  "phase": {
    "number": 3,
    "title": "User Story 1 - Start Or Resume A Package (Priority: P1)"
  },
  "completed_task_ids": ["T007", "T008"],
  "changed_files": ["examples/sample-tasks.md"],
  "validation": [
    {
      "command": "npm test -- useApplicationDocumentEntry",
      "status": "passed",
      "notes": "Focused hook coverage passed."
    }
  ],
  "documentation_path": "Documentation/example/phase-3-execution.md",
  "receipt_path": ".specify/phase-orchestrator/receipts/example/phase-3-receipt.json",
  "issues": [],
  "commit": null
}
```

The receipt contract records:

1. Phase status.
2. Completed task IDs.
3. Changed files.
4. Validation commands and results.
5. Documentation path.
6. Receipt contract path.
7. Issues or blockers.
8. Optional commit information.

Use `completed_task_ids` and `changed_files`, not `completedTaskIds` or
`changedFiles`.
