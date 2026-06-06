from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import phase_tasks


SAMPLE_TASKS = ROOT / "examples" / "sample-tasks.md"
FIVE_PHASE_TASKS = ROOT / "examples" / "five-phase-tasks.md"
SCRIPT = ROOT / "scripts" / "phase_tasks.py"
MERMAID_STYLE = ROOT / "references" / "mermaid-style.md"
PHASE_DOC_TEMPLATE = ROOT / "references" / "phase-doc-template.md"
WORKER_PROMPT_TEMPLATE = ROOT / "references" / "worker-prompt-template.md"
RECEIPT_SCHEMA = ROOT / "schemas" / "phase-receipt.schema.json"
SAMPLE_RECEIPT = ROOT / "examples" / "sample-phase-receipt.json"


def style_lines(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip().startswith(("classDef ", "linkStyle "))
    ]


def worker_prompt_body(template: str) -> str:
    return template.split("```text\n", 1)[1].split(
        "\n```\n\n## Sanitization Rules", 1
    )[0]


def render_worker_prompt_for_phase_four() -> str:
    selected = phase_tasks.build_output(FIVE_PHASE_TASKS, "phase", 4)["selected_phase"]
    replacements = {
        "[REPO_ROOT]": str(ROOT),
        "[SANITIZED_PHASE_BRIEF]": "Complete Phase 4 review item work only.",
        "[SANITIZED_PARENT_CONTEXT]": "None",
        "[TASKS_PATH]": "examples/five-phase-tasks.md",
        "[MODE]": "phase",
        "[PHASE_NUMBER]": str(selected["number"]),
        "[PHASE_TITLE]": selected["title"],
        "[PURPOSE_OR_OMIT]": selected["purpose"] or "Omit",
        "[CHECKPOINT_OR_OMIT]": selected["checkpoint"] or "Omit",
        "[INDEPENDENT_TEST_OR_OMIT]": selected["independent_test"] or "Omit",
        "[ASSIGNED_TASK_IDS]": ", ".join(selected["incomplete_task_ids"]),
        "[TEST_TASKS]": "\n".join(
            f"- {task['id']}: {task['text']}" for task in selected["test_tasks"]
        ),
        "[IMPLEMENTATION_TASKS]": "\n".join(
            f"- {task['id']}: {task['text']}"
            for task in selected["implementation_tasks"]
        ),
        "[PREVIOUS_PHASE_DOCS_OR_OMIT]": "None",
        "[VALIDATION_EXPECTATIONS]": "Run focused Phase 4 review item tests.",
        "[RELEVANT_SKILLS_OR_OMIT]": "None",
        "[REFERENCE_SUMMARIES_OR_OMIT]": "None",
        "[MERMAID_STYLE_REFERENCE]": MERMAID_STYLE.read_text(encoding="utf-8"),
        "[MCP_NOTES_OR_OMIT]": "None",
        "[DOCUMENTATION_PATH]": selected["documentation_path"],
        "[RECEIPT_PATH]": selected["receipt_path"],
    }
    prompt = worker_prompt_body(WORKER_PROMPT_TEMPLATE.read_text(encoding="utf-8"))
    for placeholder, value in replacements.items():
        prompt = prompt.replace(placeholder, value)
    return prompt


