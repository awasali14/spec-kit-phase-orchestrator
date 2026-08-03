# Spec Kit Phase Orchestrator Extension Publication Plan

Last updated: 2026-08-03

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
   release as `v1.0.1`.
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

1. **Status: Approved; implementation not started** — Use this description in
   `extension.yml`, submission metadata, and concise public summaries:

   ```text
   Run Spec Kit tasks.md phase-by-phase with isolated workers and validation gates.
   ```

2. **Status: Completed** — Use this longer explanation where more context is
   appropriate:

   ```text
   Spec Kit Phase Orchestrator runs existing Spec Kit tasks.md files one phase
   at a time with isolated worker handoffs, focused validation, Markdown phase
   execution documents, and parent-owned post-phase commits.
   ```

### Supported Command Behavior

1. **Status: Completed** — Support `next <tasks.md path>`.
2. **Status: Completed** — Support `phase <number> <tasks.md path>`.
3. **Status: Completed** — Support `all <tasks.md path>`.
4. **Status: Completed** — Support `--docs-dir <directory>`.
5. **Status: Completed** — Honor an explicit Markdown documentation path given
   in natural language.
6. **Status: Completed** — Create a parent-owned post-phase commit by default.
7. **Status: Completed** — Support `--no-commit` and clear natural-language
   requests not to commit.
8. **Status: Completed** — Never push to a remote. Pushing is user-owned.
9. **Status: Completed** — Use exactly one selected-phase worker at a time.
10. **Status: Completed** — Require subagents or isolated worker contexts. If
    they are unavailable, abort and explain the requirement. Do not execute the
    selected phase in the parent context.
11. **Status: Completed** — In `next` and explicit `phase` modes, stop after the
    selected phase.
12. **Status: Completed** — In `all` mode, continue sequentially only after the
    current phase passes task, validation, documentation, and Git gates.
13. **Status: Completed** — Stop after blockers, unresolved ambiguity,
    validation failure, missing documentation, or unsafe Git state.

### Phase Output Contract

1. **Status: Completed** — The selected-phase worker writes one Markdown phase
   execution document to the path resolved by the parent orchestrator.
2. **Status: Completed** — The document records completed task IDs, changed
   files, validation commands and results, issues or caveats, and a styled
   Mermaid phase-flow diagram unless the user opts out.
3. **Status: Completed** — The parent validates the document during the
   post-phase gate.
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
10. **Status: In progress** — Sole installed examples and use-cases document:
    `docs/examples.md`.
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
5. **Status: In progress** — Track this publication plan in Git. It has been
   removed from `.gitignore` and staged; commit and push are still pending.
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
10. **Status: In progress** — `docs/examples.md` as the only installed examples
    and use-cases artifact.

Files and directories that must be excluded by `.extensionignore` while
remaining available in the Git repository:

1. **Status: Not started** — Add `tests/`.
2. **Status: Not started** — Add `examples/` after `docs/examples.md` is made
   self-contained.
3. **Status: Not started** — Add `schemas/` because the current command and
   parser do not consume the schema at runtime.
4. **Status: Not started** — Add `docs/submission-notes.md`.
5. **Status: Completed** — Exclude this publication plan.
6. **Status: Completed** — Exclude `git-branch-plan.md`.
7. **Status: Completed** — Exclude `.git/` and `.gitignore`.
8. **Status: Completed** — Exclude Python bytecode and cache directories.
9. **Status: Not started** — Add `.github/`, `.agents/`, `.codex/`, and
   `.tools/` as defensive development-install exclusions. These paths are not
   currently part of the tagged Git source archive, but local `--dev`
   installation must not copy them if they exist.

### Single Examples Document

`docs/examples.md` must be understandable by both users and AI coding agents
without requiring files from the excluded `examples/` directory.

1. **Status: Not started** — Explain when to use `next`, explicit `phase`, and
   `all` modes.
2. **Status: Not started** — Include slash-command invocation for compatible
   agents and the Codex `$speckit-phase-orchestrator-phase` invocation.
3. **Status: Not started** — Include `--docs-dir` and `--no-commit` examples.
4. **Status: Not started** — Include a compact but realistic `tasks.md` sample.
5. **Status: Not started** — Include representative parser output.
6. **Status: Not started** — Include a representative selected-phase worker
   handoff.
7. **Status: Not started** — Show expected validation, Markdown documentation,
   and parent-commit results.
8. **Status: Not started** — Update README and other public documentation to
   link only to `docs/examples.md` for examples.

### Source Archive Versus Installed Copy

1. **Status: Completed** — Understand that a GitHub tag archive contains all
   files tracked at that tag, including development files.
2. **Status: Completed** — Use `.extensionignore` to keep development files out
   of the copy installed by `specify extension add`.
3. **Status: Approved** — The Spec Kit submission may use the standard GitHub
   tag archive because the official installer applies `.extensionignore` when
   creating the installed extension copy.
