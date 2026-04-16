import json
import unittest
from pathlib import Path

import yaml

from fixit_ai.candidate_generation import generate_candidate_windows
from fixit_ai.packet_builder import build_packets
from fixit_ai.retrieval import retrieve_similar_incidents
from fixit_ai.schema_tools import SchemaBundle
from fixit_ai.shadow import build_shadow_report_data, build_triage_decisions
from fixit_ai.student import (
    extract_packet_features,
    predict_packets,
    train_student_model,
)
from fixit_ai.teacher import select_teacher_reviews

ROOT = Path(__file__).resolve().parents[1]


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


class AlertIntelligencePipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.thresholds = yaml.safe_load((ROOT / "configs/thresholds.yaml").read_text())
        cls.teacher_budget = yaml.safe_load((ROOT / "configs/teacher-budget.yaml").read_text())
        cls.services = yaml.safe_load((ROOT / "configs/services.yaml").read_text())
        cls.metrics = read_jsonl(ROOT / "data/samples/raw/metrics_windows.jsonl")
        cls.logs = read_jsonl(ROOT / "data/samples/raw/log_evidence.jsonl")
        cls.traces = read_jsonl(ROOT / "data/samples/raw/trace_evidence.jsonl")
        cls.topology = read_jsonl(ROOT / "data/samples/raw/topology.jsonl")
        cls.memory = read_jsonl(ROOT / "data/samples/raw/memory_summaries.jsonl")
        cls.incidents = read_jsonl(ROOT / "data/eval/historical_incidents.jsonl")
        cls.training = read_jsonl(ROOT / "data/eval/training_examples.jsonl")
        cls.outcomes = read_jsonl(ROOT / "data/eval/outcomes.jsonl")
        cls.manual_teacher = read_jsonl(ROOT / "data/eval/manual_teacher_judgements.jsonl")
        cls.schemas = SchemaBundle(ROOT / "schemas")

    def test_candidate_generation_flags_rule_hits_and_multi_signal_windows(self):
        candidates = generate_candidate_windows(
            self.metrics,
            self.thresholds,
            allowed_services={self.services["pilot_family"]["service"]},
        )
        candidate_ids = {item["window_id"] for item in candidates}
        self.assertEqual(candidate_ids, {"w001", "w002", "w004", "w005"})

        hard_case = next(item for item in candidates if item["window_id"] == "w004")
        self.assertIn("multi_signal_shift", hard_case["anomaly_signals"])
        self.assertEqual(hard_case["rules"]["fired"], [])

    def test_packet_builder_merges_sources_and_validates_against_schema(self):
        candidates = generate_candidate_windows(self.metrics, self.thresholds)
        packets = build_packets(candidates, self.logs, self.traces, self.topology, self.memory, self.schemas)
        self.assertEqual(len(packets), 4)
        packet = next(item for item in packets if item["packet_id"] == "ipk_w001")
        self.schemas.validate("incident-packet.v1.json", packet)
        self.assertEqual(packet["topology"]["owner"], "growth-campaign-oncall")
        self.assertEqual(packet["traces"]["top_error_operation"], "ADCService/Compile")

    def test_retrieval_prefers_matching_compile_error_incident(self):
        candidates = generate_candidate_windows(self.metrics, self.thresholds)
        packets = build_packets(candidates, self.logs, self.traces, self.topology, self.memory, self.schemas)
        packet = next(item for item in packets if item["packet_id"] == "ipk_w001")
        refs = retrieve_similar_incidents(packet, self.incidents, top_k=2)
        self.assertEqual(refs[0]["incident_id"], "inc-compile-500")
        self.assertGreater(refs[0]["similarity_score"], refs[1]["similarity_score"])

    def test_student_model_scores_severe_packets_above_non_severe(self):
        model, manifest = train_student_model(self.training, self.thresholds)
        self.assertIn("error_rate_delta", manifest["feature_names"])

        candidates = generate_candidate_windows(self.metrics, self.thresholds)
        packets = build_packets(candidates, self.logs, self.traces, self.topology, self.memory, self.schemas)
        retrieval = {
            packet["packet_id"]: retrieve_similar_incidents(packet, self.incidents, top_k=3)
            for packet in packets
        }
        scores = predict_packets(model, packets, retrieval)

        severe = next(item for item in scores if item["packet_id"] == "ipk_w001")
        rule_missed_severe = next(item for item in scores if item["packet_id"] == "ipk_w004")
        low = next(item for item in scores if item["packet_id"] == "ipk_w005")

        self.assertGreater(severe["student_score"], 0.75)
        self.assertGreater(rule_missed_severe["student_score"], low["student_score"])
        self.assertGreater(rule_missed_severe["novelty_score"], 0.85)

    def test_teacher_gate_and_shadow_report_capture_rule_missed_high_rank_case(self):
        model, _ = train_student_model(self.training, self.thresholds)
        candidates = generate_candidate_windows(self.metrics, self.thresholds)
        packets = build_packets(candidates, self.logs, self.traces, self.topology, self.memory, self.schemas)
        retrieval = {
            packet["packet_id"]: retrieve_similar_incidents(packet, self.incidents, top_k=3)
            for packet in packets
        }
        scores = predict_packets(model, packets, retrieval)
        teacher_reviews, payloads = select_teacher_reviews(
            packets,
            retrieval,
            scores,
            self.teacher_budget,
            self.manual_teacher,
        )
        self.assertLessEqual(len(payloads), self.teacher_budget["max_reviews_per_run"])
        self.assertIn("ipk_w004", {item["packet_id"] for item in teacher_reviews})
        self.schemas.validate("teacher-judgement.v1.json", teacher_reviews[0])

        decisions = build_triage_decisions(
            packets,
            retrieval,
            scores,
            teacher_reviews,
            self.thresholds,
            self.schemas,
        )
        report = build_shadow_report_data(
            packets,
            retrieval,
            decisions,
            teacher_reviews,
            self.outcomes,
            self.services,
            top_k=self.thresholds["student"]["evaluation"]["top_k"],
        )
        top_rule_missed_ids = {item["packet_id"] for item in report["rule_missed_high_ranked"]}
        self.assertIn("ipk_w004", top_rule_missed_ids)
        self.assertGreaterEqual(report["metrics"]["severe_recall"], 1.0)

        for decision in decisions:
            self.schemas.validate("triage-decision.v1.json", decision)

    def test_feature_extractor_emits_expected_keys(self):
        candidates = generate_candidate_windows(self.metrics, self.thresholds)
        packets = build_packets(candidates, self.logs, self.traces, self.topology, self.memory, self.schemas)
        packet = next(item for item in packets if item["packet_id"] == "ipk_w004")
        refs = retrieve_similar_incidents(packet, self.incidents, top_k=3)
        features = extract_packet_features(packet, refs)
        self.assertEqual(set(features.keys()), {
            "error_rate_delta",
            "p95_delta",
            "qps_delta",
            "alert_count",
            "rule_score_max",
            "template_novelty_max",
            "log_error_density",
            "trace_error_ratio",
            "blast_radius_score",
            "similar_severe_score",
            "recent_deploy",
        })


if __name__ == "__main__":
    unittest.main()
