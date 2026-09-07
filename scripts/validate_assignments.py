#!/usr/bin/env python3
"""Validate parent-owned task assignments; never infer a task's role."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__:
    from . import phase_tasks
else:
    import phase_tasks


def validate_assignments(output: dict, manifest: dict) -> dict:
    phase = output["selected_phase"]
    if not isinstance(manifest, dict) or phase is None:
        raise ValueError("expected an assignment object and an explicit selected phase")
    if manifest.get("schema_version") != "1.0.0":
        raise ValueError("assignment schema_version must be 1.0.0")
    if type(manifest.get("phase_number")) is not int or manifest["phase_number"] != phase["number"]:
        raise ValueError("assignment phase_number does not match selected phase")
    if manifest.get("inventory_digest") != output["inventory_digest"]:
        raise ValueError("task source changed; parent must review and revise assignments")
    if type(manifest.get("revision")) is not int or manifest["revision"] < 1:
        raise ValueError("revision must be a positive integer")
    if not isinstance(manifest.get("reason"), str) or not manifest["reason"].strip():
        raise ValueError("assignment revision requires a reason")
    entries = manifest.get("assignments")
    if not isinstance(entries, list):
        raise ValueError("assignments must be an array")
    by_id = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("each assignment must be an object")
        task_id = entry.get("id")
        if not isinstance(task_id, str) or task_id in by_id:
            raise ValueError("invalid or duplicate assignment ID")
        if entry.get("stage") not in ("test", "implementation"):
            raise ValueError(f"invalid stage for {task_id}")
        if not isinstance(entry.get("rationale"), str) or not entry["rationale"].strip():
            raise ValueError(f"missing deliverable rationale for {task_id}")
        by_id[task_id] = entry
    expected = {task["id"] for task in phase["tasks"]}
    if set(by_id) != expected:
        raise ValueError(f"assignment coverage mismatch: missing={sorted(expected - set(by_id))}, "
                         f"unknown={sorted(set(by_id) - expected)}")
    groups = {
        stage + "_tasks": [task for task in phase["incomplete_tasks"]
                           if by_id[task["id"]]["stage"] == stage]
        for stage in ("test", "implementation")
    }
    next_stage = ("test" if groups["test_tasks"] else
                  "implementation" if groups["implementation_tasks"] else
                  None if phase["workflow_complete"] else "verification")
    return {"phase_number": phase["number"], "revision": manifest["revision"],
            "next_stage": next_stage, **groups}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tasks_path", type=Path)
    parser.add_argument("assignments_path", type=Path)
    parser.add_argument("--phase", type=int, required=True)
    docs = parser.add_mutually_exclusive_group()
    docs.add_argument("--docs-dir", type=Path)
    docs.add_argument("--docs-path", type=Path)
    args = parser.parse_args(argv)
    try:
        output = phase_tasks.build_output(args.tasks_path, "next", args.phase,
                                         args.docs_dir, args.docs_path)
        manifest = json.loads(args.assignments_path.read_text(encoding="utf-8"))
        print(json.dumps(validate_assignments(output, manifest), indent=2))
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
