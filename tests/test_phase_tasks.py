from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import phase_tasks


SAMPLE_TASKS = ROOT / "examples" / "sample-tasks.md"
FIVE_PHASE_TASKS = ROOT / "examples" / "five-phase-tasks.md"
SCRIPT = ROOT / "scripts" / "phase_tasks.py"
MERMAID_STYLE = ROOT / "references" / "mermaid-style.md"
PHASE_DOC_TEMPLATE = ROOT / "references" / "phase-doc-template.md"
WORKER_PROMPT_TEMPLATE = ROOT / "references" / "worker-prompt-template.md"
COMMAND_FILE = ROOT / "commands" / "speckit.phase-orchestrator.phase.md"
EXTENSION_FILE = ROOT / "extension.yml"
AGENT_SUPPORT = ROOT / "docs" / "agent-support.md"
USAGE = ROOT / "docs" / "usage.md"
HANDOFF_SCHEMA = ROOT / "schemas" / "phase-handoff.schema.json"
REPORT_SCHEMA = ROOT / "schemas" / "phase-report.schema.json"
HANDOFF_SAMPLE = ROOT / "examples" / "sample-phase-handoff.json"
CHANGELOG = ROOT / "CHANGELOG.md"
EXTENSION_IGNORE = ROOT / ".extensionignore"
ISSUES_TRACKER = ROOT / "issues-tracker.md"
PUBLICATION_PLAN = ROOT / "speckit-phase-orchestrator-extension-publication-plan.md"
SUBMISSION_NOTES = ROOT / "docs" / "submission-notes.md"
WORKFLOW_MARKER = "<!-- phase-orchestrator:workflow-complete v2 -->"


def style_lines(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip().startswith(("classDef ", "linkStyle "))
    ]


def section(text: str, heading: str) -> str:
    start = text.index(f"## {heading}")
    remainder = text[start + len(f"## {heading}") :]
    next_heading = remainder.find("\n## ")
    return remainder if next_heading == -1 else remainder[:next_heading]


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def assert_schema_valid(test: unittest.TestCase, instance: dict) -> None:
    schema = json.loads(HANDOFF_SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(instance), key=str)
    test.assertEqual(errors, [], "\n".join(error.message for error in errors))


def set_handoff_stage(handoff: dict, stage: str) -> None:
    handoff["stage"] = stage
    handoff["report_contract"]["stage"] = stage


def report_validator() -> Draft202012Validator:
    return Draft202012Validator(json.loads(REPORT_SCHEMA.read_text(encoding="utf-8")))


def base_report(stage: str, status: str = "passed") -> dict:
    report = {
        "schema_version": "2.0.0",
        "stage": stage,
        "phase_number": 3,
        "assigned_task_ids": [],
        "status": status,
        "changed_paths": [],
        "validation": [],
        "regression_evidence": [],
        "expected_failures": [],
        "findings": [],
        "remediation_results": [],
        "caveats": [],
    }
    if stage == "baseline_verification":
        report["status"] = "baseline_recorded"
        report["validation"] = [
            {"kind": "regression", "command": "pytest", "status": "passed", "summary": "Baseline passed."}
        ]
        report["regression_evidence"] = [comparison_evidence("passed")]
    elif stage in {"test", "implementation"}:
        report["assigned_task_ids"] = ["T007"]
        report["validation"] = [
            {"kind": "focused", "command": "pytest focused", "status": "passed", "summary": "Focused gate passed."}
        ]
    elif stage == "verification":
        report["validation"] = [
            {"kind": "focused", "command": "pytest focused", "status": "passed", "summary": "Focused gate passed."},
            {"kind": "independent_phase", "command": "pytest phase", "status": "passed", "summary": "Phase gate passed."},
            {"kind": "regression", "command": "pytest", "status": "passed", "summary": "Regression gate passed."},
        ]
        report["regression_evidence"] = [comparison_evidence("passed")]
    elif stage == "remediation":
        report["validation"] = [
            {"kind": "focused", "command": "pytest focused", "status": "passed", "summary": "Focused gate passed."}
        ]
        report["remediation_results"] = [
            {"finding_id": "F1", "status": "resolved", "summary": "Finding resolved."}
        ]
    elif stage == "documentation":
        report["validation"] = [
            {"kind": "documentation", "command": "document inspection", "status": "passed", "summary": "Document valid."},
            {"kind": "parser", "command": "phase parser", "status": "passed", "summary": "Workflow complete."},
        ]
    return report


def comparison_evidence(status: str = "failed") -> dict:
    return {
        "command": "pytest",
        "environment_fingerprint": "python-3.12; pytest",
        "status": status,
        "failing_tests": [] if status == "passed" else ["legacy test"],
        "failure_signatures": [] if status == "passed" else ["legacy assertion"],
    }


def report_finding(disposition: str | None = None) -> dict:
    evidence = comparison_evidence("failed")
    return {
        "id": "F1",
        "kind": "phase_scoped_failure",
        "gate": "focused",
        "disposition": disposition,
        "attribution": "phase_introduced",
        "confidence": "confirmed",
        "summary": "Focused validation failed.",
        "related_task_ids": ["T007"],
        "affected_paths": ["src/example.py"],
        "baseline_evidence": None,
        "current_evidence": evidence,
        "downstream_safe": None,
    }


def completed_tasks_fixture() -> str:
    return SAMPLE_TASKS.read_text(encoding="utf-8").replace("- [ ]", "- [X]")


