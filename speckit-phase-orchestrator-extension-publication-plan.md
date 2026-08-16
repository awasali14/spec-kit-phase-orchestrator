# Spec Kit Phase Orchestrator Extension Publication Plan

Last updated: 2026-08-07

## 1. Document Authority

This document is the ground-truth plan for preparing, releasing, and submitting
the Spec Kit Phase Orchestrator extension. Follow it until the extension is
accepted into the Spec Kit community extension catalog.

Status values used throughout this plan:

1. **Completed**: Finished and verified. Do not repeat unless a later change
   invalidates the result.
2. **In progress**: Started but not yet ready to treat as complete.
3. **Not started**: Approved work that still needs to be performed.
4. **Blocked**: Cannot proceed until the stated dependency is resolved.
5. **Approved**: A decision has been accepted but may still have a separately
   tracked implementation step.
6. **Ongoing**: A recurring rule that applies throughout development and
   maintenance rather than finishing once.

If this plan conflicts with the latest official Spec Kit documentation, the
official documentation wins. Update this plan before continuing.

### Current State

1. **Status: Completed** — Public repository created at
   `https://github.com/awasali14/spec-kit-phase-orchestrator`.
2. **Status: Completed** — Initial release `v1.0.0` published from commit
   `02c829d` on 2026-07-04.
3. **Status: Completed** — The `v1.0.0` tag archive was installed successfully
   in a disposable Spec Kit project.
4. **Status: Completed** — The extension was manually tested successfully with
   Codex, Claude Code, and Cursor.
5. **Status: In progress** — Post-`v1.0.0` improvements are being prepared for
   release as `v2.0.0`.
6. **Status: Not started** — Spec Kit community extension submission.

## 2. Product Decisions

### Goal And Positioning

1. **Status: Completed** — Publish the project-local phase orchestration
   workflow as a public Spec Kit extension.
2. **Status: Completed** — Use the public name `Spec Kit Phase Orchestrator`,
   repository name `spec-kit-phase-orchestrator`, and extension ID
   `phase-orchestrator`.
3. **Status: Completed** — Identify `awasali14` as the maintainer and author.
4. **Status: Completed** — Keep the extension agent-agnostic through Spec Kit's
   integration and command-rendering system rather than publishing a
   Codex-only skill.
5. **Status: Completed** — Keep `/speckit.implement` as the official
   implementation workflow. Phase Orchestrator is a companion command and must
   not replace, bypass, or modify it.
6. **Status: Completed** — Use one public command:
   `speckit.phase-orchestrator.phase`.

### Canonical Description

1. **Status: Completed on 2026-08-07** — Use this description in
   `extension.yml`, submission metadata, and concise public summaries:

   ```text
   Orchestrate each Spec Kit tasks.md phase through isolated test,
   implementation, verification, remediation, and documentation stages with
   parent-owned Git gates.
   ```

### Supported Command Behavior

1. **Status: Completed** — Support `next <tasks.md path>`.
2. **Status: Completed** — Support `phase <number> <tasks.md path>`.
3. **Status: Completed** — Support `all <tasks.md path>`.
4. **Status: Completed** — Support `--docs-dir <directory>`.
5. **Status: Completed** — Honor an explicit Markdown documentation path given
   in natural language.
6. **Status: Completed on 2026-08-07** — Create parent-owned stage commits after
   each eligible successful test, implementation, remediation, and
   documentation stage.
7. **Status: Completed** — Support `--no-commit` and clear natural-language
   requests not to commit.
8. **Status: Completed** — Never push to a remote. Pushing is user-owned.
9. **Status: Completed on 2026-08-07** — Run context-isolated test,
   implementation, read-only verification, conditional remediation and fresh
   re-verification, and documentation agents sequentially for each phase.
10. **Status: Completed** — Require subagents or isolated worker contexts. If
    they are unavailable, abort and explain the requirement. Do not execute the
    selected phase in the parent context.
11. **Status: Completed** — In `next` and explicit `phase` modes, stop after the
    selected phase.
12. **Status: Completed on 2026-08-07** — In `all` mode, continue sequentially only
    after the current phase passes every stage, validation, documentation, and
    Git gate and records workflow completion.
13. **Status: Completed** — Stop after blockers, unresolved ambiguity,
    validation failure, missing documentation, or unsafe Git state.

### Phase Output Contract

1. **Status: Completed on 2026-08-07** — Only the documentation agent writes the
   Markdown phase execution document, after final verification passes.
2. **Status: Completed on 2026-08-07** — The document aggregates stage reports,
   task IDs, stage commit SHAs and manifests, validation, expected failures,
   issues, and a styled Mermaid phase-flow diagram unless the user opts out.
3. **Status: Completed on 2026-08-07** — The parent validates the document and its
   durable workflow-complete marker before the documentation commit gate.
4. **Status: Completed** — Separate phase receipt files are no longer part of
   the current product contract.

