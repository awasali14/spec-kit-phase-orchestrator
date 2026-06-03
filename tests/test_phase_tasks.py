from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import phase_tasks


SAMPLE_TASKS = ROOT / "examples" / "sample-tasks.md"
SCRIPT = ROOT / "scripts" / "phase_tasks.py"


class PhaseTasksParserTest(unittest.TestCase):
    def test_selects_next_incomplete_phase(self) -> None:
        output = phase_tasks.build_output(SAMPLE_TASKS, "next", None)

        self.assertEqual(output["selected_phase"]["number"], 1)
        self.assertEqual(output["selected_phase"]["incomplete_task_ids"], ["T003"])

    def test_selects_explicit_phase_three(self) -> None:
        output = phase_tasks.build_output(SAMPLE_TASKS, "next", 3)

        self.assertEqual(output["mode"], "phase")
        self.assertEqual(output["requested_phase"], 3)
        self.assertEqual(output["selected_phase"]["number"], 3)
        self.assertEqual(
            output["selected_phase"]["incomplete_task_ids"],
            ["T007", "T008", "T009", "T010", "T011"],
        )

    def test_returns_all_incomplete_phases(self) -> None:
        output = phase_tasks.build_output(SAMPLE_TASKS, "all", None)

        self.assertEqual([phase["number"] for phase in output["selected_phases"]], [1, 2, 3, 4, 5, 6])
        self.assertEqual(output["incomplete_phase_count"], 6)

    def test_preserves_task_ids(self) -> None:
        output = phase_tasks.build_output(SAMPLE_TASKS, "phase", 5)

        self.assertEqual(
            output["selected_phase"]["incomplete_task_ids"],
            ["T017", "T018", "T019", "T020", "T021"],
        )

    def test_separates_test_tasks_from_implementation_tasks(self) -> None:
        output = phase_tasks.build_output(SAMPLE_TASKS, "next", 3)
        selected = output["selected_phase"]

        self.assertEqual([task["id"] for task in selected["test_tasks"]], ["T007", "T008"])
        self.assertEqual(
            [task["id"] for task in selected["implementation_tasks"]],
            ["T009", "T010", "T011"],
        )

    def test_handles_six_or_more_phases(self) -> None:
        output = phase_tasks.build_output(SAMPLE_TASKS, "all", None)

        self.assertGreaterEqual(output["phase_count"], 6)

    def test_returns_no_incomplete_phase_when_all_tasks_are_complete(self) -> None:
        completed_content = SAMPLE_TASKS.read_text(encoding="utf-8").replace("- [ ]", "- [X]")

        with tempfile.TemporaryDirectory() as temp_dir:
            tasks_path = Path(temp_dir) / "tasks.md"
            tasks_path.write_text(completed_content, encoding="utf-8")
            output = phase_tasks.build_output(tasks_path, "next", None)

        self.assertIsNone(output["selected_phase"])
        self.assertEqual(output["selected_phases"], [])
        self.assertEqual(output["incomplete_phase_count"], 0)
        self.assertEqual(output["complete_phase_count"], 6)

    def test_fails_clearly_for_missing_file(self) -> None:
        missing = ROOT / "examples" / "missing-tasks.md"

        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(missing), "--json"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("tasks.md not found", result.stderr)

    def test_fails_clearly_for_missing_phase_number(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(SAMPLE_TASKS), "--phase", "99", "--json"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("phase 99 was not found", result.stderr)


if __name__ == "__main__":
    unittest.main()
