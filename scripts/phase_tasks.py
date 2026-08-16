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
TITLE_RE = re.compile(r"^#\s+Tasks:\s+(.+?)\s*$")
SUBHEADING_RE = re.compile(r"^###\s+(.+?)\s*$")
TASK_RE = re.compile(r"^- \[(?P<mark>[ xX])\]\s+(?P<id>T\d+)\s*(?P<body>.*)$")
PURPOSE_RE = re.compile(r"^\*\*Purpose\*\*:\s*(.+?)\s*$")
CHECKPOINT_RE = re.compile(r"^\*\*Checkpoint\*\*:\s*(.+?)\s*$")
INDEPENDENT_TEST_RE = re.compile(r"^\*\*Independent Test\*\*:\s*(.+?)\s*$")
TEST_SECTION_RE = re.compile(r"^tests(?:\s+first|\s+for\s+phase\s+\d+)?$", re.I)
TEST_FILE_RE = re.compile(r"(^|[/`])(?:test_[^/`\s]+|[^/`\s]+\.(?:test|spec)\.[^/`\s]+)")
HELPER_SETUP_RE = re.compile(
    r"\b(?:fixtures?|fakes?|helpers?|mocks?|stubs?|setup|utilities?|utils?|"
    r"factories|factory|builders?|scaffolding)\b",
    re.I,
)
EXPLICIT_TEST_ACTION_RE = re.compile(
    r"\b(?:add|create|write|implement|extend|update|run|execute|fix|verify)\b"
    r".*\b(?:unit|integration|e2e|end-to-end|regression|acceptance|"
    r"accessibility|a11y|contract)?\s*tests?\b",
    re.I,
)
TEST_NOUN_RE = re.compile(r"\b(?:test|spec)\s+(?:file|case|suite|coverage|run|command)\b", re.I)
WORKFLOW_COMPLETE_MARKER = "<!-- phase-orchestrator:workflow-complete v2 -->"


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
    section = task.section.strip()
    text = task.text

    if TEST_SECTION_RE.match(section):
        return True

    if TEST_FILE_RE.search(text):
        return True

    if HELPER_SETUP_RE.search(text):
        return False

    if EXPLICIT_TEST_ACTION_RE.search(text) or TEST_NOUN_RE.search(text):
        return True

    return False


def infer_feature_slug(path: Path, feature_title: str | None) -> str:
    if path.name == "tasks.md" and path.parent.name:
        parent_slug = re.sub(r"^\d+-", "", path.parent.name)
        if parent_slug and parent_slug not in {".", "specs"}:
            return slugify(parent_slug)

    if feature_title:
        return slugify(feature_title)

    return slugify(path.stem)


def phase_documentation_path(
    phase: Phase,
    docs_dir: Path | None,
    feature_slug: str,
    explicit_path: Path | None = None,
) -> str:
    if explicit_path is not None:
        return explicit_path.as_posix()
    base_dir = docs_dir if docs_dir is not None else Path("Documentation") / feature_slug
    stem = f"phase-{phase.number}-{phase.slug}"
    return (base_dir / f"{stem}-execution.md").as_posix()


def parse_tasks(path: Path) -> tuple[list[Phase], str | None]:
    phases: list[Phase] = []
    current: Phase | None = None
    section = "General"
    seen_numbers: set[int] = set()
    feature_title: str | None = None

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise ValueError(f"tasks.md is not valid UTF-8: {path}") from exc

    for lineno, line in enumerate(lines, 1):
        title_match = TITLE_RE.match(line)
        if title_match and feature_title is None:
            feature_title = title_match.group(1).strip()
            continue

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

    return phases, feature_title


def task_to_dict(task: Task) -> dict[str, Any]:
    return asdict(task)


def phase_to_dict(
    phase: Phase,
    docs_dir: Path | None = None,
    feature_slug: str = "feature",
    explicit_docs_path: Path | None = None,
) -> dict[str, Any]:
    incomplete = phase.incomplete
    test_tasks = [task for task in incomplete if is_test_task(task)]
    implementation_tasks = [task for task in incomplete if task not in test_tasks]
    documentation_path = phase_documentation_path(
        phase, docs_dir, feature_slug, explicit_docs_path
    )
    documentation_file = Path(documentation_path)
    documentation_complete = False
    if documentation_file.is_file():
        try:
            documentation_complete = WORKFLOW_COMPLETE_MARKER in documentation_file.read_text(
                encoding="utf-8"
            )
        except (OSError, UnicodeDecodeError):
            documentation_complete = False
    # An empty phase has no pending task work, so it can advance directly to
    # mandatory verification and documentation.
    task_complete = not incomplete
    workflow_complete = task_complete and documentation_complete

    if workflow_complete:
        next_stage = None
    elif test_tasks:
        next_stage = "test"
    elif implementation_tasks:
        next_stage = "implementation"
    else:
        next_stage = "verification"

    return {
        "number": phase.number,
        "title": phase.title,
        "slug": phase.slug,
        "documentation_path": documentation_path,
        "purpose": phase.purpose,
        "checkpoint": phase.checkpoint,
        "independent_test": phase.independent_test,
        "complete": phase.complete,
        "task_complete": task_complete,
        "documentation_complete": documentation_complete,
        "workflow_complete": workflow_complete,
        "next_stage": next_stage,
        "incomplete_task_ids": [task.id for task in incomplete],
        "counts": {
            "total": len(phase.tasks),
            "completed": len([task for task in phase.tasks if task.completed]),
            "incomplete": len(incomplete),
            "test_tasks": len(test_tasks),
            "implementation_tasks": len(implementation_tasks),
        },
        "test_tasks": [task_to_dict(task) for task in test_tasks],
        "tests_first_tasks": [task_to_dict(task) for task in test_tasks],
        "implementation_tasks": [
            task_to_dict(task) for task in implementation_tasks
        ],
        "incomplete_tasks": [task_to_dict(task) for task in incomplete],
    }


