# Mermaid Style Guidance

Use one styled Phase Flow Mermaid diagram in every phase execution document
unless the user explicitly asks to omit diagrams. Prefer one small diagram over
multiple detailed diagrams.

## Defaults

- Group major branches with subgraphs so Mermaid can position related nodes
  with more separation.
- Use `flowchart LR` for broad architecture and `flowchart TD` for short
  validation paths.
- Keep node labels short.
- Avoid product-specific names unless they are part of the selected tasks.
- Show the phase boundary clearly.
- Do not diagram unrelated phases.
- Copy the dark/emerald `classDef` and `linkStyle` lines below exactly unless
  the project already has diagram styling.

## Colours

- Outer subgraphs: `#0A0A0A` background, `#424242` border
- Inner subgraphs: `#1E1E1E` background, `#424242` border
- Nodes/files/components: `#161616` fill, `#424242` border, `#ffffff` text
- Arrows: `#00E589`
- Edge labels: `#0A0A0A` background

## Example

```mermaid
flowchart LR
  classDef outer fill:#0A0A0A,stroke:#424242,color:#ffffff
  classDef inner fill:#1E1E1E,stroke:#424242,color:#ffffff
  classDef node fill:#161616,stroke:#424242,color:#ffffff
  linkStyle default stroke:#00E589,color:#00E589

  subgraph Phase["Selected Phase"]
    direction TB
    A["Tests or setup"]:::node
    B["Implementation"]:::node
  end

  subgraph Gate["Validation Gate"]
    direction TB
    C["Focused validation"]:::node
    D["Execution doc"]:::node
  end

  A --> B --> C --> D
  class Phase,Gate outer
```
