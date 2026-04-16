import json
import unittest
from datetime import date
from pathlib import Path

from fixit_ai.small_model_review import (
    audit_phase2_conditions,
    build_deployment_review,
    build_evidence_ledger,
    build_final_verdict,
    build_guardrail_bars,
    build_hard_case_taxonomy,
    build_model_option_matrix,
    build_readiness_rubric,
    render_review_markdown,
)

ROOT = Path(__file__).resolve().parents[1]


class SmallModelReviewTests(unittest.TestCase):
    def test_readiness_rubric_freezes_phase2_conditions_and_verdicts(self):
        rubric = build_readiness_rubric()
        criterion_ids = {item["criterion_id"] for item in rubric["criteria"]}
        self.assertEqual(
            criterion_ids,
            {
                "schema_stability_2_to_4_weeks",
                "teacher_judgement_volume_sufficient",
                "baseline_recall_ceiling_clear",
                "hard_cases_are_small_model_worthy",
                "local_budget_latency_and_rollback_ready",
            },
        )
        self.assertEqual(set(rubric["verdict_standards"].keys()), {"go", "not-yet", "no-go"})

    def test_evidence_ledger_reads_existing_artifacts(self):
        ledger = build_evidence_ledger(ROOT, reference_date=date(2026, 4, 16))
        self.assertEqual(ledger["schema_stability_days"], 0)
        self.assertEqual(ledger["teacher_reviewed_count"], 1)
        self.assertEqual(ledger["teacher_fallback_count"], 1)
        self.assertEqual(ledger["pilot_service_count"], 1)
        self.assertEqual(ledger["replay_dataset_count"], 9)
        self.assertGreaterEqual(ledger["outcome_total"], 8)

    def test_phase2_audit_marks_current_repo_not_yet_ready(self):
        rubric = build_readiness_rubric()
        ledger = build_evidence_ledger(ROOT, reference_date=date(2026, 4, 16))
        hard_cases = build_hard_case_taxonomy(ROOT)
        deployment = build_deployment_review(ledger)
        audit = audit_phase2_conditions(rubric, ledger, hard_cases, deployment)

        statuses = {item["criterion_id"]: item["status"] for item in audit["criteria"]}
        self.assertEqual(statuses["schema_stability_2_to_4_weeks"], "unmet")
        self.assertEqual(statuses["teacher_judgement_volume_sufficient"], "unmet")
        self.assertEqual(statuses["baseline_recall_ceiling_clear"], "partial")
        self.assertEqual(statuses["hard_cases_are_small_model_worthy"], "unmet")
        self.assertEqual(statuses["local_budget_latency_and_rollback_ready"], "unmet")

    def test_hard_case_taxonomy_and_model_option_matrix_prefer_review_not_implementation(self):
        ledger = build_evidence_ledger(ROOT, reference_date=date(2026, 4, 16))
        hard_cases = build_hard_case_taxonomy(ROOT)
        option_matrix = build_model_option_matrix(ledger, hard_cases)
        recommendations = {item["option_id"]: item["recommendation"] for item in option_matrix["options"]}
        self.assertEqual(hard_cases["semantic_failure_count"], 0)
        self.assertGreaterEqual(hard_cases["review_gap_count"], 1)
        self.assertEqual(recommendations["small_encoder_classifier"], "future_candidate")
        self.assertEqual(recommendations["small_instruct_reranker"], "defer")
        self.assertEqual(option_matrix["preferred_current_path"], "keep_baseline_and_accumulate_data")

    def test_final_verdict_is_not_yet_and_points_to_data_teacher_accumulation(self):
        rubric = build_readiness_rubric()
        ledger = build_evidence_ledger(ROOT, reference_date=date(2026, 4, 16))
        hard_cases = build_hard_case_taxonomy(ROOT)
        deployment = build_deployment_review(ledger)
        audit = audit_phase2_conditions(rubric, ledger, hard_cases, deployment)
        option_matrix = build_model_option_matrix(ledger, hard_cases)
        verdict = build_final_verdict(audit, option_matrix, deployment)
        self.assertEqual(verdict["verdict"], "not-yet")
        self.assertEqual(verdict["recommended_successor"], "ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION")

    def test_guardrail_bars_freeze_success_and_rollback_expectations(self):
        ledger = build_evidence_ledger(ROOT, reference_date=date(2026, 4, 16))
        hard_cases = build_hard_case_taxonomy(ROOT)
        option_matrix = build_model_option_matrix(ledger, hard_cases)
        deployment = build_deployment_review(ledger)
        bars = build_guardrail_bars(ledger, option_matrix, deployment)
        self.assertIn("success_bar", bars)
        self.assertIn("rollback_bar", bars)
        self.assertGreaterEqual(bars["success_bar"]["offline_recall_floor"], ledger["severe_recall"])
        self.assertGreaterEqual(bars["rollback_bar"]["fallback_rate_ceiling"], 0)

    def test_markdown_renderer_contains_key_review_sections(self):
        rubric = build_readiness_rubric()
        ledger = build_evidence_ledger(ROOT, reference_date=date(2026, 4, 16))
        hard_cases = build_hard_case_taxonomy(ROOT)
        deployment = build_deployment_review(ledger)
        audit = audit_phase2_conditions(rubric, ledger, hard_cases, deployment)
        option_matrix = build_model_option_matrix(ledger, hard_cases)
        bars = build_guardrail_bars(ledger, option_matrix, deployment)
        verdict = build_final_verdict(audit, option_matrix, deployment)
        markdown = render_review_markdown(rubric, ledger, audit, hard_cases, option_matrix, deployment, verdict, bars)
        self.assertIn("## Readiness Rubric", markdown)
        self.assertIn("## Evidence Ledger", markdown)
        self.assertIn("## Phase-2 Condition Audit", markdown)
        self.assertIn("## Hard-case Taxonomy", markdown)
        self.assertIn("## Deployment and Guardrails", markdown)
        self.assertIn("## Acceptance and Rollback Bars", markdown)
        self.assertIn("## Final Verdict", markdown)


if __name__ == "__main__":
    unittest.main()