def write_workflow_document(path: Path, marker: str = WORKFLOW_MARKER) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# Execution\n\nFinal verification: passed\n\n{marker}\n", encoding="utf-8")


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

    def test_range_from_phase_one_requires_no_predecessor(self) -> None:
        output = phase_tasks.build_output(
            SAMPLE_TASKS, "next", 1, through_phase=6
        )

        self.assertEqual(output["mode"], "range")
        self.assertEqual(output["frozen_phase_numbers"], [1, 2, 3, 4, 5, 6])
        self.assertEqual(
            [phase["number"] for phase in output["selected_phases"]],
            [1, 2, 3, 4, 5, 6],
        )

    def test_range_accepts_checked_predecessor_without_documentation(self) -> None:
        content = SAMPLE_TASKS.read_text(encoding="utf-8").replace(
            "- [ ] T007", "- [X] T007"
        ).replace(
            "- [ ] T008", "- [X] T008"
        ).replace(
            "- [ ] T009", "- [X] T009"
        ).replace(
            "- [ ] T010", "- [X] T010"
        ).replace(
            "- [ ] T011", "- [X] T011"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            tasks_path = Path(temp_dir) / "tasks.md"
            tasks_path.write_text(content, encoding="utf-8")
            output = phase_tasks.build_output(
                tasks_path, "next", 4, through_phase=6
            )

        self.assertEqual(output["frozen_phase_numbers"], [4, 5, 6])
        self.assertEqual(
            [phase["number"] for phase in output["selected_phases"]], [4, 5, 6]
        )
        phase_three = next(
            phase for phase in output["all_phases"] if phase["number"] == 3
        )
        self.assertTrue(phase_three["task_complete"])
        self.assertFalse(phase_three["documentation_complete"])

    def test_range_rejects_unchecked_predecessor(self) -> None:
        with self.assertRaisesRegex(
            ValueError, r"prerequisite phase 3 has unchecked tasks"
        ):
            phase_tasks.build_output(SAMPLE_TASKS, "next", 4, through_phase=6)

    def test_range_skips_workflow_complete_phase_but_resumes_checked_undocumented_phase(
        self,
    ) -> None:
        content = """# Tasks: Range Completion

## Phase 1: Prerequisite
- [X] T001 Complete prerequisite in `src/one.py`

## Phase 2: Documented
- [X] T002 Complete documented work in `src/two.py`

## Phase 3: Undocumented
- [X] T003 Complete undocumented work in `src/three.py`

## Phase 4: Pending
- [ ] T004 Add pending work in `src/four.py`
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            tasks_path = root / "tasks.md"
            docs_dir = root / "docs"
            tasks_path.write_text(content, encoding="utf-8")
            phase_two = phase_tasks.build_output(
                tasks_path, "next", 2, docs_dir
            )["selected_phase"]
            write_workflow_document(Path(phase_two["documentation_path"]))
            output = phase_tasks.build_output(
                tasks_path, "next", 2, docs_dir, through_phase=4
            )

        self.assertEqual(
            [phase["number"] for phase in output["selected_phases"]], [3, 4]
        )
        self.assertEqual(output["selected_phase"]["number"], 3)
        self.assertEqual(output["selected_phase"]["next_stage"], "verification")

    def test_range_rejects_missing_noncontiguous_phase_number(self) -> None:
        content = """# Tasks: Missing Phase

## Phase 1: First
- [X] T001 Complete first work

## Phase 3: Third
- [ ] T003 Complete third work
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            tasks_path = Path(temp_dir) / "tasks.md"
            tasks_path.write_text(content, encoding="utf-8")
            with self.assertRaisesRegex(
                ValueError, r"missing phase number\(s\): 2"
            ):
                phase_tasks.build_output(
                    tasks_path, "next", 1, through_phase=3
                )

    def test_range_stops_exactly_at_ending_phase(self) -> None:
        output = phase_tasks.build_output(
            SAMPLE_TASKS, "next", 1, through_phase=4
        )

        self.assertEqual(output["frozen_phase_numbers"], [1, 2, 3, 4])
        self.assertEqual(
            [phase["number"] for phase in output["selected_phases"]], [1, 2, 3, 4]
        )

    def test_cli_rejects_invalid_ranges_and_multi_phase_docs_path(self) -> None:
        cases = [
            (["--phase", "0", "--through-phase", "2"], "positive integer"),
            (["--phase", "-1", "--through-phase", "2"], "positive integer"),
            (["--phase", "1", "--through-phase", "0"], "positive integer"),
            (["--phase", "1", "--through-phase", "-2"], "positive integer"),
            (["--phase", "3", "--through-phase", "2"], "less than or equal"),
            (["--through-phase", "2"], "requires --phase"),
            (
                [
                    "--phase",
                    "1",
                    "--through-phase",
                    "2",
                    "--docs-path",
                    "Documentation/phase.md",
                ],
                "multi-phase range",
            ),
        ]

        for arguments, message in cases:
            with self.subTest(arguments=arguments):
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), str(SAMPLE_TASKS), *arguments],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn(message, result.stderr)

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
            [task["id"] for task in selected["tests_first_tasks"]],
            ["T007", "T008"],
        )
        self.assertEqual(
            [task["id"] for task in selected["implementation_tasks"]],
            ["T009", "T010", "T011"],
        )

    def test_fixture_setup_under_tests_path_is_implementation(self) -> None:
        content = """# Tasks: Fixture Setup Feature

## Phase 1: Setup

- [ ] T001 Add fake scholarship fixtures in `tests/fakes.py`
- [ ] T002 Create shared test helper setup in `tests/helpers.py`
- [ ] T003 Add feature constants in `src/constants.py`
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            tasks_path = Path(temp_dir) / "tasks.md"
            tasks_path.write_text(content, encoding="utf-8")
            output = phase_tasks.build_output(tasks_path, "next", None)

        selected = output["selected_phase"]
        self.assertEqual(selected["test_tasks"], [])
        self.assertEqual(
            [task["id"] for task in selected["implementation_tasks"]],
            ["T001", "T002", "T003"],
        )

    def test_tests_first_heading_is_classified_as_tests(self) -> None:
        content = """# Tasks: Test First Feature

## Phase 1: User Story 1

### Tests First

- [ ] T001 Add contract coverage in `tests/contracts/user_api.py`

### Implementation

- [ ] T002 Add user API in `src/user_api.py`
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            tasks_path = Path(temp_dir) / "tasks.md"
            tasks_path.write_text(content, encoding="utf-8")
            output = phase_tasks.build_output(tasks_path, "next", None)

        selected = output["selected_phase"]
        self.assertEqual([task["id"] for task in selected["test_tasks"]], ["T001"])
        self.assertEqual(
            [task["id"] for task in selected["implementation_tasks"]],
            ["T002"],
        )

    def test_test_and_spec_filenames_are_classified_as_tests(self) -> None:
        content = """# Tasks: Filename Test Feature

## Phase 1: User Story 1

- [ ] T001 Add route behavior in `tests/routes/app.test.ts`
- [ ] T002 Add hook behavior in `tests/hooks/useApp.spec.ts`
- [ ] T003 Add API behavior in `tests/test_api.py`
- [ ] T004 Add API client in `src/api.py`
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            tasks_path = Path(temp_dir) / "tasks.md"
            tasks_path.write_text(content, encoding="utf-8")
            output = phase_tasks.build_output(tasks_path, "next", None)

        selected = output["selected_phase"]
        self.assertEqual(
            [task["id"] for task in selected["test_tasks"]],
            ["T001", "T002", "T003"],
        )
        self.assertEqual(
            [task["id"] for task in selected["implementation_tasks"]],
            ["T004"],
        )

    def test_docs_dir_overrides_generated_documentation_paths(self) -> None:
        output = phase_tasks.build_output(
            SAMPLE_TASKS, "next", 3, Path("docs/custom")
        )
        selected = output["selected_phase"]

        self.assertEqual(output["docs_dir"], "docs/custom")
        self.assertEqual(
            selected["documentation_path"],
            "docs/custom/phase-3-user-story-1-start-or-resume-a-package-priority-p1-execution.md",
        )
        self.assertEqual(
            [key for key in selected if key.endswith("_path")],
            ["documentation_path"],
        )

    def test_explicit_documentation_path_overrides_generated_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            explicit_path = Path(temp_dir) / "chosen" / "phase-three.md"
            output = phase_tasks.build_output(
                SAMPLE_TASKS,
                "next",
                3,
                explicit_docs_path=explicit_path,
            )

        self.assertEqual(output["explicit_docs_path"], explicit_path.as_posix())
        self.assertEqual(
            output["selected_phase"]["documentation_path"],
            explicit_path.as_posix(),
        )

    def test_cli_requires_phase_for_explicit_documentation_path(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(SAMPLE_TASKS),
                "--docs-path",
                "Documentation/phase.md",
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("--docs-path requires --phase", result.stderr)

    def test_default_documentation_paths_use_feature_slug(self) -> None:
        output = phase_tasks.build_output(SAMPLE_TASKS, "next", 3)
        selected = output["selected_phase"]

        self.assertEqual(output["feature_slug"], "example-application-document-workspace")
        self.assertEqual(
            selected["documentation_path"],
            "Documentation/example-application-document-workspace/phase-3-user-story-1-start-or-resume-a-package-priority-p1-execution.md",
        )
        self.assertEqual(
            [key for key in selected if key.endswith("_path")],
            ["documentation_path"],
        )

    def test_handles_six_or_more_phases(self) -> None:
        output = phase_tasks.build_output(SAMPLE_TASKS, "all", None)

        self.assertGreaterEqual(output["phase_count"], 6)

    def test_handles_five_phase_handoff_boundary_fixture(self) -> None:
        output = phase_tasks.build_output(FIVE_PHASE_TASKS, "phase", 4)
        selected = output["selected_phase"]

        self.assertEqual(output["phase_count"], 5)
        self.assertEqual(selected["number"], 4)
        self.assertEqual(selected["incomplete_task_ids"], ["T005", "T006"])
        self.assertEqual([task["id"] for task in selected["test_tasks"]], ["T005"])
        self.assertEqual(
            [task["id"] for task in selected["implementation_tasks"]],
            ["T006"],
        )

    def test_checked_tasks_without_documentation_resume_at_verification(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tasks_path = Path(temp_dir) / "tasks.md"
            docs_dir = Path(temp_dir) / "docs"
            tasks_path.write_text(completed_tasks_fixture(), encoding="utf-8")
            output = phase_tasks.build_output(tasks_path, "next", None, docs_dir)

        selected = output["selected_phase"]
        self.assertEqual(selected["number"], 1)
        self.assertTrue(selected["task_complete"])
        self.assertFalse(selected["documentation_complete"])
        self.assertFalse(selected["workflow_complete"])
        self.assertEqual(selected["next_stage"], "verification")

    def test_documentation_requires_exact_workflow_marker(self) -> None:
        content = """# Tasks: Marker Feature

## Phase 1: Complete Work

