# Spec Kit Phase Orchestrator

Run Spec Kit `tasks.md` one phase at a time with clean agent context.

Maintainer: `awasali14`

Repository: https://github.com/awasali14/spec-kit-phase-orchestrator

## Why This Exists

Large Spec Kit implementation runs can overload a single agent conversation.
The agent may carry too much context from previous phases, blur task
boundaries, or mark tasks complete without a clear validation trail.

Spec Kit Phase Orchestrator solves that by selecting one phase from an
existing `tasks.md`, creating a compact phase handoff, running only that
phase, writing a receipt, and stopping at a validation gate.

## What It Does

1. Parses an existing Spec Kit `tasks.md`.
2. Selects `next`, `phase <number>`, or `all`.
3. Runs one phase at a time.
4. Uses a clean worker context when the active coding agent supports it.
5. Falls back to local execution when subagents are not available.
6. Marks completed task checkboxes.
7. Runs focused validation.
8. Writes phase documentation and a phase receipt.
9. Supports optional post-phase commits.

## What It Does Not Do

1. It does not replace `/speckit.implement`.
2. It does not modify core Spec Kit.
3. It does not require Codex.
4. It does not require Claude Code.
5. It does not run destructive git operations by default.

## Installation

Development install:

```bash
specify extension add --dev /path/to/spec-kit-phase-orchestrator
```

Release install:

```bash
specify extension add phase-orchestrator --from https://github.com/awasali14/spec-kit-phase-orchestrator/archive/refs/tags/v1.0.0.zip
```

## Usage

Run the next incomplete phase:

```text
/speckit.phase-orchestrator.phase next specs/002-feature/tasks.md
```

Run a specific phase:

```text
/speckit.phase-orchestrator.phase phase 3 specs/002-feature/tasks.md
```

Run all remaining phases sequentially:

```text
/speckit.phase-orchestrator.phase all specs/002-feature/tasks.md
```

## Supported Agents

The extension is designed for Spec Kit's agent integration system. It uses a
portable command prompt and supporting scripts rather than a Codex-only skill.

If the current coding agent supports subagents or isolated worker contexts,
the command uses exactly one worker for the selected phase. If the agent does
not support subagents, it executes the same phase-scoped workflow locally.

## Safety

1. Official `/speckit.implement` remains untouched.
2. Only the selected phase should be implemented.
3. Validation must run before a phase is considered complete.
4. Phase documentation and receipt files preserve the implementation trail.
5. Unrelated git changes should not be staged or committed.
6. Mixed unrelated changes should stop the workflow for user guidance.

## Examples

See:

1. `examples/sample-tasks.md`
2. `examples/sample-phase-handoff.json`
3. `examples/sample-phase-receipt.json`
4. `docs/examples.md`

## Testing

Run parser tests:

```bash
python3 -m unittest discover -s tests
```

Test extension installation:

```bash
specify extension add --dev /path/to/spec-kit-phase-orchestrator
specify extension list
```

## License

MIT
