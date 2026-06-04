# Phase Execution Document Template

Use this structure for the Markdown document written at the selected phase's
`documentation_path`.

````markdown
# Phase [PHASE_NUMBER]: [PHASE_TITLE]

## Scope

- Tasks file: `[TASKS_PATH]`
- Completed task IDs: [COMPLETED_TASK_IDS]
- Documentation path: `[DOCUMENTATION_PATH]`
- Receipt path: `[RECEIPT_PATH]`

## Work Completed

Summarize the implementation, setup, and test-first work completed in this
phase. Keep the summary tied to task IDs.

## Changed Files

- `[PATH]` - [brief reason]

## Validation

| Command | Status | Notes |
| --- | --- | --- |
| `[COMMAND]` | passed/failed/not run | [notes] |

## Phase Flow

Use one high-level Mermaid diagram when it clarifies the phase. Keep labels
short and avoid project-specific styling.

```mermaid
flowchart LR
  classDef outer fill:#0A0A0A,stroke:#424242,color:#ffffff
  classDef inner fill:#1E1E1E,stroke:#424242,color:#ffffff
  classDef node fill:#000000,stroke:#424242,color:#ffffff
  linkStyle default stroke:#00E589,color:#00E589

  subgraph Phase["Selected phase"]
    direction TB
    A["Tests or setup"]:::node
    B["Implementation"]:::node
  end

  subgraph Gate["Validation gate"]
    direction TB
    C["Focused validation"]:::node
    D["Receipt and docs"]:::node
  end

  A --> B --> C --> D
  class Phase,Gate outer
```

## Issues And Caveats

Record blockers, validation gaps, risky assumptions, or follow-up work. Write
`None` only when there are no caveats.
````

## Notes

Use generic paths and wording unless the user supplied project-specific
documentation requirements. If the user supplied an exact documentation or
receipt path, preserve it.