4. **Status: Not started** — Verify the exact installed payload from the final
   `v1.0.1` tag archive before submission.

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

1. **Status: Not started for v1.0.1** — Finish and push tested work on `dev`.
2. **Status: Not started for v1.0.1** — Switch to `main` and update it from
   `origin/main` using `git pull --ff-only origin main`.
3. **Status: Not started for v1.0.1** — Merge `dev` into `main`.
4. **Status: Not started for v1.0.1** — Run the complete release verification
   suite on the exact `main` commit.
5. **Status: Not started for v1.0.1** — Create annotated tag `v1.0.1` from the
   verified `main` commit.
6. **Status: Not started for v1.0.1** — Push `main` and `v1.0.1`.
7. **Status: Not started for v1.0.1** — Publish the GitHub release.
8. **Status: Not started for v1.0.1** — If `main` contains release-only commits
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
   0.8.7 after all `v1.0.1` changes. If this is not done, raise the declared
   minimum to the oldest version actually verified for the release.

### Python

1. **Status: Completed** — Require Python 3.10 or newer.
2. **Status: Completed** — Align public documentation with the manifest; do not
   state Python 3.9 compatibility.

### Git

1. **Status: In progress** — The manifest currently marks Git optional, but the
   default workflow uses Git status, diff, staging, and commit operations.
2. **Status: Approved; implementation not started** — Mark Git as required in
   `extension.yml` unless the command is explicitly redesigned and tested to
   work outside a Git repository.

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
   project `/tmp/speckit-phase-archive-test-20260704`.
7. **Status: Completed on 2026-07-04** — Verified the installed extension was
   enabled and its Codex wrapper existed.

## 8. Current v1.0.1 Work Plan

### Documentation And Metadata

1. **Status: In progress** — Commit the already prepared documentation updates
   recording successful Codex, Claude Code, and Cursor testing.
2. **Status: Not started** — Replace the manifest description with the approved
   concise description.
3. **Status: Not started** — Update the command description where a shorter
   integration-facing summary improves discoverability.
4. **Status: Not started** — Set the manifest version to `1.0.1` immediately
   before the release candidate is finalized.
5. **Status: Not started** — Add a `1.0.1` changelog entry containing the final
   packaging, documentation, and orchestration changes.
6. **Status: Not started** — Update README installation instructions to use the
   real `v1.0.1` archive only after that tag exists and the archive is verified.
7. **Status: Not started** — Update `docs/submission-notes.md` with the exact
   final release and testing values.

### Packaging

1. **Status: Not started** — Make `docs/examples.md` self-contained.
2. **Status: Not started** — Add the approved development-only exclusions to
   `.extensionignore`.
3. **Status: Not started** — Simulate a development install and list the exact
   installed payload.
4. **Status: Not started** — Confirm the installed payload contains no tests,
   fixtures, schemas, submission notes, publication plans, branch plans, local
   hooks, caches, or agent/tool workspace directories.
5. **Status: Not started** — Confirm `docs/examples.md` is the only installed
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

1. **Status: Not started for v1.0.1** — `git diff --check` passes.
2. **Status: Not started for v1.0.1** — `git status --short` contains only
   intentional release changes before commit.
3. **Status: Not started for v1.0.1** — No secrets, credentials, private project
   paths, generated caches, or unrelated files are tracked.
4. **Status: Not started for v1.0.1** — Manifest, README, changelog, release
   notes, and submission values use the same version and description.

### Automated Verification

1. **Status: Not started for v1.0.1** — Run
   `python3 -m unittest discover -s tests`.
2. **Status: Not started for v1.0.1** — Run parser smoke tests for `next`,
   explicit phase, and `all`.
3. **Status: Not started for v1.0.1** — Validate missing-file and missing-phase
   failure paths.
4. **Status: Not started for v1.0.1** — Load and validate `extension.yml` with
   the release CLI.

### Development Installation

1. **Status: Not started for v1.0.1** — Install from the final local directory
   into a clean Spec Kit project.
2. **Status: Not started for v1.0.1** — Verify the extension is enabled and the
   command wrapper is registered for the active integration.
3. **Status: Not started for v1.0.1** — Inspect the installed payload against
   the contract in Section 4.

### Agent Matrix

1. **Status: Completed historically; final release retest not started** — Codex.
2. **Status: Completed historically; final release retest not started** —
   Claude Code.
3. **Status: Completed historically; final release retest not started** —
   Cursor.
4. **Status: Not started for v1.0.1** — Record agent version, Spec Kit version,
   operating system, command mode, result, validation, documentation path, and
   caveats for each final test.
5. **Status: Not started for v1.0.1** — Confirm at least one realistic run tests
   the default parent-owned commit path.
6. **Status: Not started for v1.0.1** — Confirm at least one realistic run tests
   `--no-commit`.
7. **Status: Not started for v1.0.1** — Confirm `all` mode stops safely after a
   failed or blocked phase.

### Release Archive

