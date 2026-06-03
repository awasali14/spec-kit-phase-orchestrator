#!/usr/bin/env python3
"""Parse a Spec Kit tasks.md file into phase execution units."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


PHASE_RE = re.compile(r"^##\s+Phase\s+(\d+):\s+(.+?)\s*$")
SUBHEADING_RE = re.compile(r"^###\s+(.+?)\s*$")
TASK_RE = re.compile(r"^- \[(?P<mark>[ xX])\]\s+(?P<id>T\d+)\s*(?P<body>.*)$")
PURPOSE_RE = re.compile(r"^\*\*Purpose\*\*:\s*(.+?)\s*$")
CHECKPOINT_RE = re.compile(r"^\*\*Checkpoint\*\*:\s*(.+?)\s*$")
INDEPENDENT_TEST_RE = re.compile(r"^\*\*Independent Test\*\*:\s*(.+?)\s*$")


@dataclass(frozen=True)
class Task:
    id: str
    text: str
    completed: bool
    parallel: bool
    story: str | None
    section: str
    line: int


@dataclass
class Phase:
    number: int
    title: str
    slug: str
    purpose: str | None = None
    checkpoint: str | None = None
    independent_test: str | None = None
    tasks: list[Task] = field(default_factory=list)

    @property
    def incomplete(self) -> list[Task]:
        return [task for task in self.tasks if not task.completed]

    @property
    def complete(self) -> bool:
        return bool(self.tasks) and not self.incomplete


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "phase"


def parse_story(body: str) -> str | None:
    match = re.search(r"\[(US\d+)\]", body)
    return match.group(1) if match else None


def is_test_task(task: Task) -> bool:
    section = task.section.lower()
    text = task.text.lower()
    if section in {"tests first", "tests"} or section.startswith("tests "):
        return True
    if re.search(r"\btests?\b", section):
        return True
    if re.search(r"\btest(s|ing)?\b", text):
        return True
    if "test_" in text or ".test." in text or ".spec." in text:
        return True
    return False


def parse_tasks(path: Path) -> list[Phase]:
    phases: list[Phase] = []
    current: Phase | None = None
    section = "General"
    seen_numbers: set[int] = set()

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise ValueError(f"tasks.md is not valid UTF-8: {path}") from exc

    for lineno, line in enumerate(lines, 1):
        phase_match = PHASE_RE.match(line)
        if phase_match:
            number = int(phase_match.group(1))
            if number in seen_numbers:
                raise ValueError(f"duplicate Phase {number} at line {lineno}")
            seen_numbers.add(number)
            current = Phase(
                number=number,
                title=phase_match.group(2).strip(),
                slug=slugify(phase_match.group(2)),
            )
            phases.append(current)
            section = "General"
            continue

        if current is None:
            continue

        subheading_match = SUBHEADING_RE.match(line)
        if subheading_match:
            section = subheading_match.group(1).strip()
            continue

        purpose_match = PURPOSE_RE.match(line)
        if purpose_match:
            current.purpose = purpose_match.group(1).strip()
            continue

        checkpoint_match = CHECKPOINT_RE.match(line)
        if checkpoint_match:
            current.checkpoint = checkpoint_match.group(1).strip()
            continue

        independent_test_match = INDEPENDENT_TEST_RE.match(line)
        if independent_test_match:
            current.independent_test = independent_test_match.group(1).strip()
            continue

        task_match = TASK_RE.match(line)
        if not task_match:
            continue

        body = task_match.group("body").strip()
        current.tasks.append(
            Task(
                id=task_match.group("id"),
                text=body,
                completed=task_match.group("mark").lower() == "x",
                parallel="[P]" in body,
                story=parse_story(body),
                section=section,
                line=lineno,
            )
        )

    if not phases:
        raise ValueError(f"no Spec Kit phase headings found in {path}")

    return phases


def task_to_dict(task: Task) -> dict[str, Any]:
    return asdict(task)


def phase_to_dict(phase: Phase) -> dict[str, Any]:
    incomplete = phase.incomplete
    test_tasks = [task for task in incomplete if is_test_task(task)]
    implementation_tasks = [task for task in incomplete if task not in test_tasks]

    return {
        "number": phase.number,
        "title": phase.title,
        "slug": phase.slug,
        "purpose": phase.purpose,
        "checkpoint": phase.checkpoint,
        "independent_test": phase.independent_test,
        "complete": phase.complete,
        "incomplete_task_ids": [task.id for task in incomplete],
        "counts": {
            "total": len(phase.tasks),
            "completed": len([task for task in phase.tasks if task.completed]),
            "incomplete": len(incomplete),
            "test_tasks": len(test_tasks),
            "implementation_tasks": len(implementation_tasks),
        },
        "test_tasks": [task_to_dict(task) for task in test_tasks],
        "implementation_tasks": [
            task_to_dict(task) for task in implementation_tasks
        ],
        "incomplete_tasks": [task_to_dict(task) for task in incomplete],
    }


def select_phases(
    phases: list[Phase], mode: str, phase_number: int | None
) -> list[Phase]:
    incomplete = [phase for phase in phases if phase.incomplete]

    if phase_number is not None:
        selected = [phase for phase in phases if phase.number == phase_number]
        if not selected:
            raise ValueError(f"phase {phase_number} was not found")
        return selected

    if mode == "all":
        return incomplete

    if mode == "next":
        return incomplete[:1]

    raise ValueError(f"unsupported mode: {mode}")


def build_output(path: Path, mode: str, phase_number: int | None) -> dict[str, Any]:
    phases = parse_tasks(path)
    selected = select_phases(phases, mode, phase_number)
    selected_phase = selected[0] if selected else None
    incomplete_phases = [phase for phase in phases if phase.incomplete]

    return {
        "tasks_path": str(path),
        "mode": "phase" if phase_number is not None else mode,
        "requested_phase": phase_number,
        "phase_count": len(phases),
        "complete_phase_count": len([phase for phase in phases if phase.complete]),
        "incomplete_phase_count": len(incomplete_phases),
        "remaining_phase_count": len(incomplete_phases),
        "selected_phase": phase_to_dict(selected_phase) if selected_phase else None,
        "selected_phases": [phase_to_dict(phase) for phase in selected],
        "all_phases": [
            {
                "number": phase.number,
                "title": phase.title,
                "slug": phase.slug,
                "complete": phase.complete,
                "total": len(phase.tasks),
                "completed": len([task for task in phase.tasks if task.completed]),
                "incomplete": len(phase.incomplete),
            }
            for phase in phases
        ],
    }


def print_text_summary(output: dict[str, Any]) -> None:
    selected = output["selected_phase"]
    if selected is None:
        print("No incomplete phases found.")
        return

    print(f"Tasks: {output['tasks_path']}")
    print(f"Mode: {output['mode']}")
    print(f"Selected: Phase {selected['number']}: {selected['title']}")
    print(f"Incomplete tasks: {', '.join(selected['incomplete_task_ids'])}")
    print(f"Remaining incomplete phases: {output['remaining_phase_count']}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parse a Spec Kit tasks.md file into phase execution units."
    )
    parser.add_argument("tasks_path", type=Path)
    parser.add_argument("--mode", choices=["next", "all"], default="next")
    parser.add_argument("--phase", type=int)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    if args.phase is not None and args.phase < 1:
        parser.error("--phase must be a positive integer")
    if args.phase is not None and args.mode != "next":
        parser.error("--phase cannot be combined with --mode")

    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    tasks_path = args.tasks_path

    if not tasks_path.exists():
        print(f"tasks.md not found: {tasks_path}", file=sys.stderr)
        return 2

    if not tasks_path.is_file():
        print(f"tasks.md path is not a file: {tasks_path}", file=sys.stderr)
        return 2

    try:
        output = build_output(tasks_path, args.mode, args.phase)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.as_json:
        print(json.dumps(output, indent=2))
    else:
        print_text_summary(output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