- [X] T001 Implement behavior in `src/behavior.py`
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            tasks_path = root / "tasks.md"
            docs_dir = root / "docs"
            tasks_path.write_text(content, encoding="utf-8")
            initial = phase_tasks.build_output(tasks_path, "next", None, docs_dir)
            doc_path = Path(initial["selected_phase"]["documentation_path"])
            write_workflow_document(
                doc_path, "<!-- phase-orchestrator:workflow-complete -->"
            )
            missing_exact_marker = phase_tasks.build_output(
                tasks_path, "next", None, docs_dir
            )
            write_workflow_document(doc_path)
            complete = phase_tasks.build_output(tasks_path, "next", None, docs_dir)

        self.assertFalse(
            missing_exact_marker["selected_phase"]["documentation_complete"]
        )
        self.assertIsNone(complete["selected_phase"])
        self.assertEqual(complete["workflow_complete_phase_count"], 1)
        self.assertEqual(complete["remaining_phase_count"], 0)

    def test_all_selects_by_workflow_completion_in_phase_order(self) -> None:
        content = """# Tasks: Queue Feature

## Phase 1: Already Documented
- [X] T001 Add first behavior in `src/one.py`

## Phase 2: Checked But Undocumented
- [X] T002 Add second behavior in `src/two.py`

## Phase 3: Pending
- [ ] T003 Add third behavior in `src/three.py`
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            tasks_path = root / "tasks.md"
            docs_dir = root / "docs"
            tasks_path.write_text(content, encoding="utf-8")
            phase_one = phase_tasks.build_output(tasks_path, "next", 1, docs_dir)
            write_workflow_document(
                Path(phase_one["selected_phase"]["documentation_path"])
            )
            output = phase_tasks.build_output(tasks_path, "all", None, docs_dir)

        self.assertEqual(
            [phase["number"] for phase in output["selected_phases"]], [2, 3]
        )
        self.assertEqual(output["selected_phases"][0]["next_stage"], "verification")
        self.assertEqual(output["selected_phases"][1]["next_stage"], "implementation")

    def test_empty_test_and_implementation_stages_are_skipped(self) -> None:
        implementation_only = """# Tasks: Implementation Only

## Phase 1: Build
- [ ] T001 Add service in `src/service.py`
"""
        test_only = """# Tasks: Test Only

