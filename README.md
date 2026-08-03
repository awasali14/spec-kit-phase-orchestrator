# Spec Kit Phase Orchestrator

Run Spec Kit `tasks.md` phase-by-phase by spawning isolated subagents for
clean handoffs, validation, docs, and commits.

Maintainer: `awasali14`

Repository: https://github.com/awasali14/spec-kit-phase-orchestrator

## Why This Exists

Large Spec Kit implementation runs can overload a single agent conversation.
The agent may carry too much context from previous phases, blur task
boundaries, or mark tasks complete without a clear validation trail.

Spec Kit Phase Orchestrator solves that by selecting one phase from an
existing `tasks.md`, creating a compact phase handoff, running only that
phase, writing a Markdown execution document, and stopping at a validation
gate.

## What It Does

1. Parses an existing Spec Kit `tasks.md`.
2. Selects `next`, `phase <number>`, or `all`.
3. Runs one phase at a time.
4. Spawns an isolated subagent for each phase.
5. Aborts with a clear message when subagents or isolated worker contexts are
   unavailable.
6. Marks completed task checkboxes.
7. Runs focused validation.
8. Writes phase documentation.
9. Reviews the phase diff and creates one parent-owned post-phase commit by
   default.

## What It Does Not Do

1. It does not replace `/speckit.implement`.
2. It does not modify core Spec Kit.
3. It does not require Codex.
4. It does not require Claude Code.
5. It does not run destructive git operations by default.
6. It does not push to remotes.

## Installation

Development install:

```bash
specify extension add --dev /path/to/spec-kit-phase-orchestrator
```

Pre-release note: the published tag install command will be documented here
after the release tag exists and the release archive install flow is verified.

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

Use a custom documentation directory:

```text
/speckit.phase-orchestrator.phase phase 3 specs/002-feature/tasks.md --docs-dir Documentation/custom-feature
```

Without a custom location, generated Markdown phase documents go under
`Documentation/{feature-slug}/`.

By default, the parent orchestrator reviews the completed phase, stages only
selected-phase files, and creates one Conventional Commit after validation and
documentation checks pass. To leave changes unstaged and uncommitted, add
`--no-commit` or clearly say not to commit:

```text
/speckit.phase-orchestrator.phase phase 3 specs/002-feature/tasks.md --no-commit
```

The orchestrator never pushes. Pushes remain user-owned.

## Supported Agents

The extension is designed for Spec Kit's agent integration system. It uses a
portable command prompt and supporting scripts rather than a Codex-only skill.

The extension has been manually tested successfully with Codex, Claude Code,
and Cursor.

The command requires subagents or isolated worker contexts and uses exactly one
worker for the selected phase. If the active coding agent does not support
isolated workers, the command aborts and informs the user.

Spec Kit installs agent-facing command wrappers into the relevant integration
directory, such as `.agents/skills` for Codex, `.cursor/skills` for Cursor,
and `.claude/skills` for Claude Code. The extension's supporting files remain
under `.specify/extensions/phase-orchestrator/`.

If you install another Spec Kit integration after Phase Orchestrator is already
installed, re-register the extension for that integration using the
troubleshooting steps below. Seeing only `SKILL.md` in the agent skills
directory is normal.

## Troubleshooting

### Extension installed but not visible in Claude Code, Cursor, or another integration

If you add another Spec Kit integration after installing Phase Orchestrator,
the extension may need to be re-registered for that integration.

If you originally installed the extension with `--dev`, re-register it from
the same local path:

```bash
specify extension add --dev /path/to/spec-kit-phase-orchestrator
```

If you originally installed the extension from a published release URL,
re-register it with that same release archive source:

```bash
specify extension add phase-orchestrator --from <published-release-url>
```

If your Spec Kit CLI supports reinstall with `--force`, you can add it to
either command above.

If your Spec Kit CLI does not support `--force` for `specify extension add`,
remove the extension and re-add it from the same original source:

```bash
specify extension remove phase-orchestrator
specify extension add --dev /path/to/spec-kit-phase-orchestrator
```

If the original source was a published release URL, the re-add command becomes:

```bash
specify extension add phase-orchestrator --from <published-release-url>
```

Restart the coding agent after re-registering the extension.

`specify extension update phase-orchestrator` only helps when the extension is
available from a configured Spec Kit extension catalog.

Note: In Claude Code, seeing `SKILL.md` in `.claude/skills/` is normal.
Supporting scripts and reference templates remain under
`.specify/extensions/phase-orchestrator/`.

## Safety

1. Official `/speckit.implement` remains untouched.
2. Only the selected phase should be implemented.
3. Validation must run before a phase is considered complete.
4. Phase documentation preserves the implementation trail.
5. Unrelated git changes should not be staged or committed.
6. Mixed unrelated changes should stop the workflow for user guidance.
7. Workers should never stage, commit, or push; post-phase commits are a parent
   responsibility.

## Examples

See:

1. `examples/sample-tasks.md`
2. `examples/sample-phase-handoff.json`
3. `docs/examples.md`

## Testing

Manual extension testing has been completed successfully on Codex, Claude
Code, and Cursor.

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
