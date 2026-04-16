import json
import unittest
from pathlib import Path

import yaml

from fixit_ai.calibration import build_calibration_report
from fixit_ai.candidate_generation import generate_candidate_windows
from fixit_ai.enrichment import apply_live_first_enrichment, summarize_enrichment_usage
from fixit_ai.labeling import build_label_ledger
from fixit_ai.packet_builder import build_packets
from fixit_ai.replay_pack import refresh_replay_pack
from fixit_ai.retrieval_index import build_retrieval_index, search_retrieval_index
from fixit_ai.schema_tools import SchemaBundle
from fixit_ai.shadow import build_shadow_report_data, build_triage_decisions, render_shadow_report_markdown
from fixit_ai.student import predict_packets, train_student_model
from fixit_ai.teacher import run_teacher_workflow

ROOT = Path(__file__).resolve().parents[1]


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


class HardeningPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schemas = SchemaBundle(ROOT / "schemas")
        cls.thresholds = yaml.safe_load((ROOT / "configs/thresholds.yaml").read_text())
        cls.teacher_budget = yaml.safe_load((ROOT / "configs/teacher-budget.yaml").read_text())
        cls.services = yaml.safe_load((ROOT / "configs/services.yaml").read_text())
        cls.replay_cfg = yaml.safe_load((ROOT / "configs/replay-pack.yaml").read_text())

    def test_replay_manifest_refresh_is_deterministic_and_classifies_sources(self):
        manifest = refresh_replay_pack(self.replay_cfg, ROOT, generated_at="2026-04-16T12:00:00Z")
        manifest_again = refresh_replay_pack(self.replay_cfg, ROOT, generated_at="2026-04-16T12:00:00Z")
        self.assertEqual(manifest, manifest_again)

        classes = {source["class"] for dataset in manifest["datasets"] for source in dataset["sources"]}
        self.assertIn("live_bounded_export", classes)
        self.assertIn("retained_fixture", classes)
        self.assertTrue(any(item["class"] == "derived_artifact" for item in manifest["derived_artifacts"]))
        self.assertTrue((ROOT / "data/samples/replay/metrics_windows.jsonl").exists())
        self.assertTrue((ROOT / "data/eval/replay/training_examples.jsonl").exists())

    def test_retrieval_index_preserves_explainable_top_hit_on_replay_pack(self):
        refresh_replay_pack(self.replay_cfg, ROOT, generated_at="2026-04-16T12:05:00Z")
        incidents = read_jsonl(ROOT / "data/eval/replay/historical_incidents.jsonl")
        index = build_retrieval_index(incidents)

        metrics = read_jsonl(ROOT / "data/samples/replay/metrics_windows.jsonl")
        logs = read_jsonl(ROOT / "data/samples/replay/log_evidence.jsonl")
        traces = read_jsonl(ROOT / "data/samples/replay/trace_evidence.jsonl")
        topology = read_jsonl(ROOT / "data/samples/replay/topology.jsonl")
        memory = read_jsonl(ROOT / "data/samples/replay/memory_summaries.jsonl")
        candidates = generate_candidate_windows(metrics, self.thresholds)
        packets = build_packets(candidates, logs, traces, topology, memory, self.schemas)
        packet = next(item for item in packets if item["packet_id"] == "ipk_w001")

        refs = search_retrieval_index(packet, index, top_k=3)
        self.assertEqual(refs[0]["incident_id"], "inc-compile-500")
        self.assertIn("matched_terms", refs[0])
        self.assertTrue(refs[0]["matched_terms"])

    def test_label_ledger_and_calibration_report_harden_replay_evidence(self):
        refresh_replay_pack(self.replay_cfg, ROOT, generated_at="2026-04-16T12:10:00Z")
        training = read_jsonl(ROOT / "data/eval/replay/training_examples.jsonl")
        outcomes = read_jsonl(ROOT / "data/eval/replay/outcomes.jsonl")
        ledger = build_label_ledger(training, outcomes)

        self.assertGreaterEqual(ledger["counts_by_source"]["human_outcome"], 2)
        self.assertIn("effective_weights", ledger)

        model, _ = train_student_model(training, self.thresholds)
        metrics = read_jsonl(ROOT / "data/samples/replay/metrics_windows.jsonl")
        logs = read_jsonl(ROOT / "data/samples/replay/log_evidence.jsonl")
        traces = read_jsonl(ROOT / "data/samples/replay/trace_evidence.jsonl")
        topology = read_jsonl(ROOT / "data/samples/replay/topology.jsonl")
        memory = read_jsonl(ROOT / "data/samples/replay/memory_summaries.jsonl")
        candidates = generate_candidate_windows(metrics, self.thresholds)
        packets = build_packets(candidates, logs, traces, topology, memory, self.schemas)
        index = build_retrieval_index(read_jsonl(ROOT / "data/eval/replay/historical_incidents.jsonl"))
        retrieval = {packet["packet_id"]: search_retrieval_index(packet, index, top_k=3) for packet in packets}
        scores = predict_packets(model, packets, retrieval)
        report = build_calibration_report(scores, outcomes, self.thresholds)

        self.assertIn("bucket_summary", report)
        self.assertIn("threshold_review", report)
        self.assertTrue(report["threshold_review"]["recommended_action"] in {"keep", "adjust"})

    def test_teacher_workflow_records_review_and_fallback_ledgers(self):
        refresh_replay_pack(self.replay_cfg, ROOT, generated_at="2026-04-16T12:15:00Z")
        training = read_jsonl(ROOT / "data/eval/replay/training_examples.jsonl")
        model, _ = train_student_model(training, self.thresholds)
        metrics = read_jsonl(ROOT / "data/samples/replay/metrics_windows.jsonl")
        logs = read_jsonl(ROOT / "data/samples/replay/log_evidence.jsonl")
        traces = read_jsonl(ROOT / "data/samples/replay/trace_evidence.jsonl")
        topology = read_jsonl(ROOT / "data/samples/replay/topology.jsonl")
        memory = read_jsonl(ROOT / "data/samples/replay/memory_summaries.jsonl")
        candidates = generate_candidate_windows(metrics, self.thresholds)
        packets = build_packets(candidates, logs, traces, topology, memory, self.schemas)
        index = build_retrieval_index(read_jsonl(ROOT / "data/eval/replay/historical_incidents.jsonl"))
        retrieval = {packet["packet_id"]: search_retrieval_index(packet, index, top_k=3) for packet in packets}
        scores = predict_packets(model, packets, retrieval)

        workflow = run_teacher_workflow(
            packets,
            retrieval,
            scores,
            self.teacher_budget,
            seed_judgements=read_jsonl(ROOT / "data/eval/replay/manual_teacher_judgements.jsonl"),
        )
        self.assertGreaterEqual(workflow["summary"]["selected_count"], 2)
        self.assertGreaterEqual(workflow["summary"]["reviewed_count"], 1)
        self.assertGreaterEqual(workflow["summary"]["fallback_count"], 1)
        self.assertTrue(any(item["packet_id"] == "ipk_w006" for item in workflow["fallbacks"]))

    def test_live_first_enrichment_prefers_live_then_fallback(self):
        config_rows = read_jsonl(ROOT / "data/samples/replay/topology.jsonl")
        config_map = {row["service"]: row for row in config_rows}
        live_records = [{"service": "g-crm-campaign", "tier": "tier1-live", "owner": "cp-owner", "repos": ["cp-repo"], "blast_radius_score": 0.91, "upstream_count": 5, "downstream_count": 6}]
        enriched_live, usage_live = apply_live_first_enrichment(config_rows, config_map, live_records)
        row = next(item for item in enriched_live if item["service"] == "g-crm-campaign")
        self.assertEqual(row["owner"], "cp-owner")
        self.assertEqual(usage_live[0]["source"], "live")

        enriched_fallback, usage_fallback = apply_live_first_enrichment(config_rows, config_map, [])
        row = next(item for item in enriched_fallback if item["service"] == "g-crm-campaign")
        self.assertEqual(row["owner"], "growth-campaign-oncall")
        self.assertEqual(usage_fallback[0]["source"], "config_fallback")
        summary = summarize_enrichment_usage(usage_fallback)
        self.assertEqual(summary["fallback_count"], 1)

    def test_hardened_shadow_report_includes_freshness_fallback_and_queue_visibility(self):
        manifest = refresh_replay_pack(self.replay_cfg, ROOT, generated_at="2026-04-16T12:20:00Z")
        training = read_jsonl(ROOT / "data/eval/replay/training_examples.jsonl")
        outcomes = read_jsonl(ROOT / "data/eval/replay/outcomes.jsonl")
        model, _ = train_student_model(training, self.thresholds)

        metrics = read_jsonl(ROOT / "data/samples/replay/metrics_windows.jsonl")
        logs = read_jsonl(ROOT / "data/samples/replay/log_evidence.jsonl")
        traces = read_jsonl(ROOT / "data/samples/replay/trace_evidence.jsonl")
        topology = read_jsonl(ROOT / "data/samples/replay/topology.jsonl")
        memory = read_jsonl(ROOT / "data/samples/replay/memory_summaries.jsonl")
        config_map = {row["service"]: row for row in topology}
        topology_rows, enrichment_usage = apply_live_first_enrichment(topology, config_map, [])
        candidates = generate_candidate_windows(metrics, self.thresholds)
        packets = build_packets(candidates, logs, traces, topology_rows, memory, self.schemas)
        index = build_retrieval_index(read_jsonl(ROOT / "data/eval/replay/historical_incidents.jsonl"))
        retrieval = {packet["packet_id"]: search_retrieval_index(packet, index, top_k=3) for packet in packets}
        scores = predict_packets(model, packets, retrieval)
        workflow = run_teacher_workflow(
            packets,
            retrieval,
            scores,
            self.teacher_budget,
            seed_judgements=read_jsonl(ROOT / "data/eval/replay/manual_teacher_judgements.jsonl"),
        )

        decisions = build_triage_decisions(
            packets,
            retrieval,
            scores,
            workflow["judgements"],
            self.thresholds,
            self.schemas,
            teacher_fallbacks=workflow["fallbacks"],
        )
        report = build_shadow_report_data(
            packets,
            retrieval,
            decisions,
            workflow["judgements"],
            outcomes,
            self.services,
            top_k=self.thresholds["student"]["evaluation"]["top_k"],
            replay_manifest=manifest,
            enrichment_usage_summary=summarize_enrichment_usage(enrichment_usage),
            teacher_queue_summary=workflow["summary"],
        )
        self.assertIn("data_freshness", report)
        self.assertIn("enrichment_usage", report)
        self.assertIn("teacher_queue", report)
        self.assertGreaterEqual(report["teacher_queue"]["fallback_count"], 1)
        markdown = render_shadow_report_markdown(report)
        self.assertIn("Data Freshness", markdown)
        self.assertIn("Fallback Usage", markdown)
        self.assertIn("Teacher Queue", markdown)


if __name__ == "__main__":
    unittest.main()