## 3. Canonical Repository Files

Do not duplicate full copies of these files in this plan. Their repository
versions are canonical:

1. **Status: Completed** — Manifest: `extension.yml`.
2. **Status: Completed** — Public command:
   `commands/speckit.phase-orchestrator.phase.md`.
3. **Status: Completed** — Parser: `scripts/phase_tasks.py`.
4. **Status: Completed** — Worker prompt contract:
   `references/worker-prompt-template.md`.
5. **Status: Completed** — Phase document contract:
   `references/phase-doc-template.md`.
6. **Status: Completed** — Mermaid styling contract:
   `references/mermaid-style.md`.
7. **Status: Completed** — Public overview and installation guide: `README.md`.
8. **Status: Completed** — Detailed usage guide: `docs/usage.md`.
9. **Status: Completed** — Agent compatibility guide:
   `docs/agent-support.md`.
10. **Status: Completed on 2026-08-04** — Sole installed examples and use-cases
    document: `docs/examples.md`.
11. **Status: Completed** — Submission working record:
    `docs/submission-notes.md`.
12. **Status: Completed** — License: `LICENSE`.
13. **Status: Completed** — Release history: `CHANGELOG.md`.

## 4. Repository And Installed-Payload Contracts

### Repository Source Contract

Development material must remain tracked in Git on `dev` and `main` so a fresh
clone on another computer contains everything needed to continue development.

1. **Status: Completed** — Keep parser tests under `tests/` in Git.
2. **Status: Completed** — Keep test fixtures under `examples/` in Git.
3. **Status: Completed** — Keep development schemas under `schemas/` in Git
   until they are intentionally retired in a separate reviewed change.
4. **Status: Completed** — Keep `docs/submission-notes.md` in Git until catalog
   submission is complete.
5. **Status: Completed on 2026-08-04** — Track this publication plan in Git.
   Commit `efa5a59` is present on both local and remote `dev`.
6. **Status: Completed** — Keep `git-branch-plan.md` local-only unless a future
   decision explicitly makes it public.

### Installed Extension Contract

The installed extension should contain only runtime files, public
documentation, license and changelog metadata, and one examples document.

Files and directories that must remain in the installed payload:

1. **Status: Completed** — `extension.yml`.
2. **Status: Completed** — `commands/`.
3. **Status: Completed** — `scripts/phase_tasks.py`.
4. **Status: Completed** — Required files under `references/`.
5. **Status: Completed** — `README.md`.
6. **Status: Completed** — `LICENSE`.
7. **Status: Completed** — `CHANGELOG.md`.
8. **Status: Completed** — `docs/usage.md`.
9. **Status: Completed** — `docs/agent-support.md`.
10. **Status: Completed on 2026-08-04** — `docs/examples.md` as the only
    installed examples and use-cases artifact.
11. **Status: Completed on 2026-08-07** — `schemas/phase-handoff.schema.json`,
    because the v2 command consumes the handoff contract at runtime.

Files and directories that must be excluded by `.extensionignore` while
remaining available in the Git repository:

1. **Status: Completed on 2026-08-04** — Added `tests/`.
2. **Status: Completed on 2026-08-04** — Added `examples/` after
   `docs/examples.md` was made self-contained.
3. **Status: Completed historically; changed for v2.0.0** — `schemas/` was
   excluded in v1, but the v2 runtime now requires the handoff schema and must
   install it.
4. **Status: Completed on 2026-08-04** — Added `docs/submission-notes.md`.
5. **Status: Completed** — Exclude this publication plan.
6. **Status: Completed** — Exclude `git-branch-plan.md`.
7. **Status: Completed** — Exclude `.git/` and `.gitignore`.
8. **Status: Completed** — Exclude Python bytecode and cache directories.
9. **Status: Completed on 2026-08-04** — Added `.github/`, `.agents/`,
   `.codex/`, and `.tools/` as defensive development-install exclusions. These
   paths are not currently part of the tagged Git source archive, but local
   `--dev` installation must not copy them if they exist.

### Single Examples Document

`docs/examples.md` must be understandable by both users and AI coding agents
without requiring files from the excluded `examples/` directory.

1. **Status: Completed on 2026-08-04** — Explained when to use `next`, explicit
   `phase`, and `all` modes.
2. **Status: Completed on 2026-08-04** — Included slash-command invocation for
   compatible agents and the Codex `$speckit-phase-orchestrator-phase`
   invocation.
3. **Status: Completed on 2026-08-04** — Included `--docs-dir` and
   `--no-commit` examples.
4. **Status: Completed on 2026-08-04** — Included a compact but realistic
   `tasks.md` sample.
5. **Status: Completed on 2026-08-04** — Included representative parser output.
6. **Status: Completed on 2026-08-04** — Included a representative
   selected-phase worker handoff.
7. **Status: Completed on 2026-08-04** — Showed expected validation, Markdown
   documentation, and parent-commit results.
