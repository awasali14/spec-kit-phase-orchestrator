# Tasks: Five Phase Boundary Fixture

**Input**: Boundary test fixture for worker handoff examples.
**Organization**: Tasks are grouped by phase for selected-phase isolation.

## Phase 1: Setup

**Purpose**: Prepare shared folders.

- [X] T001 Create fixture root in `src/boundary/`

## Phase 2: Foundation

**Purpose**: Add shared primitives.

- [X] T002 Add boundary constants in `src/boundary/constants.js`

## Phase 3: User Story 1 - Create Item

**Independent Test**: A user can create an item.

### Tests for Phase 3

- [X] T003 Add create item test in `tests/boundary/createItem.test.js`

### Implementation for Phase 3

- [X] T004 Add create item handler in `src/boundary/createItem.js`

## Phase 4: User Story 2 - Review Item

**Independent Test**: A user can review an item.

### Tests for Phase 4

- [ ] T005 Add review item test in `tests/boundary/reviewItem.test.js`

### Implementation for Phase 4

- [ ] T006 Add review item panel in `src/boundary/ReviewItemPanel.jsx`

## Phase 5: Polish

**Purpose**: Final quality pass.

- [ ] T007 Update boundary documentation in `Documentation/boundary.md`
