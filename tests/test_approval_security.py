"""
Test Suite for Approval Gate Security, Identity Assertion & Revision Invalidation (Milestone 8).

Validates:
1. Rejection of AI agent and automated bot self-approval attempts.
2. Rejection of placeholder/demo identities (Jane Doe, John Doe, etc.) in production mode.
3. Acceptance of genuine human reviewer identity assertions.
4. Auditable decision logging and plain-text assertion warnings.
5. Invalidation of approvals upon post-approval geometry tampering.
6. Approval integrity verification helper functions.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.sketch_interpreter import (
    load_sketch_input,
    validate_observations,
    reconstruct_geometry,
    compile_draft_model,
)
from scripts.approval_package import (
    create_approval_package,
    apply_review_decision,
    calculate_geometry_hash,
    verify_approval_integrity,
)

FIXTURES_DIR = Path("tests/fixtures/sketches")
SAMPLE_OBS_PATH = FIXTURES_DIR / "fixture-a-observations.json"


class TestApprovalSecurity(unittest.TestCase):
    """Security and integrity tests for the human approval gate."""

    @classmethod
    def setUpClass(cls):
        with open(SAMPLE_OBS_PATH, "r", encoding="utf-8") as f:
            cls.obs = json.load(f)
        cls.geom = reconstruct_geometry(cls.obs)
        cls.draft = compile_draft_model(cls.obs, cls.geom, project_name="Security Test Residence")

    def setUp(self):
        # Create fresh draft and package for each test
        self.draft_model = json.loads(json.dumps(self.draft))
        self.package = create_approval_package(self.draft_model, self.obs)

    def test_01_agent_self_approval_strictly_prohibited(self):
        agent_names = [
            "AI Assistant",
            "antigravity-bot",
            "System Agent",
            "Auto Bot",
            "LLM Generator",
            "sketch-to-cad AI",
        ]
        for bad_name in agent_names:
            with self.subTest(reviewer=bad_name):
                with self.assertRaises(PermissionError) as ctx:
                    apply_review_decision(
                        self.package,
                        self.draft_model,
                        {"reviewer_name": bad_name, "action": "approve"},
                        allow_demo_identities=True,
                    )
                self.assertIn("Self-approval rejected", str(ctx.exception))

    def test_02_placeholder_demo_identities_rejected_in_production(self):
        placeholder_names = [
            "Jane Doe, Licensed Architect",
            "John Doe",
            "Demo Reviewer",
            "Sample User",
            "Placeholder Architect",
            "Test User",
        ]
        for demo_name in placeholder_names:
            with self.subTest(reviewer=demo_name):
                with self.assertRaises(ValueError) as ctx:
                    apply_review_decision(
                        self.package,
                        self.draft_model,
                        {"reviewer_name": demo_name, "action": "approve"},
                        allow_demo_identities=False,  # Strict production mode
                    )
                self.assertIn("Placeholder reviewer identity", str(ctx.exception))

    def test_03_genuine_human_approval_accepted(self):
        decision = {
            "reviewer_name": "Marcus Vance, Principal Architect (AIA #98214)",
            "action": "approve",
            "details": {"notes": "Approved for CAD drafting and municipal permit filing."},
        }
        pkg_app, model_app = apply_review_decision(
            self.package,
            self.draft_model,
            decision,
            allow_demo_identities=False,
        )
        self.assertEqual(pkg_app["status"], "approved")
        self.assertEqual(model_app["status"], "approved")
        meta = pkg_app["approval_metadata"]
        self.assertEqual(meta["approved_by"], "Marcus Vance, Principal Architect (AIA #98214)")
        self.assertEqual(meta["auth_method"], "identity_assertion")
        self.assertIn("plain-text assertion", meta["auth_note"])

    def test_04_decision_log_auditability(self):
        decision = {
            "reviewer_name": "Dr. Sarah Lin, PE",
            "action": "correct_dimension",
            "details": {"target_id": "DIM-OVERALL-WIDTH", "new_value_mm": 6200.0},
        }
        pkg, model = apply_review_decision(
            self.package,
            self.draft_model,
            decision,
            allow_demo_identities=False,
        )
        self.assertGreater(len(pkg["decisions_log"]), 0)
        last_log = pkg["decisions_log"][-1]
        self.assertEqual(last_log["reviewer_name"], "Dr. Sarah Lin, PE")
        self.assertEqual(last_log["action"], "correct_dimension")
        self.assertIn("timestamp", last_log)

    def test_05_geometry_tampering_invalidates_approval(self):
        # 1. Human approves proposal
        decision = {
            "reviewer_name": "Liam Thorne, Project Architect",
            "action": "approve",
            "details": {"notes": "Initial approval."},
        }
        pkg_app, model_app = apply_review_decision(
            self.package,
            self.draft_model,
            decision,
            allow_demo_identities=False,
        )
        self.assertEqual(pkg_app["status"], "approved")

        # 2. Verify integrity before tampering
        is_ok, msg = verify_approval_integrity(pkg_app, model_app)
        self.assertTrue(is_ok, msg)

        # 3. Tamper with model geometry (change width by 100mm)
        tampered_model = json.loads(json.dumps(model_app))
        tampered_model["envelope"]["width"] = 6100.0

        # 4. Verify integrity must fail
        is_tampered_ok, tampered_msg = verify_approval_integrity(pkg_app, tampered_model)
        self.assertFalse(is_tampered_ok)
        self.assertIn("altered", tampered_msg)

    def test_06_unapproved_model_rejection_in_pipeline(self):
        # If model status is awaiting_approval or rejected, verify_approval_integrity returns False
        unapproved_pkg = dict(self.package)
        unapproved_pkg["status"] = "awaiting_approval"
        is_ok, msg = verify_approval_integrity(unapproved_pkg, self.draft_model)
        self.assertFalse(is_ok)
        self.assertIn("not 'approved'", msg)


if __name__ == "__main__":
    unittest.main()