8. **Status: Completed on 2026-08-04** — Updated README and other public
   documentation to link only to `docs/examples.md` for examples.

### Source Archive Versus Installed Copy

1. **Status: Completed** — Understand that a GitHub tag archive contains all
   files tracked at that tag, including development files.
2. **Status: Completed** — Use `.extensionignore` to keep development files out
   of the copy installed by `specify extension add`.
3. **Status: Approved** — The Spec Kit submission may use the standard GitHub
   tag archive because the official installer applies `.extensionignore` when
   creating the installed extension copy.
4. **Status: Not started** — Verify the exact installed payload from the final
   `v2.0.0` tag archive before submission.

## 5. Branch And Release Workflow

### Long-Lived Branches

1. **Status: Completed** — `dev` is the development and integration branch.
2. **Status: Completed** — `main` is the production and release-ready branch.
3. **Status: Approved** — Tests and other development sources remain tracked on
   both branches. Branch-specific file deletion is not used for packaging.

### Normal Development

1. **Status: Ongoing** — Start new work from an up-to-date `dev` branch.
2. **Status: Ongoing** — Review changes and run relevant automated and manual
   tests before committing.
3. **Status: Ongoing** — Commit development work on `dev` with a concise subject
   and explanatory body.
4. **Status: Ongoing** — Push completed development commits to `origin/dev` so
   another computer can clone and continue the work.

### Release Flow

Use this order for every release:

1. **Status: Not started for v2.0.0** — Finish and push tested work on `dev`.
2. **Status: Not started for v2.0.0** — Switch to `main` and update it from
   `origin/main` using `git pull --ff-only origin main`.
3. **Status: Not started for v2.0.0** — Merge `dev` into `main`.
4. **Status: Not started for v2.0.0** — Run the complete release verification
   suite on the exact `main` commit.
5. **Status: Not started for v2.0.0** — Create annotated tag `v2.0.0` from the
   verified `main` commit.
6. **Status: Not started for v2.0.0** — Push `main` and `v2.0.0`.
7. **Status: Not started for v2.0.0** — Publish the GitHub release.
8. **Status: Not started for v2.0.0** — If `main` contains release-only commits
   not already in `dev`, merge `main` back into `dev` and push `dev`.
9. **Status: Approved** — Never create a release tag before the release commit
   reaches `main`, and never treat a tag as a development branch to merge.

If a temporary `release/vX.Y.Z` branch is used, create it from `dev`, merge it
into `main`, tag the resulting `main` commit, and then synchronize any
release-only changes back to `dev`.

## 6. Compatibility And Dependencies

### Spec Kit

1. **Status: Completed** — The manifest currently declares
   `speckit_version: ">=0.8.7"`.
2. **Status: Completed** — `.extensionignore` support predates Spec Kit 0.8.7
   and is therefore compatible with the declared minimum.
3. **Status: Completed** — Earlier testing covered Spec Kit 0.8.7 and 0.9.1.
4. **Status: Completed** — The current development environment uses Spec Kit
   CLI 0.13.0.
5. **Status: Not started** — Re-run the final compatibility suite against
   0.8.7 after all `v2.0.0` changes. If this is not done, raise the declared
   minimum to the oldest version actually verified for the release.

### Python

1. **Status: Completed** — Require Python 3.10 or newer.
2. **Status: Completed** — Align public documentation with the manifest; do not
   state Python 3.9 compatibility.

### Git

1. **Status: Completed on 2026-08-04** — The manifest marks Git required because
   the default workflow uses Git status, diff, staging, and commit operations.
2. **Status: Completed on 2026-08-04** — Marked Git as required in
   `extension.yml`.

## 7. Completed Implementation History

This section preserves work already executed. These milestones remain
completed even when later release work refines their outputs.

### Repository Setup

1. **Status: Completed on 2026-06-02** — Created the public GitHub repository.
2. **Status: Completed** — Created the extension folder structure.
3. **Status: Completed** — Added the GitHub remote.
4. **Status: Completed** — Added manifest, command, parser, references, schemas,
   documentation, examples, tests, license, changelog, and ignore files.

### Manifest And Command

1. **Status: Completed** — Created a valid schema-version `1.0` manifest.
2. **Status: Completed** — Declared extension ID `phase-orchestrator` and one
   public command.
3. **Status: Completed** — Updated command naming for current Spec Kit
   integrations.
4. **Status: Completed** — Protected official `/speckit.implement` behavior.
5. **Status: Completed** — Added isolated-worker handoff and sanitization rules.
6. **Status: Completed** — Added documentation and parent post-phase gates.

### Parser

1. **Status: Completed** — Ported the parser to `scripts/phase_tasks.py`.
2. **Status: Completed** — Added `next`, explicit phase, and `all` selection.
3. **Status: Completed** — Added JSON output and clear failure behavior.
4. **Status: Completed** — Added test-versus-implementation task
   classification.
