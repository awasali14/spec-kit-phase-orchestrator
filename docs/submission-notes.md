# Spec Kit Extension Submission Notes

Pre-release draft. Use these values for the Spec Kit Extension Submission issue
after the release tag exists and the release archive install flow is verified.

## Extension Metadata

Extension ID: `phase-orchestrator`

Extension Name: `Phase Orchestrator`

Version: `1.0.0`

Description: `Orchestrate Spec Kit tasks.md execution phase-by-phase with isolated worker handoffs, focused validation, documentation, and optional commits.`

Author: `awasali14`

Repository: `https://github.com/awasali14/spec-kit-phase-orchestrator`

Download URL: `https://github.com/awasali14/spec-kit-phase-orchestrator/archive/refs/tags/v1.0.0.zip`

Download URL status: pending release creation and release-archive verification.

License: `MIT`

Required Spec Kit Version: `>=0.8.7`

Required Python Version: `>=3.10`

Commands Provided: `speckit.phase-orchestrator.phase`

Tags: `workflow, implementation, orchestration, tasks`

## Key Features

1. Selects the next incomplete phase from an existing Spec Kit `tasks.md`.
2. Supports explicit phase selection and all-remaining sequential mode.
3. Keeps `/speckit.implement` untouched as the official implementation command.
4. Spawns one isolated subagent per selected phase for clean worker handoffs.
5. Aborts with a clear message when subagents or isolated worker contexts are
   unavailable.
6. Produces phase documentation and validation summaries.
7. Creates parent-owned post-phase commits by default without staging
   unrelated files, with `--no-commit` opt-out support.

## Manual Testing Record

Completed manual testing:

1. Parser CLI smoke tests completed for:
   `python3 scripts/phase_tasks.py examples/sample-tasks.md --mode next --json`,
   `python3 scripts/phase_tasks.py examples/sample-tasks.md --phase 3 --json`,
   and
   `python3 scripts/phase_tasks.py examples/sample-tasks.md --mode all --json`.
2. Development install completed with
   `specify extension add --dev /path/to/spec-kit-phase-orchestrator`.
3. Codex wrapper was present after install.
4. Adding Claude Code later reproduced the missing-wrapper issue.
5. `specify extension remove phase-orchestrator` plus re-adding from the
   original source fixed Claude registration.
6. `specify integration use claude` succeeded.
7. `specify extension update phase-orchestrator` reported that the extension
   catalog entry was not found.

Release-archive install testing is still pending because the public tag-backed
archive does not exist yet.

## Prerelease Guardrails

1. Before publishing a tag-based install command, verify the tag exists remotely with `git ls-remote --tags origin <tag>`.
2. Before release, verify every documented install URL returns `HTTP 200`, for example with `curl -I -L <install-url>`.
3. If the extension is not published in a Spec Kit extension catalog, do not position `specify extension update phase-orchestrator` as the primary refresh or re-registration path.
4. Catalog publication can be added later, but it should not block documentation or release-hygiene fixes.
5. When a real release tag is published, update the README and submission notes together so the documented install command matches the tagged archive.

## AI Disclosure

I used AI assistance to help draft documentation and structure the extension,
then manually reviewed and tested the repository before submission.
