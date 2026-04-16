import unittest
from datetime import date
from pathlib import Path

from fixit_ai.common import read_yaml
from fixit_ai.data_teacher_accumulation import (
    build_accumulation_baseline,
    build_family_closeout,
    build_phase2_refresh,
    build_replay_coverage,
    build_schema_stability_history,
    build_target_ledger,
    build_teacher_accumulation_ledger,
    render_accumulation_report,
    render_family_closeout_markdown,
    render_phase2_refresh_markdown,
)
from fixit_ai.replay_pack import refresh_replay_pack

ROOT = Path(__file__).resolve().parents[1]


class DataTeacherAccumulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.replay_cfg = read_yaml(ROOT / "configs/replay-pack.yaml")
        refresh_replay_pack(cls.replay_cfg, ROOT, generated_at="2026-04-16T16:00:00Z")

    def test_replay_coverage_reports_multi_pilot_after_dw1_refresh(self):
        coverage = build_replay_coverage(ROOT)
        self.assertEqual(coverage["pilot_service_count"], 2)
        self.assertEqual(
            coverage["services"],
            ["g-crm-campaign", "prod-hq-bff-service"],
        )
        self.assertEqual(coverage["metrics_window_count"], 12)
        self.assertEqual(coverage["topology_service_count"], 2)

    def test_baseline_reads_multi_pilot_replay_and_recommends_dw2(self):
        baseline = build_accumulation_baseline(ROOT, reference_date=date(2026, 4, 16))
        targets = build_target_ledger(baseline)
        self.assertEqual(baseline["predecessor_family"], "LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW")
        self.assertEqual(baseline["predecessor_verdict"], "not-yet")
        self.assertEqual(baseline["recommended_successor"], "ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION")
        self.assertEqual(baseline["pilot_service_count"], 2)
        self.assertEqual(baseline["teacher_request_count"], 2)
        self.assertEqual(baseline["teacher_reviewed_count"], 1)
        self.assertEqual(baseline["teacher_fallback_count"], 1)
        self.assertEqual(targets["recommended_next_slice"], "DW2.S1_TEACHER_REVIEW_BATCH_AND_LABEL_SOURCE_EXPANSION")
        self.assertEqual(targets["workstreams"]["DW1"]["pilot_service_count_gap"], 0)

    def test_teacher_accumulation_ledger_exceeds_predecessor_baseline(self):
        ledger = build_teacher_accumulation_ledger(ROOT)
        self.assertEqual(ledger["predecessor_teacher_reviewed_count"], 1)
        self.assertEqual(ledger["current_teacher_reviewed_count"], 2)
        self.assertEqual(ledger["teacher_reviewed_delta"], 1)
        self.assertEqual(ledger["current_teacher_packet_ids"], ["ipk_w004", "ipk_w006"])
        self.assertEqual(ledger["label_teacher_rubric_count"], 1)
        self.assertEqual(ledger["teacher_label_gap"], 1)

    def test_schema_stability_history_and_phase2_refresh_freeze_not_yet(self):
        baseline = build_accumulation_baseline(ROOT, reference_date=date(2026, 4, 16))
        teacher_ledger = build_teacher_accumulation_ledger(ROOT)
        history = build_schema_stability_history(ROOT, reference_date=date(2026, 4, 16))
        refresh = build_phase2_refresh(ROOT, baseline, teacher_ledger, history)
        self.assertEqual(history["current_elapsed_days"], 0)
        self.assertGreaterEqual(history["schema_file_count"], 3)
        statuses = {item["criterion_id"]: item["status"] for item in refresh["criteria"]}
        self.assertEqual(statuses["multi_pilot_replay_coverage"], "met")
        self.assertEqual(statuses["teacher_reviewed_volume_growth"], "partial")
        self.assertEqual(statuses["schema_stability_window"], "unmet")
        self.assertEqual(refresh["verdict"], "not-yet")
        self.assertEqual(refresh["recommended_successor"], "ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP")

    def test_family_closeout_requires_followup_successor(self):
        baseline = build_accumulation_baseline(ROOT, reference_date=date(2026, 4, 16))
        teacher_ledger = build_teacher_accumulation_ledger(ROOT)
        history = build_schema_stability_history(ROOT, reference_date=date(2026, 4, 16))
        refresh = build_phase2_refresh(ROOT, baseline, teacher_ledger, history)
        closeout = build_family_closeout(baseline, teacher_ledger, history, refresh)
        self.assertEqual(closeout["family_verdict"], "accept_with_residuals")
        self.assertEqual(closeout["recommended_successor"], "ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP")
        self.assertIn("teacher volume still below phase-2 threshold", closeout["residuals"])

    def test_markdown_reports_contain_current_sections(self):
        baseline = build_accumulation_baseline(ROOT, reference_date=date(2026, 4, 16))
        targets = build_target_ledger(baseline)
        teacher_ledger = build_teacher_accumulation_ledger(ROOT)
        history = build_schema_stability_history(ROOT, reference_date=date(2026, 4, 16))
        refresh = build_phase2_refresh(ROOT, baseline, teacher_ledger, history)
        closeout = build_family_closeout(baseline, teacher_ledger, history, refresh)
        accumulation_markdown = render_accumulation_report(baseline, targets)
        phase2_markdown = render_phase2_refresh_markdown(refresh)
        closeout_markdown = render_family_closeout_markdown(closeout)
        self.assertIn("## Current Baseline", accumulation_markdown)
        self.assertIn("recommended next slice", accumulation_markdown)
        self.assertIn("DW2.S1_TEACHER_REVIEW_BATCH_AND_LABEL_SOURCE_EXPANSION", accumulation_markdown)
        self.assertIn("## Phase-2 Refresh Verdict", phase2_markdown)
        self.assertIn("ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP", phase2_markdown)
        self.assertIn("## Family Verdict", closeout_markdown)
        self.assertIn("accept_with_residuals", closeout_markdown)


if __name__ == "__main__":
    unittest.main()