5. **Status: Completed** — Added generated documentation paths and
   `--docs-dir` support.

### Examples, Handoffs, And Earlier Receipt Work

1. **Status: Completed** — Created realistic five-phase and six-phase task
   fixtures.
2. **Status: Completed** — Created a representative phase handoff and handoff
   schema.
3. **Status: Completed historically; intentionally superseded** — Earlier
   receipt schema and receipt-example work was completed, then removed when the
   workflow was simplified to one Markdown phase execution document.
4. **Status: Completed** — Updated documentation and tests so removed receipt
   artifacts are no longer presented as current outputs.

### Public Documentation

1. **Status: Completed** — Created README installation, usage, safety,
   troubleshooting, testing, and license sections.
2. **Status: Completed** — Created usage, agent-support, examples, and
   submission-note documents.
3. **Status: Completed** — Documented Spec Kit integration skill directories.
4. **Status: Completed** — Documented successful testing on Codex, Claude Code,
   and Cursor.
5. **Status: Completed** — Corrected the documented Python requirement to
   Python 3.10 or newer.

### License And Changelog

1. **Status: Completed** — Added the MIT license.
2. **Status: Completed** — Added the initial `1.0.0` changelog.

### Automated Tests

1. **Status: Completed** — Added parser unit tests.
2. **Status: Completed** — Added coverage for phase selection, documentation
   paths, task classification, handoff sanitization, Mermaid requirements, and
   integration documentation.
3. **Status: Completed on 2026-07-29** — All 24 unit tests passed.
4. **Status: Completed on 2026-07-29** — Parser CLI smoke tests for `next`,
   explicit phase, and `all` passed.

### Manual Integration Testing

1. **Status: Completed** — Development installation with
   `specify extension add --dev` succeeded.
2. **Status: Completed** — Codex registration and extension execution were
   tested successfully.
3. **Status: Completed** — Claude Code registration and extension execution
   were tested successfully.
4. **Status: Completed** — Cursor registration and extension execution were
   tested successfully.
5. **Status: Completed** — The missing-wrapper behavior after adding another
   integration was reproduced and resolved during earlier testing.
6. **Status: Completed** — `specify integration use claude` succeeded during
   earlier testing.
7. **Status: Completed** — Confirmed that `specify extension update` cannot
   update this extension before it exists in an active catalog.

### Git And Initial Release

1. **Status: Completed on 2026-07-04** — Committed initial publication work on
   `dev`.
2. **Status: Completed on 2026-07-04** — Fast-forwarded `dev` into `main` and
   pushed `main`.
3. **Status: Completed on 2026-07-04** — Created and pushed tag `v1.0.0` from
   commit `02c829d`.
4. **Status: Completed on 2026-07-04** — Published GitHub release `v1.0.0`.
5. **Status: Completed on 2026-07-04** — Confirmed the tag archive URL resolves
   to a ZIP download.
6. **Status: Completed on 2026-07-04** — Installed the archive into disposable
   disposable project.
7. **Status: Completed on 2026-07-04** — Verified the installed extension was
   enabled and its Codex wrapper existed.

## 8. Current v2.0.0 Work Plan

### Documentation And Metadata

1. **Status: Completed on 2026-08-07** — Align public documentation with the staged-agent
   architecture and workflow-completion resume behavior.
2. **Status: Completed on 2026-08-07** — Use the approved concise v2.0.0 canonical and
   integration-facing descriptions.
3. **Status: Completed on 2026-08-05** — Set the manifest version to `2.0.0`
   while retaining manifest schema version `1.0`.
4. **Status: Completed on 2026-08-05** — Add an unreleased `2.0.0` changelog
   entry covering the staged architecture and safety contract.
5. **Status: Not started** — Update README installation instructions to use the
   real `v2.0.0` archive only after that tag exists and the archive is verified.
6. **Status: Completed on 2026-08-07** — Keep `docs/submission-notes.md` aligned
   with the planned v2.0.0 metadata and record completed pre-release evidence.

### Packaging

1. **Status: Completed on 2026-08-04** — Made `docs/examples.md` self-contained.
2. **Status: Completed on 2026-08-05** — Keep development-only exclusions in
   `.extensionignore` while installing the runtime v2 handoff schema.
3. **Status: Completed on 2026-08-07** — Simulate a development install and list the exact
   installed payload.
4. **Status: Completed on 2026-08-07** — Confirm the installed payload contains the v2
   handoff schema but no tests, fixtures, submission notes, publication plans,
   branch plans, local hooks, caches, or agent/tool workspace directories.
5. **Status: Completed on 2026-08-07** — Confirm `docs/examples.md` is the only installed
   examples artifact.

### Integration Guidance

1. **Status: Not started** — Recheck extension registration behavior with Spec
   Kit 0.13.0 using `specify integration use` or `switch`.
2. **Status: Not started** — Reconcile README and agent-support troubleshooting
   guidance with the current official integration behavior.