1. **Status: Not started for v1.0.1** — Confirm remote tag `v1.0.1` exists.
2. **Status: Not started for v1.0.1** — Confirm the archive URL returns a valid
   ZIP download.
3. **Status: Not started for v1.0.1** — Install from:

   ```text
   https://github.com/awasali14/spec-kit-phase-orchestrator/archive/refs/tags/v1.0.1.zip
   ```

4. **Status: Not started for v1.0.1** — Run `specify extension list` and verify
   `Phase Orchestrator (v1.0.1)` is enabled.
5. **Status: Not started for v1.0.1** — Inspect the archive-installed payload
   against Section 4.
6. **Status: Not started for v1.0.1** — Verify command registration and a real
   command run from the archive installation.

Do not submit if any required final verification remains incomplete.

## 10. GitHub Release v1.0.1

1. **Status: Not started** — Finish all work and verification on `dev`.
2. **Status: Not started** — Merge `dev` into `main`.
3. **Status: Not started** — Verify the exact `main` release commit.
4. **Status: Not started** — Create annotated tag:

   ```bash
   git tag -a v1.0.1 -m "Release v1.0.1"
   ```

5. **Status: Not started** — Push `main` and the tag.
6. **Status: Not started** — Create the GitHub release with release notes based
   on `CHANGELOG.md`.
7. **Status: Not started** — Complete the archive-install checks in Section 9.
8. **Status: Not started** — Synchronize release-only `main` commits back to
   `dev` if necessary.

If a release-blocking defect is found after publishing `v1.0.1`, do not move or
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
3. **Status: Approved** — Version: `1.0.1`.
4. **Status: Approved** — Description:
   `Run Spec Kit tasks.md phase-by-phase with isolated workers and validation gates.`
5. **Status: Approved** — Author: `awasali14`.
6. **Status: Approved** — Repository:
   `https://github.com/awasali14/spec-kit-phase-orchestrator`.
7. **Status: Approved** — Download URL:
   `https://github.com/awasali14/spec-kit-phase-orchestrator/archive/refs/tags/v1.0.1.zip`.
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
14. **Status: Approved; implementation not started** — Git is required.
15. **Status: Approved** — Number of commands: `1`.
16. **Status: Approved** — Number of hooks: `0`.
17. **Status: Approved** — Command:
    `speckit.phase-orchestrator.phase`.
18. **Status: Approved** — Category: `process`.
19. **Status: Approved** — Effect: `read-write`.
20. **Status: Approved** — Tags: `workflow`, `implementation`,
    `orchestration`, `tasks`.

### Key Features

1. **Status: Approved** — Selects the next incomplete phase, an explicit phase,
   or all remaining phases from an existing Spec Kit `tasks.md`.
2. **Status: Approved** — Uses one isolated worker per selected phase and aborts
   if isolated workers are unavailable.
3. **Status: Approved** — Keeps `/speckit.implement` as the official
   implementation workflow.
4. **Status: Approved** — Builds sanitized worker handoffs from parser output,
   selected-phase context, and reusable reference templates.
5. **Status: Approved** — Writes Markdown phase execution documentation with
   validation results and styled Mermaid flow diagrams.
6. **Status: Approved** — Creates parent-owned Conventional Commits by default
   with `--no-commit` opt-out support.
7. **Status: Approved** — Never pushes to remotes.

### Submission Checklist

1. **Status: Completed historically; v1.0.1 verification not started** — Valid
   `extension.yml` exists.
2. **Status: Completed historically; v1.0.1 verification not started** — README
   contains installation and usage instructions.
3. **Status: Completed** — MIT `LICENSE` exists.
4. **Status: Completed historically; v1.0.1 verification not started** — All
   command files exist and are properly formatted.
5. **Status: Completed** — Extension ID follows lowercase-with-hyphens naming.
6. **Status: Not started** — `v1.0.1` GitHub release exists.
7. **Status: Not started** — Extension installs successfully through the final
   download URL.
8. **Status: Not started** — All documented command modes execute without
   errors in the final release test matrix.
9. **Status: In progress** — Documentation is complete and accurate.
10. **Status: Not started** — Final security and secret review finds no known
    vulnerabilities or exposed credentials.
11. **Status: Completed historically; v1.0.1 verification not started** —
    Tested on at least one realistic project.
12. **Status: Not started** — Final testing details and example usage are copied
    from verified `v1.0.1` evidence into the submission issue.

### Proposed Catalog Entry

Update dates and the minimum Spec Kit version from final evidence immediately
before submission:

```json
{
  "phase-orchestrator": {
    "name": "Phase Orchestrator",
    "id": "phase-orchestrator",
    "description": "Run Spec Kit tasks.md phase-by-phase with isolated workers and validation gates.",
    "author": "awasali14",
    "version": "1.0.1",
    "download_url": "https://github.com/awasali14/spec-kit-phase-orchestrator/archive/refs/tags/v1.0.1.zip",
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
