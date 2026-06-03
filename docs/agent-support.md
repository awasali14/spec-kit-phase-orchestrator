# Agent Support

Spec Kit Phase Orchestrator is a Spec Kit extension command, not a Codex-only
skill. The command wording is portable so Spec Kit can render it through
supported integrations.

## Subagent-Capable Agents

When the active coding agent supports subagents or isolated worker contexts,
the command should use exactly one worker for the selected phase. That worker
gets a compact handoff with the phase number, title, incomplete tasks, scope
rules, validation expectations, and documentation requirements.

The worker should not stage, commit, spawn more workers, or continue to another
phase. The parent context owns review and continuation.

## Local Fallback

When subagents are unavailable, the same phase-scoped workflow runs in the
current agent conversation. The boundaries remain the same:

1. Select one phase.
2. Work only on that phase.
3. Validate.
4. Write documentation and a receipt.
5. Stop unless `all` mode is active and the phase completed cleanly.

## Agent Requirements

Codex is not required.

Claude Code is not required.

Any agent integration that can execute the Spec Kit command prompt and run the
supporting parser can use the workflow. Agents without a Python runtime can
still follow the command text manually, but the packaged parser requires
Python 3.9 or newer.