3. **Status: Not started** — Keep remove-and-reinstall steps only as a verified
   fallback for CLI versions where switching integrations does not resurface
   installed extension commands.

## 9. Final Verification Matrix

### Repository Verification

1. **Status: Completed on 2026-08-07** — `git diff --check` passes.
2. **Status: Completed on 2026-08-07** — `git status --short` contains only
   intentional release changes before commit.
3. **Status: Completed on 2026-08-07** — No secrets, credentials, private project
   paths, generated caches, or unrelated files are tracked.
4. **Status: Completed on 2026-08-07** — Manifest, README, changelog, release
   notes, and submission values use the same version and description.

### Automated Verification

1. **Status: Completed on 2026-08-07** — Run
   `python3 -m unittest discover -s tests`.
2. **Status: Completed on 2026-08-07** — Run parser smoke tests for `next`,
   explicit phase, and `all`.
3. **Status: Completed on 2026-08-07** — Validate workflow completion and
   verification resume, empty stages, classification, custom docs, role
   sanitization, remediation cap, expected RED and green gates, exact staging,
   dirty state, no-change stages, `--no-commit`, and documentation completion.
4. **Status: Completed on 2026-08-07** — Load `extension.yml` through a Spec
   Kit 0.13.0 development install and confirm version 2.0.0 is enabled.

### Development Installation

1. **Status: Completed on 2026-08-07** — Install from the final local directory
   into a clean Spec Kit project.
2. **Status: Completed on 2026-08-07** — Verify the extension is enabled and the
   command wrapper is registered for the active integration.
3. **Status: Completed on 2026-08-07** — Inspect the installed payload against
   the contract in Section 4.

### Agent Matrix

1. **Status: Completed historically; final release retest not started** — Codex.
2. **Status: Completed historically; final release retest not started** —
   Claude Code.
3. **Status: Completed historically; final release retest not started** —
   Cursor.
4. **Status: Completed on 2026-08-07** — Forward-test isolated agents in
   disposable repositories with minimal context; never use production projects.
5. **Status: Completed on 2026-08-07** — Cover happy path, remediation success,
   remediation exhaustion, empty stages, unrelated dirty files, and
   `--no-commit`.
6. **Status: In progress** — Record agent and Spec Kit versions,
   operating system, mode, stage results, validation, documentation path, and
   caveats for each final test. Codex desktop isolated-agent results, Spec Kit
   0.13.0, Linux/WSL2, stage outcomes, and the three-slot harness caveat are
   recorded; the runtime did not expose a subagent model build identifier.

### Release Archive

1. **Status: Not started for v2.0.0** — Confirm remote tag `v2.0.0` exists.
2. **Status: Not started for v2.0.0** — Confirm the archive URL returns a valid
   ZIP download.
3. **Status: Not started for v2.0.0** — Install from:

   ```text
   https://github.com/awasali14/spec-kit-phase-orchestrator/archive/refs/tags/v2.0.0.zip
   ```

4. **Status: Not started for v2.0.0** — Run `specify extension list` and verify
   `Phase Orchestrator (v2.0.0)` is enabled.
5. **Status: Not started for v2.0.0** — Inspect the archive-installed payload
   against Section 4.
6. **Status: Not started for v2.0.0** — Verify command registration and a real
   command run from the archive installation.

Do not submit if any required final verification remains incomplete.

## 10. GitHub Release v2.0.0

1. **Status: Not started** — Finish all work and verification on `dev`.
2. **Status: Not started** — Merge `dev` into `main`.
3. **Status: Not started** — Verify the exact `main` release commit.
4. **Status: Not started** — Create annotated tag:

   ```bash
   git tag -a v2.0.0 -m "Release v2.0.0"
   ```

5. **Status: Not started** — Push `main` and the tag.
6. **Status: Not started** — Create the GitHub release with release notes based
   on `CHANGELOG.md`.
7. **Status: Not started** — Complete the archive-install checks in Section 9.
8. **Status: Not started** — Synchronize release-only `main` commits back to
   `dev` if necessary.

If a release-blocking defect is found after publishing `v2.0.0`, do not move or
overwrite the tag. Fix it on `dev` and publish a new patch version.

## 11. Spec Kit Community Submission

### Submission Process

1. **Status: Completed on 2026-08-03** — Rechecked the official Extension
   Publishing Guide, Extension Development Guide, integrations reference,
   contribution guide, submission issue template, and community catalog.
2. **Status: Completed** — Confirmed that new community extensions are
   submitted through the Extension Submission issue template.
3. **Status: Completed** — Confirmed that authors should not directly edit
   `extensions/catalog.community.json` for a new submission.
4. **Status: Not started** — Recheck the official process again immediately
   before submitting.
5. **Status: Not started** — Open the current Extension Submission issue:
   `https://github.com/github/spec-kit/issues/new?template=extension_submission.yml`.

