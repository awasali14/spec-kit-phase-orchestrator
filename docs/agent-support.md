# Agent Support

Spec Kit Phase Orchestrator is a Spec Kit extension command, not a Codex-only
skill. The command wording is portable so Spec Kit can render it through
supported integrations.

## Subagent-Capable Agents

The command requires subagents or isolated worker contexts. It should use
exactly one worker for the selected phase. That worker gets a compact handoff
with the phase number, title, incomplete tasks, scope rules, validation
expectations, and documentation requirements.

The worker should not stage, commit, spawn more workers, or continue to another
phase. The parent context owns review, selected-file staging, post-phase
commit creation, and continuation.

Parent-only model and effort settings, fallback model-selection text, and
orchestration instructions should stay with the parent. They are configuration
for creating the worker, not phase work. The worker prompt should include only
sanitized phase instructions plus relevant user-requested skills and concise
reference summaries.

In `all` mode, the parent owns the queue. It should spawn one selected-phase
worker at a time, re-run the parser after each phase, confirm the Markdown
phase document contains a Mermaid block unless the user opted out, review the
phase diff, and keep `all` mode, continuation, staging, committing, and
worker-spawn instructions out of the worker's executable prompt.

When an Exa or equivalent code-context/web MCP is available, its availability
can be included in every worker prompt. Database-specific MCP notes should be
included only when the selected phase tasks or skills indicate database-layer
work such as database, Supabase, Postgres, SQL, migrations, RLS, grants, or
storage policies.

## Unsupported Agents

When subagents or isolated worker contexts are unavailable, the command should
abort and inform the user. It should not run the phase in the current agent
conversation because phase isolation is the core execution boundary.

## Spec Kit Skill Adoption

Spec Kit installs agent-facing command wrappers into the relevant integration
directory when the extension is installed or reinstalled. Do not expect a
wrapper registered for one integration to auto-register in another agent that
is added later.

Common integration skill directories:

1. Codex: `.agents/skills`
2. Cursor: `.cursor/skills`
3. Claude Code: `.claude/skills`

The extension's supporting files remain under
`.specify/extensions/phase-orchestrator/`. Seeing only `SKILL.md` in an agent
skills directory is normal.

If another Spec Kit integration is added after Phase Orchestrator is already
installed, re-register the extension for that integration.

If the extension was originally installed with `--dev`, re-register it from
the same local path:

```bash
specify extension add --dev /path/to/spec-kit-phase-orchestrator
```

If the extension was originally installed from a published release URL,
re-register it with that same archive source:

```bash
specify extension add phase-orchestrator --from <published-release-url>
```

For newer Spec Kit CLIs, `--force` is optional when the command supports it.

For older Spec Kit CLIs without `--force` on `specify extension add`, remove
the extension and re-add it from the same original source:

```bash
specify extension remove phase-orchestrator
specify extension add --dev /path/to/spec-kit-phase-orchestrator
```

If the original source was a published release URL, the re-add command becomes:

```bash
specify extension add phase-orchestrator --from <published-release-url>
```

Restart the coding agent after re-registering the extension.

## Commits

Post-phase commits are parent-owned by default. After clean validation and
documentation checks, the parent stages only selected-phase files and creates
one Conventional Commit that records completed task IDs, changed files,
validation, and Markdown documentation path.

If the user includes `--no-commit` or clearly says not to commit, the parent
skips staging and commit creation and reports changed files for manual review.
The orchestrator must never push; pushing is always user-owned.

## Documentation Paths

When no custom documentation location is provided, phase documentation and
execution docs should use the parser-generated path under
`Documentation/{feature-slug}/`. If the user provides a documentation directory
or documentation path, use that location exactly.

## Agent Requirements

Codex is not required.

Claude Code is not required.

Any agent integration that can execute the Spec Kit command prompt and run the
supporting parser can use the workflow. Agents without a Python runtime can
still follow the command text manually, but the packaged parser requires
Python 3.9 or newer.