def validate_receipt_schema(instance: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    def matches_type(value: Any, expected: str) -> bool:
        if expected == "object":
            return isinstance(value, dict)
        if expected == "array":
            return isinstance(value, list)
        if expected == "string":
            return isinstance(value, str)
        if expected == "integer":
            return type(value) is int
        if expected == "null":
            return value is None
        return True

    def validate(value: Any, rule: dict[str, Any], path: str) -> None:
        expected_type = rule.get("type")
        if expected_type is not None:
            expected_types = (
                expected_type if isinstance(expected_type, list) else [expected_type]
            )
            if not any(matches_type(value, expected) for expected in expected_types):
                errors.append(f"{path}: wrong type")
                return

        if "const" in rule and value != rule["const"]:
            errors.append(f"{path}: wrong const")
        if "enum" in rule and value not in rule["enum"]:
            errors.append(f"{path}: not in enum")
        if isinstance(value, str):
            if len(value) < rule.get("minLength", 0):
                errors.append(f"{path}: too short")
            if "pattern" in rule and not re.search(rule["pattern"], value):
                errors.append(f"{path}: pattern mismatch")

        if isinstance(value, dict):
            properties = rule.get("properties", {})
            for required_key in rule.get("required", []):
                if required_key not in value:
                    errors.append(f"{path}.{required_key}: missing")
            if rule.get("additionalProperties") is False:
                for extra_key in sorted(set(value) - set(properties)):
                    errors.append(f"{path}.{extra_key}: additional property")
            for key, child_rule in properties.items():
                if key in value:
                    validate(value[key], child_rule, f"{path}.{key}")

        if isinstance(value, list) and "items" in rule:
            for index, item in enumerate(value):
                validate(item, rule["items"], f"{path}[{index}]")

    validate(instance, schema, "$")
    return errors


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
            selected["receipt_path"],
            ".specify/phase-orchestrator/receipts/example-application-document-workspace/phase-3-user-story-1-start-or-resume-a-package-priority-p1-receipt.json",
        )

    def test_default_documentation_paths_use_feature_slug(self) -> None:
        output = phase_tasks.build_output(SAMPLE_TASKS, "next", 3)
        selected = output["selected_phase"]

        self.assertEqual(output["feature_slug"], "example-application-document-workspace")
        self.assertEqual(
            selected["documentation_path"],
            "Documentation/example-application-document-workspace/phase-3-user-story-1-start-or-resume-a-package-priority-p1-execution.md",
        )
        self.assertEqual(
            selected["receipt_path"],
            ".specify/phase-orchestrator/receipts/example-application-document-workspace/phase-3-user-story-1-start-or-resume-a-package-priority-p1-receipt.json",
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

    def test_mermaid_style_uses_readable_node_fill(self) -> None:
        text = MERMAID_STYLE.read_text(encoding="utf-8")

        self.assertIn("fill:#161616", text)
        self.assertNotIn("#000000", text)

    def test_phase_doc_template_mermaid_snippet_matches_style_reference(self) -> None:
        style = MERMAID_STYLE.read_text(encoding="utf-8")
        template = PHASE_DOC_TEMPLATE.read_text(encoding="utf-8")

        self.assertIn("required styled Phase Flow Mermaid diagram", template)
        for line in style_lines(style):
            self.assertIn(line, template)
        self.assertNotIn("#000000", template)

    def test_worker_prompt_requires_styled_phase_flow_and_reference(self) -> None:
        template = WORKER_PROMPT_TEMPLATE.read_text(encoding="utf-8")

        self.assertIn("[MERMAID_STYLE_REFERENCE]", template)
        self.assertIn("required styled Phase Flow Mermaid diagram", template)
        self.assertIn("Copy the provided dark/emerald Mermaid", template)
        self.assertNotIn("optional styled Phase", template)

    def test_rendered_worker_handoff_includes_mermaid_reference_and_is_sanitized(self) -> None:
        prompt = render_worker_prompt_for_phase_four()

        for line in style_lines(MERMAID_STYLE.read_text(encoding="utf-8")):
            self.assertIn(line, prompt)
        self.assertIn("T005", prompt)
        self.assertIn("T006", prompt)
        for excluded_task_id in ["T001", "T002", "T003", "T004", "T007"]:
            self.assertNotIn(excluded_task_id, prompt)
        for parent_only_text in [
            "Codex 5.3",
            "medium effort",
            "Use exactly one worker",
            "post-phase staging",
            "run mode `all`",
        ]:
            self.assertNotIn(parent_only_text, prompt)

    def test_receipt_schema_accepts_snake_case_and_rejects_ad_hoc_keys(self) -> None:
        schema = json.loads(RECEIPT_SCHEMA.read_text(encoding="utf-8"))
        valid = json.loads(SAMPLE_RECEIPT.read_text(encoding="utf-8"))

        self.assertEqual(validate_receipt_schema(valid, schema), [])

        for ad_hoc_key in [
            "completedTaskIds",
            "changedFiles",
            "generatedAt",
            "name",
            "priority",
        ]:
            invalid = copy.deepcopy(valid)
            invalid[ad_hoc_key] = "unexpected"
            self.assertTrue(validate_receipt_schema(invalid, schema), ad_hoc_key)

            invalid_phase = copy.deepcopy(valid)
            invalid_phase["phase"][ad_hoc_key] = "unexpected"
            self.assertTrue(validate_receipt_schema(invalid_phase, schema), ad_hoc_key)

    def test_documentation_examples_do_not_surface_receipts_as_docs(self) -> None:
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
            ROOT / "examples" / "sample-phase-receipt.json",
        ]
        receipt_doc_path = re.compile(r"Documentation/[^\s`\"]+receipt\.json")

        for path in public_paths:
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(receipt_doc_path.search(text), path)
            self.assertNotIn("optional Phase Flow", text, path)
            self.assertNotIn("based on the dark/emerald", text, path)
            self.assertNotIn("python3 -m unittest .specify", text, path)

if __name__ == "__main__":
    unittest.main()