### Planned Submission Values

1. **Status: Approved** — Extension ID: `phase-orchestrator`.
2. **Status: Approved** — Extension Name: `Phase Orchestrator`.
3. **Status: Approved** — Version: `2.0.0`.
4. **Status: Approved** — Description:
   `Orchestrate each Spec Kit tasks.md phase through isolated test, implementation, verification, remediation, and documentation stages with parent-owned Git gates.`
5. **Status: Approved** — Author: `awasali14`.
6. **Status: Approved** — Repository:
   `https://github.com/awasali14/spec-kit-phase-orchestrator`.
7. **Status: Approved as a planned value; not yet published** — Download URL:
   `https://github.com/awasali14/spec-kit-phase-orchestrator/archive/refs/tags/v2.0.0.zip`.
8. **Status: Approved** — License: `MIT`.
9. **Status: Approved** — Homepage:
   `https://github.com/awasali14/spec-kit-phase-orchestrator`.
10. **Status: Approved** — Documentation URL:
    `https://github.com/awasali14/spec-kit-phase-orchestrator/tree/main/docs`.
11. **Status: Approved** — Changelog URL:
    `https://github.com/awasali14/spec-kit-phase-orchestrator/blob/main/CHANGELOG.md`.
12. **Status: In progress** — Required Spec Kit version: `>=0.8.7`, pending the
    final minimum-version compatibility test.
13. **Status: Approved** — Required Python version: `>=3.10`.
14. **Status: Completed on 2026-08-04** — Git is required in `extension.yml`.
15. **Status: Approved** — Number of commands: `1`.
16. **Status: Approved** — Number of hooks: `0`.
17. **Status: Approved** — Command:
    `speckit.phase-orchestrator.phase`.
18. **Status: Approved** — Category: `process`.
19. **Status: Approved** — Effect: `read-write`.
20. **Status: Approved** — Tags: `workflow`, `implementation`,
    `orchestration`, `tasks`.

### Key Features

1. **Status: Approved** — Selects the next workflow-incomplete phase, an
   explicit phase, or all remaining workflow-incomplete phases from an existing
   Spec Kit `tasks.md`.
2. **Status: Approved** — Runs sequential context-isolated test,
   implementation, read-only verification, conditional remediation and fresh
   re-verification, and documentation agents.
3. **Status: Approved** — Keeps `/speckit.implement` as the official
   implementation workflow.
4. **Status: Approved** — Builds compact v2 stage handoffs containing only
   phase scope, prior SHA and manifests, validation, and expected failures.
5. **Status: Approved** — Uses independent read-only verification, at most two
   remediation cycles, and documentation with a workflow-complete marker.
6. **Status: Approved** — Creates parent-owned stage Conventional Commits with
   exact-path staging and `--no-commit` opt-out support.
7. **Status: Approved** — Never pushes to remotes.

### Submission Checklist

1. **Status: Completed on 2026-08-07** — Valid
   `extension.yml` exists.
2. **Status: Completed on 2026-08-07** — README
   contains installation and usage instructions.
3. **Status: Completed** — MIT `LICENSE` exists.
4. **Status: Completed on 2026-08-07** — All
   command files exist and are properly formatted.
5. **Status: Completed** — Extension ID follows lowercase-with-hyphens naming.
6. **Status: Not started** — `v2.0.0` GitHub release exists.
7. **Status: Not started** — Extension installs successfully through the final
   download URL.
8. **Status: Not started** — All documented command modes execute without
   errors in the final release test matrix.
9. **Status: Completed on 2026-08-07** — Make documentation complete and accurate for the
   v2.0.0 workflow.
10. **Status: Completed on 2026-08-07** — Final security and secret review finds no known
    vulnerabilities or exposed credentials.
11. **Status: Completed on 2026-08-07** —
    Tested on at least one realistic project.
12. **Status: Not started** — Final testing details and example usage are copied
    from verified `v2.0.0` evidence into the submission issue.

### Proposed Catalog Entry

Update dates and the minimum Spec Kit version from final evidence immediately
before submission:

```json
{
  "phase-orchestrator": {
    "name": "Phase Orchestrator",
    "id": "phase-orchestrator",
    "description": "Orchestrate each Spec Kit tasks.md phase through isolated test, implementation, verification, remediation, and documentation stages with parent-owned Git gates.",
    "author": "awasali14",
    "version": "2.0.0",
    "download_url": "https://github.com/awasali14/spec-kit-phase-orchestrator/archive/refs/tags/v2.0.0.zip",
    "repository": "https://github.com/awasali14/spec-kit-phase-orchestrator",
    "homepage": "https://github.com/awasali14/spec-kit-phase-orchestrator",
    "documentation": "https://github.com/awasali14/spec-kit-phase-orchestrator/tree/main/docs",
    "changelog": "https://github.com/awasali14/spec-kit-phase-orchestrator/blob/main/CHANGELOG.md",
    "license": "MIT",
    "category": "process",
    "effect": "read-write",
    "requires": {
      "speckit_version": ">=0.8.7",
      "tools": [
        {
          "name": "python",
          "version": ">=3.10",
          "required": true
        },
        {
          "name": "git",
          "required": true
        }
      ]
    },
    "provides": {
      "commands": 1,
      "hooks": 0
    },
    "tags": [
      "workflow",
      "implementation",
      "orchestration",
      "tasks"
    ],
    "verified": false,
    "downloads": 0,
    "stars": 0,
    "created_at": "<submission-date>T00:00:00Z",
    "updated_at": "<submission-date>T00:00:00Z"
  }
}
```

