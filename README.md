# Spec Kit Phase Orchestrator

Run Spec Kit `tasks.md` phase-by-phase through isolated regression-baseline,
test, implementation, verification, remediation, and documentation agents with
parent-owned Git.

Maintainer: `awasali14`

Repository: https://github.com/awasali14/spec-kit-phase-orchestrator

## Why This Exists

Large Spec Kit implementation runs can overload a single agent conversation.
The agent may carry too much context from previous phases, blur task
boundaries, or mark tasks complete without a clear validation trail.

Spec Kit Phase Orchestrator solves that by selecting one phase from an
existing `tasks.md` and running context-isolated stages against shared
repository state. Compact handoffs and explicit validation, Git, and
documentation gates preserve a reviewable execution trail.

## What It Does

1. Parses an existing Spec Kit `tasks.md`.
2. Selects `next`, `phase <number>`, an inclusive phase range, or `all` after
   the parent analyzes the complete task file.
3. Runs one phase at a time through sequential, isolated stage agents.
4. Records a read-only pre-phase regression baseline, then runs test tasks,
   implementation/setup tasks, independent verification, conditional
   remediation with fresh re-verification, and documentation.
5. Aborts with a clear message when subagents or isolated worker contexts are
   unavailable.
6. Skips empty test or implementation stages, but always verifies and
   documents the phase.
7. Marks assigned task checkboxes only after the owning stage passes its gate.
8. Records exact-path manifests, validation results, commit SHAs, and a durable
   workflow-complete documentation marker.
9. Validates every worker report against a stage-specific JSON Schema contract.
10. Commits each eligible mutating stage as its own reversible progress checkpoint.

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

Run a fixed inclusive range sequentially:

```text
/speckit.phase-orchestrator.phase phase 1 to 6 specs/002-feature/tasks.md
```

For a range beginning after Phase 1, the immediately preceding phase must have
all task checkboxes checked. It does not need orchestrator documentation when
it was completed manually.

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

By default, the parent orchestrator records HEAD and the working-tree state
before every stage and launches a fresh read-only regression-baseline worker
before phase mutations. Test commits may be intentionally RED only when
failures are caused by missing assigned implementation. The parent validates
every completed worker report against the supplied stage-specific report form,
then commits each eligible implementation or remediation manifest immediately.
Fresh verification still runs after implementation and after every remediation
commit.
A strictly proven pre-existing, unrelated, unchanged regression may be
recorded as a deferred finding without hiding it from phase documentation.

To run every stage and gate while leaving all reviewed changes unstaged and
uncommitted, add `--no-commit` or clearly say not to commit:

```text
/speckit.phase-orchestrator.phase phase 3 specs/002-feature/tasks.md --no-commit
```

The orchestrator never pushes. Pushes remain user-owned.

## Supported Agents

The extension is designed for Spec Kit's agent integration system. It uses a
portable command prompt and supporting scripts rather than a Codex-only skill.

The extension has been manually tested successfully with Codex, Claude Code,
and Cursor.

The command requires subagents or isolated worker contexts. It launches one
context-isolated agent at a time for the selected phase; later agents receive
only compact structured handoffs and inspect shared repository state. If the
active coding agent cannot provide isolation, the command aborts.

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
3. Regression-baseline, test, implementation, remediation, verification, and
   documentation contracts must be satisfied before workflow completion.
4. Baseline and final verification are read-only and run in fresh contexts;
   every remediation result is re-verified and at most two cycles are permitted.
5. Phase documentation preserves aggregate stage results and the durable
   workflow-complete marker.
6. Unrelated/generated artifacts and overlap with pre-existing dirty files
   stop the workflow; unrelated pre-existing files remain untouched.
7. Workers never stage, commit, push, spawn workers, rerun the orchestrator, or
   cross phase boundaries. The parent alone owns exact-path Git operations.
8. Suspected blockers are independently classified; uncertain attribution or
   unproven downstream safety stops the workflow.
9. Schema-valid reports do not replace fresh verification; they make required
   evidence and internal consistency machine-checkable before parent policy.

## Examples

See [`docs/examples.md`](docs/examples.md) for command, parser, staged handoff,
validation, remediation, documentation, and commit examples.

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
