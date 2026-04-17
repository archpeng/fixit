import json
import unittest
from pathlib import Path

from fixit_ai.temporal_alignment import (
    build_episode_index,
    build_temporal_alignment_summary,
    build_temporal_lineage,
    build_temporal_overlay_summary,
    build_temporal_overlays,
    run_time_aware_historical_eval,
)

ROOT = Path(__file__).resolve().parents[1]


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


class TemporalAlignmentTests(unittest.TestCase):
    def test_temporal_lineage_classifies_current_repo_time_quality(self):
        lineage = build_temporal_lineage(ROOT)
        summary = build_temporal_alignment_summary(lineage)

        self.assertEqual(summary["counts_by_timestamp_quality"]["exact_window_time"], 10)
        self.assertEqual(summary["counts_by_timestamp_quality"]["exact_time_inherited"], 34)
        self.assertEqual(summary["counts_by_timestamp_quality"]["coarse_text_time"], 2)
        self.assertEqual(summary["counts_by_timestamp_quality"]["unknown_time"], 6)
        self.assertEqual(summary["counts_by_record_type"]["packet"], 10)
        self.assertEqual(summary["counts_by_record_type"]["training_example"], 16)
        self.assertEqual(summary["exact_time_range"]["earliest"], "2026-04-16T11:25:00Z")
        self.assertEqual(summary["exact_time_range"]["latest"], "2026-04-16T12:25:00Z")

    def test_temporal_lineage_derives_exact_time_for_packet_linked_records(self):
        lineage = build_temporal_lineage(ROOT)
        by_key = {(item["record_type"], item["record_id"]): item for item in lineage}

        outcome = by_key[("outcome", "ipk_w001")]
        self.assertEqual(outcome["timestamp_quality"], "exact_time_inherited")
        self.assertEqual(outcome["derived_ts_start"], "2026-04-16T11:25:00Z")
        self.assertEqual(outcome["derived_ts_end"], "2026-04-16T11:30:00Z")
        self.assertEqual(outcome["time_source"], "packet_id")

        incident = by_key[("historical_incident", "inc-compile-500")]
        self.assertEqual(incident["timestamp_quality"], "exact_time_inherited")
        self.assertEqual(incident["derived_ts_start"], "2026-04-16T11:25:00Z")
        self.assertEqual(incident["derived_ts_end"], "2026-04-16T12:10:00Z")
        self.assertEqual(incident["time_source"], "source_packet_ids")
        self.assertEqual(incident["time_source_refs"], ["ipk_w001", "ipk_w004", "ipk_w006", "ipk_w009"])
        self.assertTrue(incident["cutoff_safe"])

    def test_temporal_lineage_marks_legacy_and_memory_records_without_fake_exact_time(self):
        lineage = build_temporal_lineage(ROOT)
        by_key = {(item["record_type"], item["record_id"]): item for item in lineage}

        legacy_training = by_key[("training_example", "tr001")]
        self.assertEqual(legacy_training["timestamp_quality"], "unknown_time")
        self.assertIsNone(legacy_training["derived_ts_start"])
        self.assertIsNone(legacy_training["derived_ts_end"])
        self.assertEqual(legacy_training["time_source"], "unlinked_training_example")
        self.assertFalse(legacy_training["cutoff_safe"])

        memory = by_key[("memory_summary", "g-crm-campaign")]
        self.assertEqual(memory["timestamp_quality"], "coarse_text_time")
        self.assertEqual(memory["time_granularity"], "month_hint")
        self.assertEqual(memory["derived_time_hints"], ["2026-02", "2026-03"])
        self.assertFalse(memory["cutoff_safe"])

    def test_temporal_overlays_make_packet_linked_history_strict_eval_ready(self):
        overlays = build_temporal_overlays(ROOT)
        summary = build_temporal_overlay_summary(overlays)

        outcomes = overlays["outcomes"]
        self.assertEqual(len(outcomes), 10)
        self.assertTrue(all(item["timestamp_quality"] == "exact_time_inherited" for item in outcomes))
        self.assertTrue(all(item["cutoff_safe"] for item in outcomes))

        teacher = overlays["manual_teacher_judgements"]
        self.assertEqual(len(teacher), 10)
        self.assertTrue(all(item["timestamp_quality"] == "exact_time_inherited" for item in teacher))

        training = overlays["training_examples"]
        training_by_id = {item["example_id"]: item for item in training}
        self.assertEqual(training_by_id["tr014"]["derived_ts_start"], "2026-04-16T11:25:00Z")
        self.assertEqual(training_by_id["tr001"]["timestamp_quality"], "unknown_time")
        self.assertFalse(training_by_id["tr001"]["cutoff_safe"])

        incidents = overlays["historical_incidents"]
        incident_by_id = {item["incident_id"]: item for item in incidents}
        self.assertEqual(incident_by_id["inc-other-service"]["derived_ts_end"], "2026-04-16T12:25:00Z")
        self.assertEqual(incident_by_id["inc-other-service"]["timestamp_quality"], "exact_time_inherited")

        self.assertEqual(summary["datasets"]["outcomes"]["strict_eval_eligible_count"], 10)
        self.assertEqual(summary["datasets"]["manual_teacher_judgements"]["strict_eval_eligible_count"], 10)
        self.assertEqual(summary["datasets"]["training_examples"]["strict_eval_eligible_count"], 10)
        self.assertEqual(summary["datasets"]["training_examples"]["train_only_count"], 6)
        self.assertEqual(summary["datasets"]["historical_incidents"]["strict_eval_eligible_count"], 4)

    def test_episode_index_and_time_aware_eval_use_cutoff_safe_temporal_truth(self):
        overlays = build_temporal_overlays(ROOT)
        episodes = build_episode_index(ROOT, overlays=overlays)
        by_id = {item["episode_id"]: item for item in episodes}

        self.assertEqual(len(episodes), 4)
        self.assertEqual(by_id["ep_inc-compile-500"]["packet_ids"], ["ipk_w001", "ipk_w004", "ipk_w006", "ipk_w009"])
        self.assertEqual(by_id["ep_inc-compile-500"]["episode_start_ts"], "2026-04-16T11:25:00Z")
        self.assertEqual(by_id["ep_inc-other-service"]["episode_end_ts"], "2026-04-16T12:25:00Z")

        result = run_time_aware_historical_eval(ROOT)
        self.assertEqual(result["episode_count"], 4)
        self.assertEqual(result["packet_count"], 10)
        self.assertEqual(len(result["folds"]), 4)
        self.assertEqual(result["folds"][0]["train_row_count"], 6)
        self.assertEqual(result["folds"][0]["strict_history_incident_count"], 0)
        self.assertEqual(result["folds"][-1]["strict_history_incident_count"], 2)
        self.assertGreater(result["cutoff_leakage_audit"]["folds_with_relaxed_history_gt_strict"], 0)
        self.assertEqual(result["packet_metrics"]["teacher_escalation_rate"], 0.0)
        self.assertEqual(result["episode_metrics"]["episode_count"], 4)


if __name__ == "__main__":
    unittest.main()