### AI Disclosure

1. **Status: Approved** — Include this disclosure in the submission:

   ```text
   I used AI assistance to help draft documentation and structure the extension,
   then manually reviewed and tested the repository before submission.
   ```

## 12. After Submission

1. **Status: Not started** — Monitor maintainer feedback and the submission
   issue.
2. **Status: Not started** — Respond to requested clarification or metadata
   corrections.
3. **Status: Not started** — Make requested code or documentation changes on
   `dev`, merge them into `main`, and publish a new patch release if the
   downloadable artifact changes.
4. **Status: Not started** — Submit updated version and download metadata if a
   new release is required.
5. **Status: Not started** — After acceptance, verify the extension appears in
   the community catalog and is discoverable through
   `specify extension search`.
6. **Status: Not started** — Update README installation guidance from direct
   archive installation to catalog installation where appropriate.

## 13. Official Sources To Recheck

1. **Status: Completed on 2026-08-03; recheck before submission** — Extension
   Publishing Guide:
   `https://github.com/github/spec-kit/blob/main/extensions/EXTENSION-PUBLISHING-GUIDE.md`.
2. **Status: Completed on 2026-08-03; recheck before submission** — Extension
   Development Guide:
   `https://github.com/github/spec-kit/blob/main/extensions/EXTENSION-DEVELOPMENT-GUIDE.md`.
3. **Status: Completed on 2026-08-03; recheck before submission** — Supported
   integrations reference:
   `https://github.github.io/spec-kit/reference/integrations.html`.
4. **Status: Completed on 2026-08-03; recheck before submission** — Extension
   Submission issue template:
   `https://github.com/github/spec-kit/issues/new?template=extension_submission.yml`.
5. **Status: Completed on 2026-08-03; recheck before submission** — Current
   community catalog:
   `https://github.com/github/spec-kit/blob/main/extensions/catalog.community.json`.
6. **Status: Completed on 2026-08-03; recheck before submission** — Contribution
   guide:
   `https://github.com/github/spec-kit/blob/main/CONTRIBUTING.md`.

## 14. Execution Order And Progress Tracker

This is the only section to execute as a checklist. Sections 1–13 define the
decisions, requirements, evidence, and detailed acceptance checks used by this
checklist; do not treat their topic-based lists as separate execution queues.

Tracking rules:

1. Work from top to bottom and keep only one stage **In progress** at a time.
2. Do not start a later stage until the current stage's exit condition is met.
3. After completing a stage, update its status here to **Completed**, add the
   completion date and concise evidence, and update any affected detail statuses
   in Sections 1–13 in the same change.
4. If work cannot proceed, mark the current stage **Blocked**, record the exact
   blocker here, and do not skip ahead unless this plan is explicitly revised.
5. Continue updating this file through catalog acceptance so it remains the
   ground-truth progress record.

### Stage 1 — Commit The Current Documentation Baseline

**Status: Completed on 2026-08-04**

Review the prepared Codex, Claude Code, and Cursor documentation changes
together with this publication plan, commit the intentional changes on `dev`,
and push `dev`.

**Exit condition:** The current documentation work is committed, reproducible
from `origin/dev`, and the working tree contains no unexplained changes.

**Evidence:** Local `dev` and `origin/dev` both pointed to documentation commit
`efa5a59`, and the working tree was clean before Stage 2 began.

### Stage 2 — Complete Public Examples And Documentation

**Status: Completed on 2026-08-07**

Align README, usage, examples, agent support, and submission records with the
staged-agent workflow, workflow-completion resume behavior, stage commit gates,
and `--no-commit` manifests. Keep `docs/examples.md` self-contained.

**Exit condition:** A user or agent can understand every supported mode without
the repository-only `examples/` fixtures.

**Evidence:** Public documentation consistently explains the v2
stages, verification/remediation limits, workflow-complete documentation, Git
ownership, safety baselines, custom paths, and preserved command forms.

### Stage 3 — Finalize Runtime And Packaging Contracts

**Status: Completed on 2026-08-07**

Finalize the v2 command, parser, role-specific prompt reference, phase document,
runtime handoff schema, metadata, and development-only exclusions.

**Exit condition:** The manifest, command, repository-source contract, and
installed-payload contract agree.

