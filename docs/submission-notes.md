# Spec Kit Extension Submission Notes

Use these values for the Spec Kit Extension Submission issue.

## Extension Metadata

Extension ID: `phase-orchestrator`

Extension Name: `Phase Orchestrator`

Version: `1.0.0`

Description: `Run Spec Kit tasks.md phase-by-phase by spawning isolated subagents for clean handoffs, validation, docs, and commits.`

Author: `awasali14`

Repository: `https://github.com/awasali14/spec-kit-phase-orchestrator`

Download URL: `https://github.com/awasali14/spec-kit-phase-orchestrator/archive/refs/tags/v1.0.0.zip`

License: `MIT`

Required Spec Kit Version: `>=0.8.7`

Required Python Version: `>=3.10`

Commands Provided: `speckit.phase-orchestrator.phase`

Tags: `workflow, implementation, orchestration, tasks`

## Key Features

1. Selects the next incomplete phase from an existing Spec Kit `tasks.md`.
2. Supports explicit phase selection and all-remaining sequential mode.
3. Keeps `/speckit.implement` untouched as the official implementation command.
4. Uses clean worker handoffs when the active coding agent supports subagents.
5. Falls back to local execution for agents without subagent support.
6. Produces phase documentation and validation summaries.
7. Creates parent-owned post-phase commits by default without staging
   unrelated files, with `--no-commit` opt-out support.

## Testing Confirmation

1. Extension installs successfully with `specify extension add --dev /path/to/spec-kit-phase-orchestrator`.
2. Extension installs successfully from the GitHub release archive.
3. Command file is present and usable after installation.
4. Parser tests pass.
5. Tested on a realistic Spec Kit `tasks.md` with six phases.
6. Documentation is complete and accurate.

Manual install and cross-agent testing are intentionally left for the manual
testing phase.

## AI Disclosure

I used AI assistance to help draft documentation and structure the extension,
then manually reviewed and tested the repository before submission.