def select_phases(
    phases: list[Phase],
    mode: str,
    phase_number: int | None,
    docs_dir: Path | None = None,
    feature_slug: str = "feature",
    explicit_docs_path: Path | None = None,
) -> list[Phase]:
    incomplete = [
        phase
        for phase in phases
        if not phase_to_dict(
            phase,
            docs_dir,
            feature_slug,
            explicit_docs_path if phase_number == phase.number else None,
        )["workflow_complete"]
    ]

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


def build_output(
    path: Path,
    mode: str,
    phase_number: int | None,
    docs_dir: Path | None = None,
    explicit_docs_path: Path | None = None,
) -> dict[str, Any]:
    phases, feature_title = parse_tasks(path)
    feature_slug = infer_feature_slug(path, feature_title)
    selected = select_phases(
        phases,
        mode,
        phase_number,
        docs_dir,
        feature_slug,
        explicit_docs_path,
    )
    selected_phase = selected[0] if selected else None
    phase_outputs = [
        phase_to_dict(
            phase,
            docs_dir,
            feature_slug,
            explicit_docs_path if phase_number == phase.number else None,
        )
        for phase in phases
    ]
    incomplete_phases = [phase for phase in phase_outputs if not phase["workflow_complete"]]
    task_complete_phases = [phase for phase in phase_outputs if phase["task_complete"]]
    workflow_complete_phases = [phase for phase in phase_outputs if phase["workflow_complete"]]

    return {
        "tasks_path": str(path),
        "feature_slug": feature_slug,
        "docs_dir": docs_dir.as_posix() if docs_dir is not None else None,
        "explicit_docs_path": (
            explicit_docs_path.as_posix() if explicit_docs_path is not None else None
        ),
        "mode": "phase" if phase_number is not None else mode,
        "requested_phase": phase_number,
        "phase_count": len(phases),
        "complete_phase_count": len(workflow_complete_phases),
        "task_complete_phase_count": len(task_complete_phases),
        "workflow_complete_phase_count": len(workflow_complete_phases),
        "incomplete_phase_count": len(incomplete_phases),
        "remaining_phase_count": len(incomplete_phases),
        "selected_phase": (
            phase_to_dict(
                selected_phase,
                docs_dir,
                feature_slug,
                explicit_docs_path if phase_number is not None else None,
            )
            if selected_phase
            else None
        ),
        "selected_phases": [
            phase_to_dict(
                phase,
                docs_dir,
                feature_slug,
                explicit_docs_path if phase_number == phase.number else None,
            )
            for phase in selected
        ],
        "all_phases": [
            {
                "number": phase["number"],
                "title": phase["title"],
                "slug": phase["slug"],
                "complete": phase["workflow_complete"],
                "task_complete": phase["task_complete"],
                "documentation_complete": phase["documentation_complete"],
                "workflow_complete": phase["workflow_complete"],
                "next_stage": phase["next_stage"],
                "total": phase["counts"]["total"],
                "completed": phase["counts"]["completed"],
                "incomplete": phase["counts"]["incomplete"],
            }
            for phase in phase_outputs
        ],
    }


def print_text_summary(output: dict[str, Any]) -> None:
    selected = output["selected_phase"]
    if selected is None:
        print("No incomplete phase workflows found.")
        return

    print(f"Tasks: {output['tasks_path']}")
    print(f"Mode: {output['mode']}")
    print(f"Selected: Phase {selected['number']}: {selected['title']}")
    print(f"Incomplete tasks: {', '.join(selected['incomplete_task_ids'])}")
    print(f"Next stage: {selected['next_stage'] or 'none'}")
    print(f"Remaining incomplete workflows: {output['remaining_phase_count']}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parse a Spec Kit tasks.md file into phase execution units."
    )
    parser.add_argument("tasks_path", type=Path)
    parser.add_argument("--mode", choices=["next", "all"], default="next")
    parser.add_argument("--phase", type=int)
    parser.add_argument(
        "--docs-dir",
        type=Path,
        help=(
            "Directory for generated Markdown phase documentation. "
            "Defaults to Documentation/{feature-slug}/."
        ),
    )
    parser.add_argument(
        "--docs-path",
        type=Path,
        help="Exact Markdown phase-document path. Requires --phase.",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    if args.phase is not None and args.phase < 1:
        parser.error("--phase must be a positive integer")
    if args.phase is not None and args.mode != "next":
        parser.error("--phase cannot be combined with --mode")
    if args.docs_path is not None and args.phase is None:
        parser.error("--docs-path requires --phase")
    if args.docs_path is not None and args.docs_dir is not None:
        parser.error("--docs-path cannot be combined with --docs-dir")

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
        output = build_output(
            tasks_path,
            args.mode,
            args.phase,
            args.docs_dir,
            args.docs_path,
        )
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