**Evidence:** A disposable Spec Kit 0.13.0 development install included the v2
handoff schema and
runtime references while excluding tests, fixtures, submission notes,
GitHub/workspace metadata, caches, and local planning files. Manifest schema
version remains `1.0`; extension and handoff contract versions are `2.0.0`.

### Stage 4 — Verify Integration Behavior And Guidance

**Status: In progress**

Test registration and switching with Spec Kit 0.13.0, inspect the generated
integration wrapper, then reconcile README and `docs/agent-support.md`. Retain
remove-and-reinstall instructions only as a verified fallback.

**Exit condition:** The documented primary and fallback integration flows match
observed CLI behavior.

**Evidence:** Spec Kit 0.13.0 registered the generated Codex wrapper and
reported a healthy integration with no modified or missing managed files.
Non-Codex switching and fallback behavior still require release-candidate
retesting.

### Stage 5 — Run Pre-Release Verification On `dev`

**Status: Completed on 2026-08-07**

Run unit tests, parser smoke and failure-path tests, manifest validation, a
Cover workflow completion/resume, empty stages, classification, sanitization,
read-only verification, Mermaid routing, remediation cap, commit gates, exact
staging, dirty state, no-change stages, `--no-commit`, and documentation
completion.

**Exit condition:** All checks pass and the installed copy contains only the
files allowed by Section 4.

**Evidence:** All 43 unit tests, parser mode smokes, schema/sample validation,
Python syntax validation, payload assertions, and `git diff --check` passed.

### Stage 6 — Run The Compatibility And Agent Matrix

**Status: Not started as a release gate; partial evidence completed on 2026-08-07**

Forward-test isolated agents with minimal context in disposable repositories.
Cover happy path, remediation success, remediation exhaustion, empty stages,
unrelated dirty files, and `--no-commit`. Re-test supported integrations and
Spec Kit compatibility without touching production projects.

**Exit condition:** Recorded evidence supports every declared agent, command
mode, tool requirement, and minimum version.

**Available evidence:** The requested disposable Codex isolated-agent matrix
passed all six scenarios. Final Claude Code and Cursor retests and Spec Kit
0.8.7 minimum-version compatibility remain pending, so this release gate is not
complete.

### Stage 7 — Finalize The `v2.0.0` Release Candidate

**Status: Not started**

Set the manifest version to `2.0.0`, add the final changelog entry, update
submission notes with all evidence available before publication, check version
and description consistency, and perform the security and secret review.
Commit and push the complete release candidate on `dev`.

**Exit condition:** `origin/dev` contains the intended release contents and all
pre-tag verification is green. Do not yet change README installation
instructions to claim that the `v2.0.0` archive exists.

### Stage 8 — Promote And Verify The Release Commit

**Status: Not started**

Fast-forward local `main` from `origin/main`, merge `dev` into `main`, and run
the complete release verification suite on the resulting `main` commit.

**Exit condition:** The exact commit to be tagged passes every applicable check
in Section 9 with no unexplained working-tree changes.

### Stage 9 — Tag And Publish `v2.0.0`

**Status: Not started**

Create the annotated tag from the verified `main` commit, push `main` and the
tag, and publish the GitHub release using `CHANGELOG.md`.

**Exit condition:** The remote tag and GitHub release both exist and resolve to
the verified commit.

### Stage 10 — Verify The Immutable Release Archive

**Status: Not started**

Download the real `v2.0.0` tag archive, install it into a clean Spec Kit
project, inspect the installed payload, confirm the enabled version and
registered command, and run a real command from that installation.

**Exit condition:** Every Release Archive check in Section 9 passes. If the
archive has a release-blocking defect, do not move the tag; fix it through
`dev` and publish a new patch version.

### Stage 11 — Publish Verified Post-Release Documentation

**Status: Not started**

Only after the archive is verified, update README installation instructions to
the real `v2.0.0` URL and finish `docs/submission-notes.md` with the exact
release and test results. Make these documentation-only changes on `dev`, merge
them into `main`, and push both branches as applicable.

**Exit condition:** The public default branch and submission record point to
the verified artifact. These are intentionally post-tag documentation commits;
any runtime or installed-payload change requires a new patch release.

### Stage 12 — Submit To The Community Catalog

**Status: Not started**

Recheck every official source in Section 13, confirm the current issue template
and submission requirements, replace all provisional dates or version values,
and open the Extension Submission issue using the approved metadata and AI
disclosure.

**Exit condition:** The submitted issue contains only values supported by the
verified `v2.0.0` release evidence.

### Stage 13 — Handle Review Through Acceptance

**Status: Not started**

Monitor the issue, answer maintainer feedback, route artifact changes through
`dev` and a new patch release when necessary, then verify catalog discovery and
update installation guidance after acceptance.

**Exit condition:** The extension is accepted, discoverable through
`specify extension search`, and the public installation guidance reflects the
catalog workflow.
