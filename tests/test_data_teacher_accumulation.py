import json
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

from fixit_ai.common import read_yaml
from fixit_ai.data_teacher_accumulation import (
    build_accumulation_baseline,
    build_family_closeout,
    build_followup_family_closeout,
    build_human_writeback_audit,
    build_phase2_refresh,
    build_replay_coverage,
    build_residual_phase2_recheck,
    build_runtime_baseline,
    build_schema_dayspan_progress,
    build_schema_stability_history,
    build_stability_volume_residual_closeout,
    build_target_ledger,
    build_teacher_accumulation_ledger,
    build_teacher_daily_review_batch,
    build_volume_capacity,
    render_accumulation_report,
    render_family_closeout_markdown,
    render_human_writeback_audit_markdown,
    render_phase2_refresh_markdown,
    render_runtime_baseline_markdown,
    render_schema_dayspan_progress_markdown,
    render_teacher_daily_review_batch_markdown,
    render_volume_capacity_markdown,
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
        self.assertEqual(baseline["teacher_request_count"], 7)
        self.assertEqual(baseline["teacher_reviewed_count"], 7)
        self.assertEqual(baseline["teacher_fallback_count"], 0)
        self.assertEqual(targets["recommended_next_slice"], "DW2.S1_TEACHER_REVIEW_BATCH_AND_LABEL_SOURCE_EXPANSION")
        self.assertEqual(targets["workstreams"]["DW1"]["pilot_service_count_gap"], 0)

    def test_teacher_accumulation_ledger_exceeds_predecessor_baseline(self):
        ledger = build_teacher_accumulation_ledger(ROOT)
        self.assertEqual(ledger["predecessor_teacher_reviewed_count"], 1)
        self.assertEqual(ledger["current_teacher_reviewed_count"], 7)
        self.assertEqual(ledger["teacher_reviewed_delta"], 6)
        self.assertEqual(
            ledger["current_teacher_packet_ids"],
            ["ipk_w002", "ipk_w004", "ipk_w006", "ipk_w007", "ipk_w010", "ipk_w011", "ipk_w012"],
        )
        self.assertEqual(ledger["label_teacher_rubric_count"], 1)
        self.assertEqual(ledger["training_backfill_count"], 7)
        self.assertEqual(ledger["teacher_label_gap"], 0)

    def test_teacher_daily_review_batch_readout_is_script_backed(self):
        batch = build_teacher_daily_review_batch(ROOT)
        self.assertEqual(batch["selected_count"], 7)
        self.assertEqual(batch["reviewed_count"], 7)
        self.assertEqual(batch["fallback_count"], 0)
        self.assertEqual(batch["reviewed_packet_ids"], ["ipk_w002", "ipk_w004", "ipk_w006", "ipk_w007", "ipk_w010", "ipk_w011", "ipk_w012"])
        self.assertEqual(batch["remaining_to_phase2_target"], 3)

    def test_human_writeback_audit_covers_reviewed_packets(self):
        audit = build_human_writeback_audit(ROOT)
        self.assertEqual(audit["target_packet_ids"], ["ipk_w002", "ipk_w004", "ipk_w006", "ipk_w007", "ipk_w010", "ipk_w011", "ipk_w012"])
        self.assertEqual(audit["outcome_backfilled_count"], 7)
        self.assertEqual(audit["training_backfilled_count"], 7)
        self.assertEqual(audit["incident_backfilled_count"], 7)
        self.assertEqual(audit["fully_backfilled_count"], 7)
        self.assertEqual(audit["missing_outcome_packet_ids"], [])
        self.assertEqual(audit["missing_training_packet_ids"], [])
        self.assertEqual(audit["missing_incident_packet_ids"], [])

    def test_runtime_baseline_reports_allowlist_driven_multi_pilot_entry(self):
        runtime = build_runtime_baseline(ROOT)
        self.assertEqual(runtime["runtime_mode"], "multi_pilot_allowlist")
        self.assertEqual(runtime["runtime_allowlist_services"], ["g-crm-campaign", "prod-hq-bff-service"])
        self.assertEqual(runtime["observed_metric_services"], ["g-crm-campaign", "prod-hq-bff-service"])
        self.assertEqual(runtime["metrics_windows_by_service"]["prod-hq-bff-service"], 3)
        self.assertEqual(runtime["candidate_services"], ["g-crm-campaign", "prod-hq-bff-service"])
        self.assertEqual(runtime["packet_services"], ["g-crm-campaign", "prod-hq-bff-service"])
        self.assertEqual(runtime["packets_by_service"]["prod-hq-bff-service"], 3)

    def test_volume_capacity_routes_to_daily_review_append_when_ceiling_reaches_target(self):
        capacity = build_volume_capacity(ROOT)
        self.assertEqual(capacity["current_reviewed_count"], 7)
        self.assertEqual(capacity["current_packet_count"], 10)
        self.assertEqual(capacity["visible_unreviewed_remainder"], 3)
        self.assertEqual(capacity["visible_maximum_reviewed_ceiling"], 10)
        self.assertEqual(capacity["remaining_to_phase2_target"], 3)
        self.assertEqual(capacity["next_slice"], "RW2B.S1_DAILY_REVIEW_APPEND_AND_GAP_BURNDOWN")
        self.assertEqual(capacity["routing_reason"], "current bounded packet supply can clear reviewed-volume target")

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

    def test_schema_stability_history_preserves_existing_checkpoints(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir)
            shutil.copytree(ROOT / "schemas", temp_root / "schemas")
            (temp_root / "data/eval").mkdir(parents=True)
            initial = build_schema_stability_history(
                temp_root,
                reference_date=date(2026, 4, 16),
                captured_at="2026-04-16T09:00:00Z",
            )
            (temp_root / "data/eval/schema-stability-history.json").write_text(json.dumps(initial))
            history = build_schema_stability_history(
                temp_root,
                reference_date=date(2026, 4, 17),
                captured_at="2026-04-17T09:00:00Z",
            )
            self.assertEqual(len(history["snapshots"]), 2)
            self.assertEqual(history["snapshots"][0]["captured_at"], "2026-04-16T09:00:00Z")
            self.assertEqual(history["snapshots"][1]["captured_at"], "2026-04-17T09:00:00Z")
            self.assertEqual(history["current_elapsed_days"], 1)

    def test_schema_dayspan_progress_uses_distinct_dates_not_same_day_snapshot_count(self):
        progress = build_schema_dayspan_progress(ROOT, reference_date=date(2026, 4, 17))
        self.assertGreater(progress["snapshot_count"], 1)
        self.assertEqual(progress["distinct_observed_date_count"], 1)
        self.assertEqual(progress["current_elapsed_days"], 0)
        self.assertEqual(progress["remaining_days_to_target"], 14)
        self.assertEqual(progress["schema_gate_status"], "blocked")
        self.assertFalse(progress["rerun_admissible_from_schema_gate"])

    def test_family_closeout_requires_followup_successor(self):
        baseline = build_accumulation_baseline(ROOT, reference_date=date(2026, 4, 16))
        teacher_ledger = build_teacher_accumulation_ledger(ROOT)
        history = build_schema_stability_history(ROOT, reference_date=date(2026, 4, 16))
        refresh = build_phase2_refresh(ROOT, baseline, teacher_ledger, history)
        closeout = build_family_closeout(baseline, teacher_ledger, history, refresh)
        self.assertEqual(closeout["family_verdict"], "accept_with_residuals")
        self.assertEqual(closeout["recommended_successor"], "ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP")
        self.assertIn("teacher volume still below phase-2 threshold", closeout["residuals"])

    def test_followup_family_closeout_requires_new_residual_successor(self):
        baseline = build_accumulation_baseline(ROOT, reference_date=date(2026, 4, 16))
        runtime = build_runtime_baseline(ROOT)
        batch = build_teacher_daily_review_batch(ROOT)
        writeback = build_human_writeback_audit(ROOT)
        history = build_schema_stability_history(ROOT, reference_date=date(2026, 4, 16))
        refresh = build_phase2_refresh(ROOT, baseline, build_teacher_accumulation_ledger(ROOT), history)
        closeout = build_followup_family_closeout(runtime, batch, writeback, history, refresh)
        self.assertEqual(closeout["family"], "ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP")
        self.assertEqual(closeout["family_verdict"], "accept_with_residuals")
        self.assertEqual(closeout["recommended_successor"], "ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_STABILITY_AND_VOLUME_RESIDUAL")
        self.assertIn("teacher volume still below phase-2 threshold", closeout["residuals"])
        self.assertIn("schema stability window still below 14 days", closeout["residuals"])

    def test_residual_phase2_recheck_and_closeout_require_daily_schema_successor(self):
        capacity = build_volume_capacity(ROOT)
        batch = build_teacher_daily_review_batch(ROOT)
        schema_progress = build_schema_dayspan_progress(ROOT, reference_date=date(2026, 4, 17))
        recheck = build_residual_phase2_recheck(capacity, batch, schema_progress)
        closeout = build_stability_volume_residual_closeout(capacity, batch, build_human_writeback_audit(ROOT), schema_progress, recheck)
        self.assertEqual(recheck["verdict"], "not-yet")
        self.assertEqual(recheck["recommended_successor"], "ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_DAILY_VOLUME_AND_SCHEMA_RESIDUAL")
        self.assertEqual(closeout["family"], "ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_STABILITY_AND_VOLUME_RESIDUAL")
        self.assertEqual(closeout["family_verdict"], "accept_with_residuals")
        self.assertEqual(closeout["recommended_successor"], "ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_DAILY_VOLUME_AND_SCHEMA_RESIDUAL")
        self.assertIn("teacher volume still below phase-2 threshold", closeout["residuals"])
        self.assertIn("schema stability window still below 14 days", closeout["residuals"])

    def test_markdown_reports_contain_current_sections(self):
        baseline = build_accumulation_baseline(ROOT, reference_date=date(2026, 4, 16))
        targets = build_target_ledger(baseline)
        teacher_ledger = build_teacher_accumulation_ledger(ROOT)
        history = build_schema_stability_history(ROOT, reference_date=date(2026, 4, 16))
        refresh = build_phase2_refresh(ROOT, baseline, teacher_ledger, history)
        closeout = build_family_closeout(baseline, teacher_ledger, history, refresh)
        followup_closeout = build_followup_family_closeout(
            build_runtime_baseline(ROOT),
            build_teacher_daily_review_batch(ROOT),
            build_human_writeback_audit(ROOT),
            history,
            refresh,
        )
        residual_recheck = build_residual_phase2_recheck(
            build_volume_capacity(ROOT),
            build_teacher_daily_review_batch(ROOT),
            build_schema_dayspan_progress(ROOT, reference_date=date(2026, 4, 17)),
        )
        residual_closeout = build_stability_volume_residual_closeout(
            build_volume_capacity(ROOT),
            build_teacher_daily_review_batch(ROOT),
            build_human_writeback_audit(ROOT),
            build_schema_dayspan_progress(ROOT, reference_date=date(2026, 4, 17)),
            residual_recheck,
        )
        runtime = build_runtime_baseline(ROOT)
        batch = build_teacher_daily_review_batch(ROOT)
        writeback = build_human_writeback_audit(ROOT)
        volume_capacity = build_volume_capacity(ROOT)
        schema_progress = build_schema_dayspan_progress(ROOT, reference_date=date(2026, 4, 17))
        accumulation_markdown = render_accumulation_report(baseline, targets)
        phase2_markdown = render_phase2_refresh_markdown(refresh)
        closeout_markdown = render_family_closeout_markdown(closeout)
        followup_closeout_markdown = render_family_closeout_markdown(followup_closeout)
        residual_recheck_markdown = render_phase2_refresh_markdown(residual_recheck)
        residual_closeout_markdown = render_family_closeout_markdown(residual_closeout)
        runtime_markdown = render_runtime_baseline_markdown(runtime)
        batch_markdown = render_teacher_daily_review_batch_markdown(batch)
        writeback_markdown = render_human_writeback_audit_markdown(writeback)
        volume_capacity_markdown = render_volume_capacity_markdown(volume_capacity)
        schema_progress_markdown = render_schema_dayspan_progress_markdown(schema_progress)
        self.assertIn("## Current Baseline", accumulation_markdown)
        self.assertIn("recommended next slice", accumulation_markdown)
        self.assertIn("DW2.S1_TEACHER_REVIEW_BATCH_AND_LABEL_SOURCE_EXPANSION", accumulation_markdown)
        self.assertIn("## Phase-2 Refresh Verdict", phase2_markdown)
        self.assertIn("ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP", phase2_markdown)
        self.assertIn("## Family Verdict", closeout_markdown)
        self.assertIn("accept_with_residuals", closeout_markdown)
        self.assertIn("## Runtime Allowlist", runtime_markdown)
        self.assertIn("multi_pilot_allowlist", runtime_markdown)
        self.assertIn("## Daily Review Batch", batch_markdown)
        self.assertIn("remaining to phase-2 target", batch_markdown)
        self.assertIn("## Human Write-back Coverage", writeback_markdown)
        self.assertIn("fully backfilled count", writeback_markdown)
        self.assertIn("## Review Volume Capacity", volume_capacity_markdown)
        self.assertIn("RW2B.S1_DAILY_REVIEW_APPEND_AND_GAP_BURNDOWN", volume_capacity_markdown)
        self.assertIn("## Schema Day-span Progress", schema_progress_markdown)
        self.assertIn("same-day snapshots do not count as multi-day schema stability", schema_progress_markdown)
        self.assertIn("ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_STABILITY_AND_VOLUME_RESIDUAL", followup_closeout_markdown)
        self.assertIn("ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_DAILY_VOLUME_AND_SCHEMA_RESIDUAL", residual_recheck_markdown)
        self.assertIn("ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_DAILY_VOLUME_AND_SCHEMA_RESIDUAL", residual_closeout_markdown)


if __name__ == "__main__":
    unittest.main()
