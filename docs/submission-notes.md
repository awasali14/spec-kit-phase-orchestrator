# Spec Kit Extension Submission Notes

Pre-release draft. Use these values for the Spec Kit Extension Submission issue
after the release tag exists and the release archive install flow is verified.

## Extension Metadata

Extension ID: `phase-orchestrator`

Extension Name: `Phase Orchestrator`

Version: `2.0.0`

Description: `Orchestrate each Spec Kit tasks.md phase through isolated test, implementation, verification, remediation, and documentation stages with parent-owned Git gates.`

Author: `awasali14`

Repository: `https://github.com/awasali14/spec-kit-phase-orchestrator`

Planned Download URL: `https://github.com/awasali14/spec-kit-phase-orchestrator/archive/refs/tags/v2.0.0.zip`

Download URL status: pending v2.0.0 tag creation, release publication, and
release-archive verification. The URL is not yet an installation claim.

License: `MIT`

Required Spec Kit Version: `>=0.8.7`

Required Python Version: `>=3.10`

Commands Provided: `speckit.phase-orchestrator.phase`

Tags: `workflow, implementation, orchestration, tasks`

## Key Features

1. Selects the next workflow-incomplete phase, an explicit phase, or all
   remaining workflow-incomplete phases from an existing Spec Kit `tasks.md`.
2. Runs context-isolated test, implementation, verification, conditional
   remediation and re-verification, and documentation agents sequentially.
3. Keeps `/speckit.implement` untouched as the official implementation command.
4. Gives each stage a compact v2 handoff and prevents workers from owning Git,
   spawning workers, running the orchestrator, or crossing phase boundaries.
5. Uses independent read-only verification and permits at most two remediation
   and fresh re-verification cycles.
6. Produces phase documentation with aggregate stage reports and a durable
   workflow-complete marker only after final verification passes.
7. Creates parent-owned stage commits with exact-path staging and dirty-state
   protection, with `--no-commit` retaining reviewed changes unstaged.

## Verification Record

v2.0.0 pre-release verification completed on 2026-08-07:

1. All 43 unit tests passed on Python 3 with Spec Kit CLI 0.13.0. Coverage
   includes workflow completion and verification resume, empty stages,
   classification, custom documentation paths, role sanitization, read-only
   verification, documentation and Mermaid routing, the two-attempt remediation
   cap, intentional RED and green commit gates, exact staging, unrelated dirty
   state, no-change stages, `--no-commit`, and documentation completion.
2. Parser CLI smoke tests passed for `next`, explicit `phase`, and `all`.
   Completed disposable cases report `workflow_complete: true`; the exhausted
   remediation case reports `task_complete: true`,
   `documentation_complete: false`, and `next_stage: verification`.
3. The v2 handoff schema passed Draft 2020-12 schema validation, and the sample
   v2 handoff validated against it.
4. A development install into a disposable Spec Kit project registered and
   enabled Phase Orchestrator 2.0.0 for Codex. The installed payload contained
   the runtime schema, parser, command, references, public documentation,
   license, and changelog, while excluding tests, fixtures, submission and
   publication records, workspace metadata, and caches. `docs/examples.md` was
   the only installed examples artifact.
5. The generated Codex wrapper contained the concise v2 trigger description,
   the staged workflow, and the integration-rewritten runtime paths. The
   official `speckit-implement` wrapper remained available. Spec Kit reported a
   healthy Codex integration with no modified, missing, or invalid managed
   files.
6. Isolated Codex subagents forward-tested disposable repositories for the
   happy path, one-cycle remediation success, two-cycle remediation exhaustion,
   empty test and implementation stages, an unrelated dirty file, and
   `--no-commit`. The tests ran on Linux 6.6.87.2 under WSL2. No production
   project was used and no remote was pushed.
7. The `--no-commit` case kept the initial and final HEAD identical, left the
   index empty, accumulated reviewed changes unstaged, and still produced a
   workflow-complete document. Because the active harness exposed only three
   subagent slots, its documentation role reused the reset test-agent thread;
   all other forward-test stages used isolated role contexts, and automated
   contract tests cover the fresh-context requirement.

Tooling caveat: Spec Kit 0.13.0 adds a standard `compatibility` field to every
generated integration wrapper, including official Spec Kit wrappers. The
current skill-creator `quick_validate.py` rejects that field even though Spec
Kit generated and registered the wrapper successfully. The extension command
source does not declare the field; it is generator-owned metadata.

## Historical Manual Testing Record

Historical v1.0.0 testing completed:

1. Parser CLI smoke tests completed for:
   `python3 scripts/phase_tasks.py examples/sample-tasks.md --mode next --json`,
   `python3 scripts/phase_tasks.py examples/sample-tasks.md --phase 3 --json`,
   and
   `python3 scripts/phase_tasks.py examples/sample-tasks.md --mode all --json`.
2. Development install completed with
   `specify extension add --dev /path/to/spec-kit-phase-orchestrator`.
3. Extension registration and command availability were verified successfully
   on Codex, Claude Code, and Cursor.
4. The extension workflow was manually tested successfully on Codex, Claude
   Code, and Cursor.
5. Adding Claude Code after the initial installation reproduced the
   missing-wrapper issue.
6. `specify extension remove phase-orchestrator` plus re-adding from the
   original source fixed Claude registration.
7. `specify integration use claude` succeeded.
8. `specify extension update phase-orchestrator` reported that the extension
   catalog entry was not found.

The v2.0.0 release-archive test remains pending because no v2.0.0 tag or release
has been published. Final minimum-version and non-Codex integration retesting
also remain release-candidate tasks.

## Prerelease Guardrails

1. Before publishing a tag-based install command, verify the tag exists remotely with `git ls-remote --tags origin <tag>`.
2. Before release, verify every documented install URL returns `HTTP 200`, for example with `curl -I -L <install-url>`.
3. If the extension is not published in a Spec Kit extension catalog, do not position `specify extension update phase-orchestrator` as the primary refresh or re-registration path.
4. Catalog publication can be added later, but it should not block documentation or release-hygiene fixes.
5. When a real release tag is published, update the README and submission notes together so the documented install command matches the tagged archive.

## AI Disclosure

I used AI assistance to help draft documentation and structure the extension,
then manually reviewed and tested the repository before submission.
