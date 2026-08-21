# Agent Support

Spec Kit Phase Orchestrator is a Spec Kit extension command, not a Codex-only
skill. The command wording is portable so Spec Kit can render it through
supported integrations.

## Verified Integrations

Manual extension testing has been completed successfully with:

1. Codex
2. Claude Code
3. Cursor

These checks verify the extension on the three integrations above. Other
integrations still need sequential isolated-agent support to run the command.

## Subagent-Capable Agents

The command requires subagents or isolated worker contexts. It launches one
context-isolated stage agent at a time while sharing repository state:

1. Read-only regression baseline before phase mutations.
2. Test, skipped when empty.
3. Implementation, skipped when empty.
4. Read-only verification, always run.
5. Conditional remediation and fresh read-only re-verification after every
   remediation result, capped at two cycles.
6. Documentation after a phase-safe final verdict.

Each later agent gets only a compact structured handoff: phase/task IDs,
relevant paths, regression-baseline and current validation summaries, deferred
findings, expected failures, prior SHA/manifest, and scope. Keep
remediation-cycle state in the parent context and do not pass full traces.

Workers must not stage, commit, push, spawn workers, run the phase orchestrator,
or continue to another phase. The parent owns baselines, manifest review,
exact-path staging, commits, remediation-cycle control, and continuation.

Every worker report always includes `stage`, `phase_number`, `status`,
`changed_paths`, `validation`, and `commit_eligible`. Expected failures,
findings, and caveats may be empty or omitted. Non-empty findings use typed
classification, disposition, attribution, comparison, and downstream-safety
fields. This lightweight report contract remains separate from the JSON schema
used for parent-to-worker handoffs.

Parent-only model and effort settings, fallback model-selection text, and
orchestration instructions should stay with the parent. They are configuration
for creating the worker, not phase work. Before building handoffs, the parent
inspects the skills and MCP servers exposed by its integration. The worker
prompt includes only sanitized phase instructions, applicable user-requested
skills, automatically selected frontend/backend capabilities, MCP opt-outs,
and concise reference summaries.

Only the documentation agent receives the phase-document and Mermaid
instructions. The test agent is test-only and may produce eligible intentional
RED changes solely when missing assigned implementation explains the failure.
The implementation agent runs the complete focused phase-test gate and reports
typed unresolved findings when it cannot reach green. Implementation and
remediation workers do not make final blocker decisions. A fresh verifier
classifies findings as remediable, deferrable, or blocking and reruns exact
baseline regression commands. A test-authoring-only phase may satisfy its
contract with attributable expected RED. Implementation and remediation stay
uncommitted until phase-safe verification. Verifiers are strictly read-only.

Only a demonstrably pre-existing, unrelated, unchanged regression with passing
focused and independent-phase gates and proven downstream safety may be
deferred. A phase-introduced regression first receives in-scope remediation;
uncertain attribution or required cross-phase changes stop the queue.

In `all` mode, the parent owns the queue. It completes every stage gate and
confirms the durable workflow-complete documentation marker before starting
the next phase. Keep `all` mode, queue management, Git actions, worker-spawn
instructions, and full earlier traces out of worker prompts.

Explicit user MCP opt-outs take precedence over capability defaults. A global
opt-out disables every MCP; a provider-specific opt-out excludes only that
provider. The parent propagates applicable exclusions to every worker.

When web search is needed, both the parent and workers use Exa first when it is
available and not excluded. If Exa is unavailable or fails, they may use
another available web-search tool and report the fallback. This preference does
not require web search for work that can be completed from repository context.

For database-related work, the responsible agent identifies the project's
database from the selected tasks and repository context, looks for an exposed
related database MCP, and uses it when available and not excluded. The workflow
does not hardcode a database provider and does not stop when no related MCP is
available; it continues with suitable project tools. Frontend and backend
skills and MCPs are selected automatically from the task scope, relevant paths,
and detected project stack, then routed only to stages that need them.

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

Commits are parent-owned by default. Before each stage, record HEAD and the
working-tree baseline. Test work may retain its eligible stage commit, but
implementation and remediation manifests remain unstaged until phase-safe
verification. Then stage their exact accumulated path union once and select
`feat`, `fix`, or `chore` from the task intent. Commit bodies record task IDs,
files, baseline comparison, validation, remediation, deferred and expected
failures when applicable, and prior SHA. Baseline/verifier workers never commit.

If the user includes `--no-commit` or clearly says not to commit, all stages
and gates still run. The parent tracks per-stage manifests but suppresses every
staging and commit operation, leaving accumulated reviewed changes unstaged. The
orchestrator never pushes.

## Documentation Paths

When no custom documentation location is provided, use the parser-generated
path under `Documentation/{feature-slug}/`. Preserve `--docs-dir`, and use an
explicit user-provided Markdown path exactly. The final document aggregates
stage reports, SHAs, manifests, regression attribution, deferred findings,
validation, remediation history, and the durable workflow-complete marker.

## Agent Requirements

Codex is not required.

Claude Code is not required.

Any agent integration that can execute the Spec Kit command prompt and run the
supporting parser can use the workflow. Agents without a Python runtime can
still follow the command text manually, but the packaged parser requires
Python 3.10 or newer.