## Phase 1: Cover
### Tests First
- [ ] T001 Add service test in `tests/test_service.py`
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            docs_dir = root / "docs"
            implementation_path = root / "implementation.md"
            test_path = root / "tests.md"
            implementation_path.write_text(implementation_only, encoding="utf-8")
            test_path.write_text(test_only, encoding="utf-8")
            implementation = phase_tasks.build_output(
                implementation_path, "next", None, docs_dir
            )["selected_phase"]
            tests = phase_tasks.build_output(test_path, "next", None, docs_dir)[
                "selected_phase"
            ]

        self.assertEqual(implementation["test_tasks"], [])
        self.assertEqual(implementation["next_stage"], "implementation")
        self.assertEqual(tests["implementation_tasks"], [])
        self.assertEqual(tests["next_stage"], "test")

    def test_all_workflows_complete_returns_no_selected_phase(self) -> None:
        content = """# Tasks: Complete Feature

## Phase 1: Complete
- [X] T001 Add behavior in `src/behavior.py`
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            tasks_path = root / "tasks.md"
            docs_dir = root / "docs"
            tasks_path.write_text(content, encoding="utf-8")
            initial = phase_tasks.build_output(tasks_path, "next", None, docs_dir)
            write_workflow_document(
                Path(initial["selected_phase"]["documentation_path"])
            )
            output = phase_tasks.build_output(tasks_path, "next", None, docs_dir)

        self.assertIsNone(output["selected_phase"])
        self.assertEqual(output["selected_phases"], [])
        self.assertEqual(output["incomplete_phase_count"], 0)
        self.assertEqual(output["complete_phase_count"], 1)

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

    def test_cli_json_selected_phase_uses_documentation_path_only(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(SAMPLE_TASKS), "--phase", "3", "--json"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(
            output["selected_phase"]["documentation_path"],
            "Documentation/example-application-document-workspace/phase-3-user-story-1-start-or-resume-a-package-priority-p1-execution.md",
        )
        self.assertEqual(
            [key for key in output["selected_phase"] if key.endswith("_path")],
            ["documentation_path"],
        )
        for phase in output["selected_phases"]:
            self.assertEqual(
                [key for key in phase if key.endswith("_path")],
                ["documentation_path"],
            )

    def test_mermaid_style_uses_readable_node_fill(self) -> None:
        text = MERMAID_STYLE.read_text(encoding="utf-8")

        self.assertIn("fill:#161616", text)
        self.assertNotIn("#000000", text)

    def test_phase_doc_template_mermaid_snippet_matches_style_reference(self) -> None:
        style = MERMAID_STYLE.read_text(encoding="utf-8")
        template = PHASE_DOC_TEMPLATE.read_text(encoding="utf-8")

        self.assertIn("## Staged Execution", template)
        self.assertIn("## Regression Baseline And Attribution", template)
        self.assertIn("## Verification And Remediation", template)
        self.assertIn(WORKFLOW_MARKER, template)
        self.assertIn("phase-safe fresh verification", compact(template))
        for line in style_lines(style):
            self.assertIn(line, template)
        self.assertNotIn("#000000", template)

    def test_only_documentation_role_receives_phase_doc_and_mermaid_routing(self) -> None:
        template = WORKER_PROMPT_TEMPLATE.read_text(encoding="utf-8")
        mermaid_path = ".specify/extensions/phase-orchestrator/references/mermaid-style.md"
        phase_doc_path = ".specify/extensions/phase-orchestrator/references/phase-doc-template.md"

        documentation = section(template, "Documentation Role")
        self.assertIn(mermaid_path, documentation)
        self.assertIn(phase_doc_path, documentation)
        for role in [
            "Regression Baseline Role",
            "Test Role",
            "Implementation Role",
            "Verification Role",
            "Remediation Role",
        ]:
            role_text = section(template, role)
            self.assertNotIn(mermaid_path, role_text)
            self.assertNotIn(phase_doc_path, role_text)
            self.assertNotIn("[DOCUMENTATION_PATH]", role_text)

    def test_verification_role_is_strictly_read_only_and_structured(self) -> None:
        template = WORKER_PROMPT_TEMPLATE.read_text(encoding="utf-8")
        verification = compact(section(template, "Verification Role"))

        for expected in [
            "strictly read-only",
            "do not edit, create, delete, format, or generate",
            "focused",
            "independent-phase",
            "regression",
            "never commit eligible",
        ]:
            self.assertIn(expected, verification)

    def test_verifier_strictly_attributes_and_routes_regressions(self) -> None:
        template = compact(
            section(
                WORKER_PROMPT_TEMPLATE.read_text(encoding="utf-8"),
                "Verification Role",
            )
        )
        command = compact(COMMAND_FILE.read_text(encoding="utf-8"))
        for expected in [
            "same command and comparable environment",
            "identical failing test identities and material signatures",
            "no new failure",
            "`phase_introduced_regression`",
            "`preexisting_unrelated_regression`",
            "`inconclusive` with disposition `block`",
            "`passed_with_deferred_findings`",
        ]:
            self.assertIn(expected, template)
        for expected in [
            "baseline passed but the current command fails",
            "adds failing test identities",
            "materially changes a baseline failure signature",
            "reruns the parser in `all` mode",
            "exclude the current selected phase",
            "sets `downstream_safe` to false",
            "changes the disposition to `block`",
            "record it immediately",
        ]:
            self.assertIn(expected, command)

    def test_phase_introduced_regression_remediates_before_scope_block(self) -> None:
        command = compact(COMMAND_FILE.read_text(encoding="utf-8"))

        self.assertIn("Send it to remediation when an in-scope repair is possible", command)
        self.assertIn(
            "cannot be resolved without crossing phase scope",
            command,
        )
        self.assertIn("attributes a regression as uncertain", command)

    def test_regression_baseline_role_is_read_only_and_records_comparable_evidence(
        self,
    ) -> None:
        template = WORKER_PROMPT_TEMPLATE.read_text(encoding="utf-8")
        baseline = compact(section(template, "Regression Baseline Role"))

        for expected in [
            "strictly read-only before phase mutations",
            "exact text",
            "environment fingerprint",
            "failing test identities",
            "material failure signatures",
            "`baseline_recorded`",
            "evidence, not a stage failure",
        ]:
            self.assertIn(expected, baseline)

    def test_baseline_discovers_complete_affected_subsystem_coverage(self) -> None:
        baseline = compact(
            section(
                WORKER_PROMPT_TEMPLATE.read_text(encoding="utf-8"),
                "Regression Baseline Role",
            )
        )

        for expected in [
            "minimum coverage",
            "changed or removed behavior",
            "callers",
            "references",
            "fixtures",
            "parameterizations",
            "complete bounded suite for every affected subsystem",
            "excluded or untested affected surface",
            "`caveats`",
        ]:
            self.assertIn(expected, baseline)

    def test_initial_and_later_verification_preserve_expanded_surface(self) -> None:
        verification = compact(
            section(
                WORKER_PROMPT_TEMPLATE.read_text(encoding="utf-8"),
                "Verification Role",
            )
        )
        command = compact(COMMAND_FILE.read_text(encoding="utf-8"))

        for text in [verification, command]:
            for expected in [
                "actual phase diff",
                "focused",
                "independent-phase",
                "exact baseline",
                "complete bounded",
                "affected subsystem",
                "Continue all planned commands after",
                "aggregate all related in-phase failures",
                "preserve",
                "never narrow",
            ]:
                self.assertIn(expected.lower(), text.lower())

    def test_each_role_is_context_isolated_and_sanitized(self) -> None:
        template = WORKER_PROMPT_TEMPLATE.read_text(encoding="utf-8")
        common = compact(section(template, "Common Envelope"))
        sanitization = compact(section(template, "Sanitization And Routing"))

        for prohibited in [
            "Do not stage, commit, push, spawn workers",
            "Do not reconstruct or request full parent traces",
        ]:
            self.assertIn(prohibited, common)
        for parent_only in [
            "model names",
            "effort settings",
            "worker-spawn configuration",
            "phase queues",
            "parent plans",
            "full transcripts",
        ]:
            self.assertIn(parent_only, sanitization)

    def test_test_role_distinguishes_expected_red_from_invalid_failures(self) -> None:
        test_role = section(
            WORKER_PROMPT_TEMPLATE.read_text(encoding="utf-8"), "Test Role"
        )
        test_role = compact(test_role)

        self.assertIn("attributable to still-missing assigned implementation", test_role)
        for invalid in [
            "Syntax",
            "collection",
            "fixture",
            "infrastructure",
            "environment",
            "flaky",
            "unrelated",
        ]:
            self.assertIn(invalid, test_role)
        self.assertIn("rerun the focused gate as needed", test_role)
        self.assertIn("remains after available in-scope correction", test_role)
        self.assertNotIn("stop, and report the gate as failed", test_role)

        command = compact(COMMAND_FILE.read_text(encoding="utf-8"))
        self.assertIn("the worker to restore assigned checkboxes", command)
        self.assertIn("the parent stops the workflow", command)

    def test_implementation_role_routes_unresolved_gate_to_verification(self) -> None:
        template = WORKER_PROMPT_TEMPLATE.read_text(encoding="utf-8")
        implementation = compact(section(template, "Implementation Role"))
        command = compact(COMMAND_FILE.read_text(encoding="utf-8"))

        for expected in [
            "preceding test stage, when present",
            "complete focused phase-test gate",
            "any other relevant phase-scoped tests",
            "If green cannot be reached",
            "return `unresolved` with typed findings",
            "not a final blocker decision",
            "set its `disposition` to `null`",
            "fresh verifier to classify it independently",
            "completed schema-valid implementation report",
            "Do not stage, commit, or decide the next transition",
        ]:
            self.assertIn(expected, implementation)
        self.assertNotIn("progress commit", implementation)
        self.assertNotIn("commit eligibility", implementation)
        self.assertNotIn("parent may create", implementation.lower())
        self.assertIn("tests authored by the preceding test stage", command)
        self.assertIn("when present, and any other relevant phase-scoped tests", command)

    def test_test_authoring_only_expected_red_passes_without_remediation(self) -> None:
        template = WORKER_PROMPT_TEMPLATE.read_text(encoding="utf-8")
        verification = compact(section(template, "Verification Role"))
        command = compact(COMMAND_FILE.read_text(encoding="utf-8"))

        for text in [verification, command]:
            self.assertIn("test-authoring-only", text)
            self.assertIn("expected_red", text)
            self.assertIn("overall passing", text)
        self.assertIn("do not request out-of-scope remediation", verification)
        self.assertIn("skips remediation", command)

    def test_implement_discipline_is_required_for_test_and_implementation(self) -> None:
        template = WORKER_PROMPT_TEMPLATE.read_text(encoding="utf-8")
        test_role = compact(section(template, "Test Role"))
        implementation = compact(section(template, "Implementation Role"))
        remediation = compact(section(template, "Remediation Role"))
        routing = compact(section(template, "Sanitization And Routing"))

        for role in [test_role, implementation]:
            self.assertIn("Use the supplied official", role)
            self.assertIn("`/speckit.implement`", role)
        self.assertIn("only when it is useful", remediation)
        self.assertIn("for both test and implementation work", routing)
        self.assertIn("for remediation only when it is useful", routing)

    def test_every_remediation_result_gets_fresh_verification_and_parent_cap(self) -> None:
        template = WORKER_PROMPT_TEMPLATE.read_text(encoding="utf-8")
        remediation = compact(section(template, "Remediation Role"))
        command = compact(COMMAND_FILE.read_text(encoding="utf-8"))

        self.assertIn("run focused validation as needed", remediation)
        self.assertIn("remains after available in-scope remediation", remediation)
        self.assertIn("completed schema-valid remediation report and control to the parent", remediation)
        self.assertNotIn("fresh read-only verifier", remediation)
        self.assertNotIn("two-attempt cap", remediation)
        self.assertIn("at most two complete", command)
        self.assertIn("regardless of the remediation validation result", command)
        self.assertIn("does not itself make the final stop decision", command)

    def test_validation_running_workers_receive_sandbox_execution_policy(self) -> None:
        template = WORKER_PROMPT_TEMPLATE.read_text(encoding="utf-8")
        policy = compact(section(template, "Validation Execution Environment"))
        command = compact(COMMAND_FILE.read_text(encoding="utf-8"))

        for role in [
            "baseline-verification",
            "test",
            "implementation",
            "verification",
            "remediation",
        ]:
            self.assertIn(role, policy)
            self.assertIn(role, command)
        for expected in [
            "prefer execution outside the Codex sandbox",
            "run the exact command inside the sandbox",
            "do not attribute it to the product",
            "Request user permission to rerun that exact command outside the sandbox",
            "perform the outside rerun before returning",
            "result as authoritative",
            "environment blocker",
            "do not consume a remediation attempt",
        ]:
            self.assertIn(expected, policy)
        self.assertNotIn("the parent can request permission", policy)
        self.assertIn("Documentation workers do not receive it", command)

    def test_sandbox_failure_requires_outside_rerun_before_attribution(self) -> None:
        command = compact(COMMAND_FILE.read_text(encoding="utf-8"))

        for expected in [
            "plausibly caused by filesystem or socket permission",
            "worker running the validation requests user permission",
            "treats the outside result as authoritative",
            "permission is denied",
            "outside execution remains unavailable",
            "environment blocker with the command, sandbox evidence",
            "Do not consume a remediation attempt",
            "parent must not stop immediately",
            "relaunch a fresh isolated worker for that same stage and assignment",
            "Neither the blocker nor this relaunch consumes a remediation attempt",
            "environment `block`, first complete the parent permission",
        ]:
            self.assertIn(expected, command)

    def test_environment_blocker_uses_stage_valid_report_shapes(self) -> None:
        validator = report_validator()
        sandbox_evidence = {
            "command": "pytest affected",
            "environment_fingerprint": "codex-sandbox; python-3.12",
            "status": "failed",
            "failing_tests": [],
            "failure_signatures": ["socket permission denied"],
        }

        for stage in [
            "baseline_verification",
            "test",
            "implementation",
            "verification",
            "remediation",
        ]:
            report = base_report(stage)
            report["status"] = "blocked"
            report["validation"][0].update(
                status="not_run",
                summary="Exact outside rerun was unavailable after sandbox denial.",
            )
            finding = report_finding("block" if stage == "verification" else None)
            finding.update(
                kind="inconclusive",
                attribution="uncertain",
                confidence="confirmed",
                baseline_evidence=None,
                current_evidence=sandbox_evidence,
                summary="Environment blocker; no product attribution.",
            )
            report["findings"] = [finding]
            report["caveats"] = [
                "User denied permission for the exact outside rerun."
            ]
            if stage == "remediation":
                report["remediation_results"][0]["status"] = "unresolved"

            self.assertTrue(validator.is_valid(report), stage)
        contract = compact(
            section(
                WORKER_PROMPT_TEMPLATE.read_text(encoding="utf-8"),
                "Structured Report Contract",
            )
        )
        self.assertIn("without adding fields", contract)
        self.assertIn("verification finding uses disposition `block`", contract)
        self.assertIn("remediation use disposition `null`", contract)
        self.assertIn("environment evidence, not product-defect attribution", contract)

    def test_verifier_prompt_omits_parent_transition_mechanics(self) -> None:
        verification = compact(
            section(
                WORKER_PROMPT_TEMPLATE.read_text(encoding="utf-8"),
                "Verification Role",
            )
        )

        self.assertIn("the parent owns the final transition", verification)
        self.assertIn("`downstream_safe: null`", verification)
        self.assertIn("parent owns the downstream-safety determination", verification)
        self.assertNotIn("attempt-cap", verification)
        self.assertNotIn("remaining phase queue", verification)

    def test_worker_report_uses_schema_and_stage_specific_forms(self) -> None:
        worker_template = WORKER_PROMPT_TEMPLATE.read_text(encoding="utf-8")
        template = compact(
            section(
                worker_template,
                "Structured Report Contract",
            )
        )
        command = compact(COMMAND_FILE.read_text(encoding="utf-8"))
        sanitization = compact(section(worker_template, "Sanitization And Routing"))

        for form in [
            "Baseline Verification Report Form",
            "Test Report Form",
            "Implementation Report Form",
            "Verification Report Form",
            "Remediation Report Form",
            "Documentation Report Form",
        ]:
            self.assertIn(form, template)
        for field in [
            '"schema_version"',
            '"stage"',
            '"phase_number"',
            '"assigned_task_ids"',
            '"status"',
            '"changed_paths"',
            '"validation"',
            '"regression_evidence"',
            '"expected_failures"',
            '"findings"',
            '"remediation_results"',
            '"caveats"',
        ]:
            self.assertIn(field, template)
        self.assertIn("Every shown field is required", template)
        self.assertIn("use empty arrays rather than omitting fields", template)
        for field in [
            "`disposition`",
            "`attribution`",
            "`confidence`",
            "`baseline_evidence`",
            "`current_evidence`",
            "`downstream_safe`",
        ]:
            self.assertIn(field, template)
        self.assertIn("phase-report.schema.json", command)
        self.assertIn("validate the completed report", command)
        self.assertIn("parent-observed Git manifest", command)
        self.assertIn("Reject the report before any transition or commit", command)
        self.assertIn("selected role section and its matching report form", sanitization)
        self.assertIn("report forms belonging to every other stage", sanitization)

    def test_non_verifier_findings_are_provisional_until_verification(self) -> None:
        template = WORKER_PROMPT_TEMPLATE.read_text(encoding="utf-8")
        remediation = compact(section(template, "Remediation Role"))
        command = compact(COMMAND_FILE.read_text(encoding="utf-8"))

        self.assertIn("newly discovered relevant issue", remediation)
        self.assertIn("`disposition` to `null`", remediation)
        self.assertIn("fresh verifier to classify it independently", remediation)
        self.assertIn("Only verification-stage findings", command)
        self.assertIn("`disposition: null`", command)

    def test_implementation_and_remediation_use_separate_progress_commits(self) -> None:
        command = compact(COMMAND_FILE.read_text(encoding="utf-8"))
        remediation = compact(
            section(
                WORKER_PROMPT_TEMPLATE.read_text(encoding="utf-8"),
                "Remediation Role",
            )
        )

        self.assertIn("eligible reversible progress checkpoint", command)
        self.assertIn("immediately stage only the implementation stage's exact changed paths", command)
        self.assertIn("fix(<scope>): remediate phase <N> findings", command)
        self.assertIn("each remediation attempt commit their own exact paths", command)
        self.assertIn("Never combine their manifests", command)
        self.assertIn("assigned implementation-task intent", command)
        self.assertIn("`passed` or `unresolved`", command)
        self.assertIn("completed schema-valid remediation report", remediation)
        self.assertIn("Do not stage, commit, or decide the next transition", remediation)
        self.assertNotIn("progress commit", remediation)
        self.assertNotIn("commit eligibility", remediation)

    def test_usage_starts_with_a_purpose_line(self) -> None:
        lines = USAGE.read_text(encoding="utf-8").splitlines()

        self.assertEqual(lines[0], "# Usage")
        self.assertIn("This guide explains", lines[2])
        self.assertIn("parent-owned Git behavior", " ".join(lines[2:4]))

    def test_command_metadata_includes_v2_trigger_friendly_skill_wording(self) -> None:
        command_text = COMMAND_FILE.read_text(encoding="utf-8")
        extension_text = EXTENSION_FILE.read_text(encoding="utf-8")
        expected_description = (
            "Use /speckit.phase-orchestrator.phase or "
            "$speckit-phase-orchestrator-phase to run Spec Kit tasks.md through "
            "isolated regression-baseline, test, implementation, verification, "
            "remediation, and documentation agents with parent-owned gated commits."
        )

        self.assertIn(f'description: "{expected_description}"', command_text)
        self.assertIn(f'description: "{expected_description}"', extension_text)

    def test_agent_support_documents_integration_skill_directories(self) -> None:
        text = AGENT_SUPPORT.read_text(encoding="utf-8")

        for expected in [
            ".agents/skills",
            ".cursor/skills",
            ".claude/skills",
            ".specify/extensions/phase-orchestrator/",
            "Seeing only `SKILL.md`",
            "installed with `--dev`",
            "published release URL",
            "same original source",
            "--force",
            "specify extension remove phase-orchestrator",
        ]:
            self.assertIn(expected, text)

    def test_parent_discovers_and_routes_skills_and_mcps_with_user_precedence(
        self,
    ) -> None:
        command = compact(COMMAND_FILE.read_text(encoding="utf-8"))

        for expected in [
            "inspect the skills and MCP servers exposed",
            "Explicit user exclusions take precedence",
            "use Exa first",
            "another available web-search tool",
            "look for a related available MCP",
            "Do not hardcode a database provider",
            "continue with suitable project tools",
            "Automatically select relevant available frontend or backend skills and MCPs",
            "applicable MCP opt-outs",
        ]:
            self.assertIn(expected, command)

    def test_worker_handoff_propagates_exa_database_and_mcp_opt_out_policy(
        self,
    ) -> None:
        template = WORKER_PROMPT_TEMPLATE.read_text(encoding="utf-8")
        common = compact(section(template, "Common Envelope"))
        routing = compact(section(template, "Sanitization And Routing"))

        for expected in [
            "[STAGE_RELEVANT_SKILLS_OR_NONE]",
            "[STAGE_RELEVANT_MCPS_OR_NONE]",
            "[APPLICABLE_MCP_OPT_OUTS_OR_NONE]",
            "[EXA_FIRST_POLICY_OR_NOT_APPLICABLE]",
            "confirm it is exposed in this worker context",
        ]:
            self.assertIn(expected, common)

        for expected in [
            "explicit user exclusions take precedence",
            "use Exa first",
            "report the fallback",
            "available related database MCP",
            "Do not hardcode a provider",
            "continue with suitable project tools",
            "frontend/backend skills and MCPs",
            "only when relevant to the stage and phase",
        ]:
            self.assertIn(expected, routing)

    def test_common_handoff_is_compact_and_stage_specific(self) -> None:
        template = WORKER_PROMPT_TEMPLATE.read_text(encoding="utf-8")
        common = compact(section(template, "Common Envelope"))

        for placeholder in [
            "[STAGE]",
            "[PHASE_NUMBER]",
            "[ASSIGNED_TASK_IDS_OR_NONE]",
            "[PRIOR_SHA]",
            "[PRIOR_MANIFEST_SUMMARY_OR_NONE]",
            "[PRIOR_VALIDATION_SUMMARY_OR_NONE]",
            "[REGRESSION_BASELINE_OR_UNAVAILABLE]",
            "[DEFERRED_FINDINGS_OR_NONE]",
            "[EXPECTED_FAILURES_OR_NONE]",
            "[VALIDATION_EXPECTATIONS]",
        ]:
            self.assertIn(placeholder, common)
        self.assertNotIn("Commit eligibility", common)
        self.assertNotIn("COMMIT_ELIGIBILITY", common)
        self.assertNotIn("Remediation attempt", common)
        self.assertNotIn("REMEDIATION_ATTEMPT", common)
        self.assertNotIn("SANITIZED_PARENT_CONTEXT", common)
        self.assertIn("Do not reconstruct or request full parent traces", common)

    def test_handoff_schema_v2_and_sample_are_valid(self) -> None:
        schema = json.loads(HANDOFF_SCHEMA.read_text(encoding="utf-8"))
        sample = json.loads(HANDOFF_SAMPLE.read_text(encoding="utf-8"))

        Draft202012Validator.check_schema(schema)
        self.assertEqual(schema["properties"]["schema_version"]["const"], "2.0.0")
        self.assertEqual(
            set(schema["properties"]["stage"]["enum"]),
            {
                "baseline_verification",
                "test",
                "implementation",
                "verification",
                "remediation",
                "documentation",
            },
        )
        assert_schema_valid(self, sample)
        self.assertNotIn("commit_eligibility", schema["properties"])
        self.assertNotIn("commit_eligibility", schema["required"])
        self.assertNotIn("commit_eligibility", sample)
        self.assertNotIn("documentation_path", schema["properties"]["phase"]["properties"])
        self.assertNotIn("documentation_path", sample["phase"])
        self.assertNotIn("mode", schema["properties"])
        self.assertNotIn("mode", schema["required"])
        self.assertNotIn("mode", sample)
        for field in [
            "task_complete",
            "documentation_complete",
            "workflow_complete",
            "next_stage",
        ]:
            self.assertNotIn(field, schema["properties"]["phase"]["properties"])
            self.assertNotIn(field, schema["properties"]["phase"]["required"])
            self.assertNotIn(field, sample["phase"])
        self.assertEqual(
            set(schema["properties"]["validation"]["properties"]),
            {"expectations"},
        )
        self.assertEqual(set(sample["validation"]), {"expectations"})
        self.assertEqual(
            sample["report_contract"],
            {
                "schema_id": "https://github.com/awasali14/spec-kit-phase-orchestrator/schemas/phase-report.schema.json",
                "schema_version": "2.0.0",
                "stage": "test",
            },
        )

        missing_report_contract = copy.deepcopy(sample)
        del missing_report_contract["report_contract"]
        self.assertFalse(Draft202012Validator(schema).is_valid(missing_report_contract))

        wrong_report_stage = copy.deepcopy(sample)
        wrong_report_stage["report_contract"]["stage"] = "verification"
        self.assertFalse(Draft202012Validator(schema).is_valid(wrong_report_stage))

        leaked_current_result = copy.deepcopy(sample)
        leaked_current_result["validation"]["results"] = []
        leaked_current_result["validation"]["verdict"] = "pending"
        self.assertFalse(Draft202012Validator(schema).is_valid(leaked_current_result))

        leaked_selector_state = copy.deepcopy(sample)
        leaked_selector_state["mode"] = "phase"
        self.assertFalse(Draft202012Validator(schema).is_valid(leaked_selector_state))

        leaked_lifecycle_state = copy.deepcopy(sample)
        leaked_lifecycle_state["phase"]["next_stage"] = "test"
        self.assertFalse(Draft202012Validator(schema).is_valid(leaked_lifecycle_state))

    def test_phase_report_schema_accepts_all_six_stage_forms(self) -> None:
        schema = json.loads(REPORT_SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)

        for stage in [
            "baseline_verification",
            "test",
            "implementation",
            "verification",
            "remediation",
            "documentation",
        ]:
            report = base_report(stage)
            self.assertEqual(list(validator.iter_errors(report)), [], stage)

    def test_phase_report_schema_rejects_missing_fields_and_stage_wrong_evidence(self) -> None:
        validator = report_validator()
        missing = base_report("test")
        del missing["caveats"]
        self.assertFalse(validator.is_valid(missing))

        wrong_gate = base_report("test")
        wrong_gate["validation"][0]["kind"] = "regression"
        self.assertFalse(validator.is_valid(wrong_gate))

        wrong_stage = base_report("test")
        wrong_stage["stage"] = "review"
        self.assertFalse(validator.is_valid(wrong_stage))

        incomplete_verifier = base_report("verification")
        incomplete_verifier["validation"] = incomplete_verifier["validation"][:2]
        self.assertFalse(validator.is_valid(incomplete_verifier))

        incomplete_documentation = base_report("documentation")
        incomplete_documentation["validation"] = incomplete_documentation["validation"][:1]
        self.assertFalse(validator.is_valid(incomplete_documentation))

    def test_phase_report_schema_keeps_read_only_stages_non_mutating(self) -> None:
        validator = report_validator()
        for stage in ["baseline_verification", "verification"]:
            report = base_report(stage)
            report["changed_paths"] = ["src/unexpected.py"]
            self.assertFalse(validator.is_valid(report), stage)

    def test_phase_report_schema_enforces_dispositions_and_verdict_consistency(self) -> None:
        validator = report_validator()

        implementation = base_report("implementation", "unresolved")
        implementation["validation"][0]["status"] = "failed"
        implementation["findings"] = [report_finding("remediate")]
        self.assertFalse(validator.is_valid(implementation))
        implementation["findings"][0]["disposition"] = None
        self.assertTrue(validator.is_valid(implementation))

        verifier = base_report("verification", "unresolved")
        verifier["findings"] = [report_finding("remediate")]
        self.assertTrue(validator.is_valid(verifier))

        contradictory = copy.deepcopy(verifier)
        contradictory["status"] = "passed"
        self.assertFalse(validator.is_valid(contradictory))

        failed_validation = base_report("verification", "passed")
        failed_validation["validation"][0]["status"] = "failed"
        self.assertFalse(validator.is_valid(failed_validation))

        blocked = base_report("verification", "blocked")
        blocked["findings"] = [report_finding("block")]
        self.assertTrue(validator.is_valid(blocked))
        blocked["findings"][0]["disposition"] = "remediate"
        self.assertFalse(validator.is_valid(blocked))

    def test_report_schema_allows_in_phase_remediation_without_baseline(self) -> None:
        validator = report_validator()
        verifier = base_report("verification", "unresolved")
        finding = report_finding("remediate")
        finding.update(
            kind="phase_scoped_failure",
            attribution="uncertain",
            confidence="confirmed",
            baseline_evidence=None,
        )
        verifier["findings"] = [finding]

        self.assertTrue(validator.is_valid(verifier))

    def test_report_schema_requires_baseline_for_phase_introduced_regression(self) -> None:
        validator = report_validator()
        verifier = base_report("verification", "unresolved")
        finding = report_finding("remediate")
        finding["kind"] = "phase_introduced_regression"
        verifier["findings"] = [finding]

        self.assertFalse(validator.is_valid(verifier))
        finding["baseline_evidence"] = comparison_evidence("passed")
        self.assertTrue(validator.is_valid(verifier))

    def test_uncertain_scope_and_unproven_out_of_phase_failures_block(self) -> None:
        validator = report_validator()
        verifier = base_report("verification", "blocked")
        finding = report_finding("block")
        finding.update(
            kind="inconclusive",
            attribution="uncertain",
            confidence="uncertain",
            baseline_evidence=None,
        )
        verifier["findings"] = [finding]

        self.assertTrue(validator.is_valid(verifier))
        command = compact(COMMAND_FILE.read_text(encoding="utf-8"))
        self.assertIn("uncertain scope", command)
        self.assertIn("unproven out-of-phase failure", command)

    def test_phase_report_schema_enforces_defer_and_expected_red_evidence(self) -> None:
        validator = report_validator()
        deferred = base_report("verification", "passed_with_deferred_findings")
        finding = report_finding("defer")
        finding.update(
            kind="preexisting_unrelated_regression",
            attribution="preexisting_unrelated",
            baseline_evidence=comparison_evidence("failed"),
            current_evidence=comparison_evidence("failed"),
        )
        deferred["findings"] = [finding]
        self.assertTrue(validator.is_valid(deferred))

        deferred["findings"][0]["confidence"] = "uncertain"
        self.assertFalse(validator.is_valid(deferred))

        expected_red = base_report("test", "expected_red")
        expected_red["validation"][0]["status"] = "expected_red"
        self.assertFalse(validator.is_valid(expected_red))
        expected_red["expected_failures"] = [
            {
                "summary": "Production behavior is not implemented.",
                "related_task_ids": ["T009"],
                "attributable_to_missing_implementation": True,
            }
        ]
        self.assertTrue(validator.is_valid(expected_red))

    def test_phase_report_schema_enforces_remediation_results(self) -> None:
        validator = report_validator()
        remediation = base_report("remediation")
        self.assertTrue(validator.is_valid(remediation))

        missing_results = copy.deepcopy(remediation)
        missing_results["remediation_results"] = []
        self.assertFalse(validator.is_valid(missing_results))

        unresolved = copy.deepcopy(remediation)
        unresolved["status"] = "unresolved"
        self.assertFalse(validator.is_valid(unresolved))
        unresolved["remediation_results"][0]["status"] = "unresolved"
        unresolved["validation"][0]["status"] = "failed"
        self.assertTrue(validator.is_valid(unresolved))

        malformed = copy.deepcopy(unresolved)
        del malformed["remediation_results"][0]["finding_id"]
        self.assertFalse(validator.is_valid(malformed))

    def test_handoff_schema_enforces_baseline_read_only_contract(self) -> None:
        schema = json.loads(HANDOFF_SCHEMA.read_text(encoding="utf-8"))
        sample = json.loads(HANDOFF_SAMPLE.read_text(encoding="utf-8"))
        baseline = copy.deepcopy(sample)
        baseline.update(
            stage="baseline_verification",
            assigned_task_ids=[],
            expected_failures=[],
        )
        set_handoff_stage(baseline, "baseline_verification")
        baseline["scope"]["read_only"] = True
        assert_schema_valid(self, baseline)

        baseline["assigned_task_ids"] = ["T007"]
        self.assertFalse(Draft202012Validator(schema).is_valid(baseline))
        baseline["assigned_task_ids"] = []
        baseline["scope"]["read_only"] = False
        self.assertFalse(Draft202012Validator(schema).is_valid(baseline))
        baseline["scope"]["read_only"] = True
        leaked_commit_state = copy.deepcopy(baseline)
        leaked_commit_state["commit_eligibility"] = {"no_commit": True}
        self.assertFalse(Draft202012Validator(schema).is_valid(leaked_commit_state))

    def test_handoff_schema_types_regression_evidence_and_findings(self) -> None:
        schema = json.loads(HANDOFF_SCHEMA.read_text(encoding="utf-8"))
        sample = json.loads(HANDOFF_SAMPLE.read_text(encoding="utf-8"))
        verifier = copy.deepcopy(sample)
        verifier.update(
            stage="verification",
            assigned_task_ids=[],
            expected_failures=[],
        )
        set_handoff_stage(verifier, "verification")
        verifier["scope"]["read_only"] = True
        evidence = {
            "command": "npm test -- regression",
            "environment_fingerprint": "node-22; runner-1",
            "status": "failed",
            "failing_tests": ["legacy regression"],
            "failure_signatures": ["expected active; received pending"],
        }
        verifier["regression_baseline"] = [copy.deepcopy(evidence)]
        verifier["findings"] = [
            {
                "id": "F1",
                "kind": "preexisting_unrelated_regression",
                "gate": "regression",
                "disposition": "defer",
                "attribution": "preexisting_unrelated",
                "confidence": "confirmed",
                "summary": "Unchanged legacy regression.",
                "related_task_ids": [],
                "affected_paths": ["src/legacy.js"],
                "baseline_evidence": copy.deepcopy(evidence),
                "current_evidence": copy.deepcopy(evidence),
                "downstream_safe": None,
            }
        ]
        assert_schema_valid(self, verifier)

        missing_confidence = copy.deepcopy(verifier)
        del missing_confidence["findings"][0]["confidence"]
        self.assertFalse(Draft202012Validator(schema).is_valid(missing_confidence))

        phase_introduced = copy.deepcopy(verifier)
        phase_introduced["findings"][0].update(
            kind="phase_introduced_regression",
            disposition="remediate",
            attribution="phase_introduced",
            baseline_evidence=None,
        )
        self.assertFalse(Draft202012Validator(schema).is_valid(phase_introduced))
        phase_introduced["findings"][0]["baseline_evidence"] = copy.deepcopy(evidence)
        self.assertTrue(Draft202012Validator(schema).is_valid(phase_introduced))

    def test_provisional_finding_round_trips_into_fresh_verification(self) -> None:
        schema = json.loads(HANDOFF_SCHEMA.read_text(encoding="utf-8"))
        sample = json.loads(HANDOFF_SAMPLE.read_text(encoding="utf-8"))
        provisional = {
            "id": "F1",
            "kind": "phase_scoped_failure",
            "gate": "focused",
            "disposition": None,
            "attribution": "uncertain",
            "confidence": "uncertain",
            "summary": "The focused failure remained after in-scope remediation.",
            "related_task_ids": [],
            "affected_paths": [],
            "baseline_evidence": None,
            "current_evidence": None,
            "downstream_safe": None,
        }

        verification = copy.deepcopy(sample)
        verification.update(
            stage="verification",
            assigned_task_ids=[],
            expected_failures=[],
            findings=[copy.deepcopy(provisional)],
        )
        set_handoff_stage(verification, "verification")
        verification["scope"]["read_only"] = True
        assert_schema_valid(self, verification)

        remediation = copy.deepcopy(verification)
        set_handoff_stage(remediation, "remediation")
        remediation["scope"]["read_only"] = False
        self.assertFalse(Draft202012Validator(schema).is_valid(remediation))

        remediation["findings"][0]["disposition"] = "remediate"
        assert_schema_valid(self, remediation)

    def test_handoff_schema_enforces_expected_red_attribution(self) -> None:
        sample = json.loads(HANDOFF_SAMPLE.read_text(encoding="utf-8"))
        invalid = copy.deepcopy(sample)
        invalid["expected_failures"][0][
            "attributable_to_missing_implementation"
        ] = False

        schema = json.loads(HANDOFF_SCHEMA.read_text(encoding="utf-8"))
        self.assertFalse(Draft202012Validator(schema).is_valid(invalid))

    def test_handoff_schema_enforces_read_only_verifier(self) -> None:
        sample = json.loads(HANDOFF_SAMPLE.read_text(encoding="utf-8"))
        verifier = copy.deepcopy(sample)
        verifier.update(
            stage="verification",
            assigned_task_ids=[],
            expected_failures=[],
        )
        set_handoff_stage(verifier, "verification")
        verifier["scope"]["read_only"] = True
        assert_schema_valid(self, verifier)

        verifier["scope"]["read_only"] = False
        self.assertFalse(
            Draft202012Validator(
                json.loads(HANDOFF_SCHEMA.read_text(encoding="utf-8"))
            ).is_valid(verifier)
        )

    def test_handoff_schema_omits_parent_cycle_and_commit_state(self) -> None:
        schema = json.loads(HANDOFF_SCHEMA.read_text(encoding="utf-8"))
        sample = json.loads(HANDOFF_SAMPLE.read_text(encoding="utf-8"))
        remediation = copy.deepcopy(sample)
        remediation.update(
            stage="remediation",
            expected_failures=[],
        )
        set_handoff_stage(remediation, "remediation")
        assert_schema_valid(self, remediation)

        leaked_cycle_state = copy.deepcopy(remediation)
        leaked_cycle_state["remediation_attempt"] = 1
        self.assertFalse(Draft202012Validator(schema).is_valid(leaked_cycle_state))
        self.assertNotIn("remediation_attempt", schema["properties"])
        self.assertNotIn("remediation_attempt", schema["required"])

        leaked_commit_state = copy.deepcopy(remediation)
        leaked_commit_state["commit_eligibility"] = {
            "eligible": False,
            "change_kind": "none",
            "requirements": [],
            "no_commit": True,
        }
        self.assertFalse(Draft202012Validator(schema).is_valid(leaked_commit_state))

    def test_documentation_handoff_requires_marker_contract(self) -> None:
        schema = json.loads(HANDOFF_SCHEMA.read_text(encoding="utf-8"))
        sample = json.loads(HANDOFF_SAMPLE.read_text(encoding="utf-8"))
        documentation = copy.deepcopy(sample)
        documentation.update(
            stage="documentation",
            assigned_task_ids=[],
            expected_failures=[],
        )
        set_handoff_stage(documentation, "documentation")
        documentation["documentation"] = {
            "path": "Documentation/feature/phase-3.md",
            "workflow_complete_marker": WORKFLOW_MARKER,
            "mermaid_required": True,
        }
        assert_schema_valid(self, documentation)

        missing = copy.deepcopy(documentation)
        del missing["documentation"]
        self.assertFalse(Draft202012Validator(schema).is_valid(missing))

        leaked_to_test = copy.deepcopy(sample)
        leaked_to_test["documentation"] = copy.deepcopy(documentation["documentation"])
        self.assertFalse(Draft202012Validator(schema).is_valid(leaked_to_test))

        leaked_phase_path = copy.deepcopy(sample)
        leaked_phase_path["phase"]["documentation_path"] = documentation[
            "documentation"
        ]["path"]
        self.assertFalse(Draft202012Validator(schema).is_valid(leaked_phase_path))

    def test_parent_git_gates_use_exact_paths_and_protect_dirty_state(self) -> None:
        command = compact(COMMAND_FILE.read_text(encoding="utf-8"))

        for expected in [
            "Before the first phase and again before every stage",
            "pre-existing dirty paths as protected",
            "overlaps a protected path",
            "exact changed-path manifest",
            "Reject unrelated paths, unexpected generated artifacts",
            "stage only those paths",
            "implementation stage's exact changed paths",
            "remediation stage's exact changed paths",
            "stage that exact path",
            "Never use broad staging",
        ]:
            self.assertIn(expected, command)
        for broad_command in ["git add .", "git add -A"]:
            self.assertIn(f"`{broad_command}`", command)

    def test_no_change_and_no_commit_stages_preserve_manifests_and_index(self) -> None:
        command = compact(COMMAND_FILE.read_text(encoding="utf-8"))

        for expected in [
            "records `no_changes` and proceeds without a commit",
            "never stage or commit",
            "reviewed manifest for each stage",
            "original index unchanged",
            "accumulated changes unstaged",
        ]:
            self.assertIn(expected, command)

    def test_stage_commit_contracts_require_validation_and_prior_sha(self) -> None:
        command = compact(COMMAND_FILE.read_text(encoding="utf-8"))

        for subject in [
            "test(<scope>): add phase <N> coverage",
            "feat(<scope>):",
            "fix(<scope>):",
            "chore(<scope>):",
            "docs(<scope>): document phase <N> execution",
        ]:
            self.assertIn(subject, command)
        self.assertGreaterEqual(command.count("prior SHA"), 4)
        self.assertIn("phase-safe final verification", command)
        self.assertIn("assigned implementation-task intent", command)
        self.assertIn("fix(<scope>): remediate phase <N> findings", command)
        self.assertIn("normally has three commits", command)
        self.assertIn("up to five", command)

    def test_all_mode_completes_every_gate_before_reselection(self) -> None:
        command = compact(COMMAND_FILE.read_text(encoding="utf-8"))

        self.assertIn(
            "execute one phase through every gate and its workflow-complete",
            command,
        )
        self.assertIn("before reparsing and selecting the next phase", command)
        self.assertIn("sequentially", command)
        self.assertIn("Never reuse a", command)

    def test_parent_analyzes_complete_tasks_file_before_every_selector(self) -> None:
        command = compact(COMMAND_FILE.read_text(encoding="utf-8"))

        self.assertIn("read and analyze the complete original `tasks.md`", command)
        self.assertIn("not only parser summaries", command)
        self.assertIn(
            "applies equally to `next`, a single `phase`, an inclusive phase range, and `all`",
            command,
        )
        self.assertIn("Keep this complete-file analysis parent-only", command)
        self.assertIn("must not contain future-phase tasks", command)

    def test_command_range_contract_is_frozen_and_workflow_gated(self) -> None:
        command = compact(COMMAND_FILE.read_text(encoding="utf-8"))

        self.assertIn("phase <start> to <end> <tasks.md path>", command)
        self.assertIn("--through-phase <end>", command)
        self.assertIn(
            "every task checkbox in Phase `start - 1` is checked", command
        )
        self.assertIn("do not require predecessor orchestration documentation", command)
        self.assertIn("Freeze the exact inclusive phase-number queue", command)
        self.assertIn("never add a phase or continue beyond `end`", command)
        self.assertIn("Do not advance merely because task checkboxes are checked", command)

    def test_version_and_public_contract_are_consistently_v2_1(self) -> None:
        extension = EXTENSION_FILE.read_text(encoding="utf-8")
        command = COMMAND_FILE.read_text(encoding="utf-8")
        changelog = CHANGELOG.read_text(encoding="utf-8")
        handoff_schema = json.loads(HANDOFF_SCHEMA.read_text(encoding="utf-8"))
        report_schema = json.loads(REPORT_SCHEMA.read_text(encoding="utf-8"))

        self.assertIn('version: "2.1.0"', extension)
        self.assertIn("# Spec Kit Phase Orchestrator 2.1", command)
        self.assertRegex(changelog, r"(?m)^## 2\.1\.0 - Unreleased$")
        self.assertEqual(handoff_schema["properties"]["schema_version"]["const"], "2.0.0")
        self.assertEqual(report_schema["properties"]["schema_version"]["const"], "2.0.0")
        self.assertEqual(WORKFLOW_MARKER, "<!-- phase-orchestrator:workflow-complete v2 -->")
        self.assertIn("official\n`/speckit.implement`", command)
        self.assertNotIn("/speckit.implement phase", command)

    def test_issues_tracker_is_git_material_excluded_from_payload(self) -> None:
        ignore = EXTENSION_IGNORE.read_text(encoding="utf-8").splitlines()
        tracker = ISSUES_TRACKER.read_text(encoding="utf-8")
        publication = PUBLICATION_PLAN.read_text(encoding="utf-8")

        self.assertIn("issues-tracker.md", ignore)
        for heading in [
            "## Current Extension Direction",
            "## Issue Index",
            "## Issue Records",
            "## Direction History",
            "## Open Follow-ups",
        ]:
            self.assertIn(heading, tracker)
        for issue_id in ["PO-001", "PO-002"]:
            self.assertIn(issue_id, tracker)
        for status in ["Open", "Addressed", "Validated"]:
            self.assertIn(status, tracker)
        self.assertIn("issues-tracker.md", publication)
        self.assertIn("must not be included in an installed extension payload", publication)

    def test_pending_release_docs_target_v2_1_and_preserve_v2_0_history(self) -> None:
        submission = SUBMISSION_NOTES.read_text(encoding="utf-8")
        publication = PUBLICATION_PLAN.read_text(encoding="utf-8")

        self.assertIn("Version: `2.1.0`", submission)
        self.assertIn("tags/v2.1.0.zip", submission)
        self.assertIn("All 84 unit and contract tests passed", submission)
        self.assertIn("Historical v2.0.0 pre-release verification", submission)
        self.assertIn("superseded evidence", submission)
        self.assertIn("release as `v2.1.0`", publication)
        self.assertIn("GitHub Release v2.1.0", publication)
        self.assertIn("historical `v2.0.0` pre-release evidence is superseded", publication)

    def test_documentation_examples_do_not_surface_removed_artifacts(self) -> None:
        public_paths = [
            ROOT / "README.md",
            ROOT / "docs" / "usage.md",
            ROOT / "docs" / "examples.md",
            ROOT / "docs" / "agent-support.md",
            ROOT / "docs" / "submission-notes.md",
            ROOT / "commands" / "speckit.phase-orchestrator.phase.md",
            ROOT / "references" / "phase-doc-template.md",
            ROOT / "references" / "worker-prompt-template.md",
            ROOT / "examples" / "sample-phase-handoff.json",
        ]
        old_name = "rece" + "ipt"
        removed_doc_path = re.compile(rf"Documentation/[^\s`\"]+{old_name}\.json")
        removed_fragments = [
            f"{old_name}_path",
            f"{old_name}_required",
            f"phase-{old_name}.schema.json",
            f"sample-phase-{old_name}.json",
        ]

        for path in public_paths:
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(removed_doc_path.search(text), path)
            for fragment in removed_fragments:
                self.assertNotIn(fragment, text, path)
            self.assertNotIn("optional Phase Flow", text, path)
            self.assertNotIn("based on the dark/emerald", text, path)
            self.assertNotIn("python3 -m unittest .specify", text, path)

if __name__ == "__main__":
    unittest.main()
