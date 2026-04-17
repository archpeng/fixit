import json
import unittest
from pathlib import Path

from fixit_ai.retrieval_index import build_retrieval_index, search_retrieval_index
from fixit_ai.temporal_alignment import (
    build_episode_context_priors,
    build_episode_index,
    build_episode_index_from_records,
    build_temporal_alignment_summary,
    build_temporal_boundary_safe_probe,
    build_temporal_episode_context_probe,
    build_temporal_feature_experiment,
    build_temporal_hybrid_context_probe,
    build_temporal_lineage,
    build_temporal_selective_hybrid_probe,
    build_temporal_overlay_summary,
    build_temporal_overlays,
    build_temporal_prior_catalog,
    build_temporal_prior_probe,
    build_temporal_prior_summary,
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

    def test_recency_aware_retrieval_prefers_newer_strict_history_when_semantics_tie(self):
        incidents = [
            {
                "incident_id": "inc_old",
                "service": "svc-a",
                "operation": "POST /checkout",
                "summary": "db timeout on order lookup",
                "severity": "severe",
                "recommended_action": "page_owner",
                "tags": ["db", "timeout"],
                "derived_ts_end": "2026-04-16T10:00:00Z",
            },
            {
                "incident_id": "inc_new",
                "service": "svc-a",
                "operation": "POST /checkout",
                "summary": "db timeout on order lookup",
                "severity": "severe",
                "recommended_action": "page_owner",
                "tags": ["db", "timeout"],
                "derived_ts_end": "2026-04-16T11:50:00Z",
            },
        ]
        packet = {
            "packet_id": "ipk_test",
            "service": "svc-a",
            "operation": "POST /checkout",
            "ts_start": "2026-04-16T12:00:00Z",
            "logs": {"top_templates": [{"template": "db timeout on order lookup"}]},
            "traces": {"status_message": "db timeout on order lookup"},
        }
        index = build_retrieval_index(incidents)
        ranked = search_retrieval_index(packet, index, top_k=2, reference_ts=packet["ts_start"], recency_half_life_minutes=60)
        self.assertEqual(ranked[0]["incident_id"], "inc_new")
        self.assertGreater(ranked[0]["similarity_score"], ranked[1]["similarity_score"])

    def test_time_aware_eval_reports_recency_compare(self):
        result = run_time_aware_historical_eval(ROOT)
        self.assertIn("recency_compare", result)
        self.assertEqual(result["recency_compare"]["fold_count"], 4)
        self.assertGreater(result["recency_compare"]["folds_with_recency_delta"], 0)
        self.assertEqual(result["recency_compare"]["strict_cutoff_fold_count"], 4)

    def test_temporal_feature_experiment_reports_coverage_and_compare(self):
        result = build_temporal_feature_experiment(ROOT)
        self.assertEqual(result["temporal_feature_coverage"]["packet_linked_training_count"], 10)
        self.assertEqual(result["temporal_feature_coverage"]["legacy_zero_filled_count"], 6)
        self.assertIn("same_service_recent_packet_count", result["temporal_feature_names"])
        self.assertIn("baseline_packet_metrics", result)
        self.assertIn("temporal_packet_metrics", result)
        self.assertEqual(result["baseline_packet_metrics"]["severe_recall"], 1.0)
        self.assertEqual(result["temporal_packet_metrics"]["severe_recall"], 1.0)
        self.assertEqual(result["fold_count"], 4)

    def test_temporal_prior_catalog_expands_packet_linked_exact_time_history(self):
        priors = build_temporal_prior_catalog(ROOT)
        summary = build_temporal_prior_summary(priors)
        prior_by_id = {item["prior_id"]: item for item in priors}

        self.assertEqual(len(priors), 10)
        self.assertTrue(all(item["timestamp_quality"] == "exact_time_inherited" for item in priors))
        self.assertTrue(all(item["cutoff_safe"] for item in priors))
        self.assertEqual(prior_by_id["tprior_ipk_w001"]["severity"], "severe")
        self.assertEqual(prior_by_id["tprior_ipk_w001"]["recommended_action"], "page_owner")
        self.assertEqual(prior_by_id["tprior_ipk_w001"]["derived_ts_end"], "2026-04-16T11:30:00Z")
        self.assertEqual(summary["service_counts"]["g-crm-campaign"], 7)
        self.assertEqual(summary["severity_counts"]["severe"], 4)
        self.assertEqual(summary["packet_linked_prior_count"], 10)

    def test_temporal_prior_probe_reports_strict_history_expansion(self):
        result = build_temporal_prior_probe(ROOT)
        self.assertEqual(result["baseline_history_doc_count"], 4)
        self.assertEqual(result["expanded_packet_prior_count"], 10)
        self.assertEqual(result["fold_count"], 4)
        self.assertGreater(result["compare"]["folds_with_expanded_history_gt_baseline"], 0)
        self.assertGreater(result["compare"]["folds_with_expanded_refs_gt_baseline"], 0)
        self.assertIn("baseline_packet_metrics", result)
        self.assertIn("expanded_packet_metrics", result)

    def test_boundary_safe_cutoff_probe_reports_equality_gains_without_leakage(self):
        result = build_temporal_boundary_safe_probe(ROOT)
        self.assertEqual(result["strict_compare"]["fold_count"], 4)
        self.assertGreater(result["strict_compare"]["folds_with_boundary_safe_history_gt_strict"], 0)
        self.assertGreater(result["strict_compare"]["equality_admitted_doc_count"], 0)
        self.assertEqual(result["strict_compare"]["anti_leakage_violation_count"], 0)
        by_id = {item["episode_id"]: item for item in result["folds"]}
        self.assertGreater(
            by_id["ep_inc-compile-warmup"]["boundary_safe_history_doc_count"],
            by_id["ep_inc-compile-warmup"]["strict_history_doc_count"],
        )

    def test_compacted_prior_ablation_reduces_docs_under_boundary_safe_cutoff(self):
        result = build_temporal_boundary_safe_probe(ROOT)
        self.assertGreater(result["prototype_compare"]["folds_with_compacted_doc_count_lt_boundary_safe"], 0)
        self.assertGreater(result["prototype_compare"]["folds_with_top_hit_overlap"], 0)
        self.assertIn("boundary_safe_packet_metrics", result)
        self.assertIn("prototype_packet_metrics", result)

    def test_episode_context_prior_synthesis_compacts_packet_priors_by_episode(self):
        priors = build_temporal_prior_catalog(ROOT)
        context_priors = build_episode_context_priors(priors)
        by_id = {item["source_episode_id"]: item for item in context_priors}

        self.assertEqual(len(context_priors), 4)
        self.assertEqual(by_id["ep_inc-compile-500"]["packet_count"], 4)
        self.assertEqual(by_id["ep_inc-compile-500"]["severity"], "severe")
        self.assertEqual(by_id["ep_inc-compile-500"]["recommended_action"], "page_owner")
        self.assertEqual(by_id["ep_inc-compile-500"]["derived_ts_end"], "2026-04-16T12:10:00Z")
        self.assertIn("episode_context_synthesized", by_id["ep_inc-compile-500"]["tags"])

    def test_episode_context_probe_reports_doc_reduction_and_overlap(self):
        result = build_temporal_episode_context_probe(ROOT)
        self.assertEqual(result["episode_context_prior_count"], 4)
        self.assertEqual(result["fold_count"], 4)
        self.assertGreater(result["compare"]["folds_with_episode_context_doc_count_lt_boundary_safe"], 0)
        self.assertGreater(result["compare"]["folds_with_top_hit_overlap"], 0)
        by_id = {item["episode_id"]: item for item in result["folds"]}
        self.assertLess(
            by_id["ep_inc-other-service"]["episode_context_prior_doc_count"],
            by_id["ep_inc-other-service"]["boundary_safe_packet_prior_doc_count"],
        )
        self.assertIn("boundary_safe_packet_metrics", result)
        self.assertIn("episode_context_packet_metrics", result)

    def test_hybrid_context_probe_reports_score_delta_and_overlap(self):
        result = build_temporal_hybrid_context_probe(ROOT)
        self.assertEqual(result["hybrid_context_prior_count"], 4)
        self.assertEqual(result["fold_count"], 4)
        self.assertGreater(result["compare"]["packets_with_hybrid_score_delta_gt_raw"], 0)
        self.assertGreater(result["compare"]["folds_with_top_hit_overlap"], 0)
        self.assertEqual(result["compare"]["anti_leakage_violation_count"], 0)
        by_id = {item["episode_id"]: item for item in result["folds"]}
        self.assertGreater(by_id["ep_inc-other-service"]["hybrid_score_delta_packet_count"], 0)
        self.assertIn("raw_packet_metrics", result)
        self.assertIn("hybrid_packet_metrics", result)

    def test_selective_hybrid_probe_reports_selected_packets_and_calibration_audit(self):
        result = build_temporal_selective_hybrid_probe(ROOT)
        self.assertEqual(result["fold_count"], 4)
        self.assertGreater(result["compare"]["packets_selected_for_hybrid"], 0)
        self.assertGreater(result["compare"]["packets_with_selected_score_delta_gt_raw"], 0)
        self.assertGreater(result["compare"]["folds_with_selective_routing"], 0)
        self.assertEqual(result["compare"]["anti_leakage_violation_count"], 0)
        by_id = {item["episode_id"]: item for item in result["folds"]}
        self.assertGreater(by_id["ep_inc-other-service"]["selected_hybrid_packet_count"], 0)
        self.assertIn("raw_packet_metrics", result)
        self.assertIn("selective_packet_metrics", result)

    def test_heuristic_episode_grouping_clusters_unbacked_related_packets_but_keeps_bounds(self):
        packets = [
            {
                "packet_id": "ipk_h001",
                "service": "svc-a",
                "operation": "POST /checkout",
                "ts_start": "2026-04-16T12:00:00Z",
                "ts_end": "2026-04-16T12:05:00Z",
                "logs": {"top_templates": [{"template": "db timeout on order lookup"}]},
                "traces": {"status_message": "db timeout on order lookup"},
            },
            {
                "packet_id": "ipk_h002",
                "service": "svc-a",
                "operation": "POST /checkout",
                "ts_start": "2026-04-16T12:10:00Z",
                "ts_end": "2026-04-16T12:15:00Z",
                "logs": {"top_templates": [{"template": "db timeout on order write"}]},
                "traces": {"status_message": "db timeout on order write"},
            },
            {
                "packet_id": "ipk_h003",
                "service": "svc-a",
                "operation": "POST /checkout",
                "ts_start": "2026-04-16T14:30:00Z",
                "ts_end": "2026-04-16T14:35:00Z",
                "logs": {"top_templates": [{"template": "db timeout on order lookup"}]},
                "traces": {"status_message": "db timeout on order lookup"},
            },
            {
                "packet_id": "ipk_h004",
                "service": "svc-b",
                "operation": "POST /checkout",
                "ts_start": "2026-04-16T12:12:00Z",
                "ts_end": "2026-04-16T12:17:00Z",
                "logs": {"top_templates": [{"template": "db timeout on order lookup"}]},
                "traces": {"status_message": "db timeout on order lookup"},
            },
        ]
        episodes = build_episode_index_from_records(packets, incident_overlays=[])
        by_id = {item["episode_id"]: item for item in episodes}

        self.assertEqual(len(episodes), 3)
        heuristic = by_id["ep_heuristic_svc_a_post_checkout_001"]
        self.assertEqual(heuristic["packet_ids"], ["ipk_h001", "ipk_h002"])
        self.assertEqual(heuristic["episode_source"], "heuristic_packet_cluster")
        self.assertEqual(heuristic["episode_start_ts"], "2026-04-16T12:00:00Z")
        self.assertEqual(heuristic["episode_end_ts"], "2026-04-16T12:15:00Z")
        self.assertEqual(by_id["ep_heuristic_svc_a_post_checkout_002"]["packet_ids"], ["ipk_h003"])
        self.assertEqual(by_id["ep_heuristic_svc_b_post_checkout_001"]["packet_ids"], ["ipk_h004"])


if __name__ == "__main__":
    unittest.main()
