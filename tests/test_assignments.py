from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import phase_tasks
from scripts.validate_assignments import validate_assignments

ROOT = Path(__file__).resolve().parents[1]
SOURCE = """# Tasks: Invariants

## Phase 2: Storage
### Tests First
- [ ] T010 Deliver SQL migration in `migrations/010.sql`
  Verify using `pytest tests/test_invariants.py`.
- [ ] T011 Write invariant regression tests in `tests/test_invariants.py`
- [X] T012 Create database configuration

## Phase 3: Later
- [ ] T013 Wire application
"""


class AssignmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "tasks.md"
        self.path.write_text(SOURCE)
        self.output = phase_tasks.build_output(self.path, "next", 2)
        self.manifest = {
            "schema_version": "1.0.0", "phase_number": 2,
            "inventory_digest": self.output["inventory_digest"],
            "revision": 1, "reason": "Initial classification",
            "assignments": [
                {"id": "T010", "stage": "implementation", "rationale": "Delivers SQL migration; pytest verifies it."},
                {"id": "T011", "stage": "test", "rationale": "Delivers regression tests."},
                {"id": "T012", "stage": "implementation", "rationale": "Delivers database configuration."},
            ],
        }

    def test_migration_is_not_classified_by_parser(self):
        phase = self.output["selected_phase"]
        self.assertEqual(phase["next_stage"], "classification")
        for key in ("test_tasks", "implementation_tasks", "tests_first_tasks"):
            self.assertNotIn(key, phase)
        self.assertIn("pytest tests/test_invariants.py", phase["tasks"][0]["text"])
        result = validate_assignments(self.output, self.manifest)
        self.assertEqual([t["id"] for t in result["implementation_tasks"]], ["T010"])
        self.assertEqual([t["id"] for t in result["test_tasks"]], ["T011"])

    def test_invalid_assignments_rejected(self):
        variants = []
        for key, value in (("phase_number", 3), ("revision", 0), ("revision", True),
                           ("reason", " "), ("schema_version", "old"),
                           ("inventory_digest", "stale"), ("assignments", None)):
            m = copy.deepcopy(self.manifest); m[key] = value; variants.append(m)
        for entries in (self.manifest["assignments"][:-1],
                        self.manifest["assignments"] * 2):
            m = copy.deepcopy(self.manifest); m["assignments"] = entries; variants.append(m)
        for key, value in (("id", "T013"), ("stage", "verification"), ("rationale", "")):
            m = copy.deepcopy(self.manifest); m["assignments"][0][key] = value; variants.append(m)
        for m in variants:
            with self.subTest(manifest=m), self.assertRaises(ValueError):
                validate_assignments(self.output, m)

    def test_resume_filters_checked_tasks_without_reclassifying(self):
        self.path.write_text(SOURCE.replace("[ ] T011", "[X] T011"))
        output = phase_tasks.build_output(self.path, "next", 2)
        result = validate_assignments(output, self.manifest)
        self.assertEqual(result["next_stage"], "implementation")
        self.assertEqual(result["test_tasks"], [])
        self.path.write_text(SOURCE.replace("[ ]", "[X]"))
        output = phase_tasks.build_output(self.path, "next", 2)
        self.assertEqual(validate_assignments(output, self.manifest)["next_stage"], "verification")

    def test_source_drift_including_context_rejected(self):
        for source in (SOURCE.replace("SQL migration", "SQL index"),
                       SOURCE + "\nDependency: wait for schema approval.\n",
                       SOURCE.replace("T010", "T014")):
            self.path.write_text(source)
            output = phase_tasks.build_output(self.path, "next", 2)
            with self.assertRaisesRegex(ValueError, "source changed"):
                validate_assignments(output, self.manifest)

    def test_duplicate_source_ids_and_unphased_tasks_rejected(self):
        for source in (SOURCE.replace("T013", "T010"), "- [ ] T001 Orphan\n" + SOURCE):
            self.path.write_text(source)
            with self.assertRaises(ValueError):
                phase_tasks.build_output(self.path, "next", 2)

    def test_correction_can_reassign_and_reopen_task(self):
        corrected = copy.deepcopy(self.manifest)
        corrected.update(revision=2, reason="T012 is test-only configuration; reopen unsupported completion")
        corrected["assignments"][2].update(stage="test", rationale="Configures test harness only")
        self.path.write_text(SOURCE.replace("[X] T012", "[ ] T012"))
        result = validate_assignments(phase_tasks.build_output(self.path, "next", 2), corrected)
        self.assertEqual([t["id"] for t in result["test_tasks"]], ["T011", "T012"])
        self.assertEqual(result["revision"], 2)

    def test_cli_accepts_manifest_and_rejects_invalid_json(self):
        manifest_path = Path(self.tmp.name) / "assignments.json"
        manifest_path.write_text(json.dumps(self.manifest))
        command = [sys.executable, str(ROOT / "scripts/validate_assignments.py"),
                   str(self.path), str(manifest_path), "--phase", "2"]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["next_stage"], "test")
        manifest_path.write_text("{")
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)

    def test_empty_phase_and_documented_phase_have_no_dispatch(self):
        self.path.write_text("# Tasks: Empty\n## Phase 2: Empty\n")
        output = phase_tasks.build_output(self.path, "next", 2)
        manifest = {**self.manifest, "inventory_digest": output["inventory_digest"], "assignments": []}
        self.assertEqual(validate_assignments(output, manifest)["next_stage"], "verification")
        document = Path(self.tmp.name) / "execution.md"
        document.write_text(phase_tasks.WORKFLOW_COMPLETE_MARKER)
        output = phase_tasks.build_output(self.path, "next", 2, explicit_docs_path=document)
        self.assertIsNone(validate_assignments(output, manifest)["next_stage"])

    def test_prompt_contract_preserves_semantic_authority_and_correction(self):
        command = " ".join((ROOT / "commands/speckit.phase-orchestrator.phase.md").read_text().split())
        for requirement in (
            "parent has full authority over semantic classification",
            "Classify each task in that phase by its primary deliverable",
            "Assign each task to exactly one role based on its primary deliverable",
            "Commands that run tests to verify implementation do not make that task a test-authoring task",
            "resolve that ambiguity before dispatch",
            "Before dispatch and on resume",
            "Reconcile incorrectly checked tasks against actual deliverables",
            "Correcting a mistaken task assignment does not consume a remediation attempt",
            "Repairs requested by the verifier still follow the normal remediation limit",
            "verifier must check actual requested deliverables",
        ):
            self.assertIn(requirement, command)

    def test_assignment_clarification_is_separate_from_final_report(self):
        command = " ".join((ROOT / "commands/speckit.phase-orchestrator.phase.md").read_text().split())
        worker = " ".join((ROOT / "references/worker-prompt-template.md").read_text().split())
        for requirement in (
            "If the assignment is correct, send the explanation as a follow-up to the same worker",
            "not a completed stage report or a stage transition",
            "If the assignment is incorrect, correct it",
            "dispatch the work to the appropriate role",
            "clarification exchange is separate from the final stage report",
        ):
            self.assertIn(requirement, command)
        for requirement in (
            "end your current turn with a brief clarification question identifying the task and reason",
            "This question is not your final stage report",
            "At the end of the stage, return only one completed instance",
        ):
            self.assertIn(requirement, worker)
        clarification = command.split("### Assignment Correction", 1)[1].split("The parent archives", 1)[0]
        self.assertNotIn("`blocked`", clarification)
        self.assertNotIn("`caveats`", clarification)
