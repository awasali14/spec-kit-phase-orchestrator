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
relevant paths, regression-baseline and prior validation summaries, stage
validation expectations, deferred findings, expected failures, prior
SHA/manifest, scope, and a stage-locked report contract. The handoff includes
the applicable form from `schemas/phase-report.schema.json`; current-stage
results and verdicts come only from the completed worker report. Keep
remediation-cycle and commit-control state in the parent
context. Keep selector mode, phase-lifecycle state, and queue/continuation
metadata there as well; do not pass full traces.

Workers must not stage, commit, push, spawn workers, run the phase orchestrator,
or continue to another phase. The parent owns baselines, manifest review,
exact-path staging, commits, remediation-cycle control, and continuation.

Every worker report conforms to `schemas/phase-report.schema.json` and includes
the complete stage form, including empty arrays. The parent validates schema,
stage, phase, task IDs, evidence, remediation IDs, and changed paths, then
cross-checks the observed manifest before trusting the result. This validation
does not replace fresh technical verification.

Non-verifier findings keep `disposition: null` when routed into a fresh
verification handoff. The parent must not invent a transition decision during
that handoff. Remediation receives only verifier-classified findings with a
non-null `remediate`, `defer`, or `block` disposition.

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
contract with attributable expected RED. Eligible implementation and
remediation stages become separate parent-owned progress commits before their
fresh verifier runs. Verifiers are strictly read-only.

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
working-tree baseline. Test work retains its eligible stage commit.
Implementation commits its exact stage paths immediately after a schema-valid,
scope-clean `passed` or `unresolved` result using `feat`, `fix`, or `chore` from
task intent. Each eligible remediation cycle uses a separate
`fix(scope): remediate phase N findings` commit. Commit bodies record stage
status, task or finding IDs, files, validation, and prior SHA.
Baseline/verifier workers never commit; documentation commits only after final
verification and parser completion.

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
