from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable

FEATURE_NAMES = [
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
]

LABEL_SOURCE_WEIGHTS = {
    "human_outcome": 1.0,
    "production_outcome": 0.9,
    "teacher_rubric": 0.75,
    "rule": 0.6,
}


@dataclass
class StudentModel:
    feature_names: list[str]
    weights: dict[str, float]
    bias: float

    def predict_proba(self, features: dict[str, float]) -> float:
        z = self.bias + sum(self.weights[name] * features.get(name, 0.0) for name in self.feature_names)
        return 1.0 / (1.0 + math.exp(-max(min(z, 60), -60)))


def _sample_weight(row: dict) -> float:
    return row.get("sample_weight", LABEL_SOURCE_WEIGHTS.get(row.get("label_source"), 0.5))


def extract_packet_features(packet: dict, retrieval_refs: Iterable[dict]) -> dict[str, float]:
    metrics = packet.get("metrics", {})
    templates = packet.get("logs", {}).get("top_templates", [])
    top_novelty = max((item.get("novelty", 0.0) for item in templates), default=0.0)
    total_template_count = sum(item.get("count", 0.0) for item in templates)
    severe_similarity = max(
        (ref.get("similarity_score", 0.0) for ref in retrieval_refs if ref.get("severity") == "severe"),
        default=0.0,
    )
    score_max = max(packet.get("rules", {}).get("scores", {}).values(), default=0.0)

    return {
        "error_rate_delta": min(metrics.get("error_rate_delta", 0.0) / 0.20, 1.0),
        "p95_delta": min(metrics.get("p95_delta", 0.0), 1.0),
        "qps_delta": min(metrics.get("qps_delta", 0.0) / 0.30, 1.0),
        "alert_count": min(float(len(packet.get("rules", {}).get("fired", []))), 1.0),
        "rule_score_max": min(score_max, 1.0),
        "template_novelty_max": min(top_novelty, 1.0),
        "log_error_density": min(math.log1p(total_template_count) / 2.5, 1.0),
        "trace_error_ratio": min(packet.get("traces", {}).get("error_span_ratio", 0.0), 1.0),
        "blast_radius_score": min(packet.get("topology", {}).get("blast_radius_score", 0.0), 1.0),
        "similar_severe_score": min(severe_similarity, 1.0),
        "recent_deploy": 1.0 if packet.get("history", {}).get("recent_deploy") else 0.0,
    }


def train_student_model(training_rows: list[dict], thresholds: dict) -> tuple[StudentModel, dict]:
    cfg = thresholds["student"]["training"]
    weights = {name: 0.0 for name in FEATURE_NAMES}
    bias = 0.0
    learning_rate = cfg["learning_rate"]
    l2 = cfg["l2"]

    for _ in range(cfg["epochs"]):
        for row in training_rows:
            features = row["features"]
            z = bias + sum(weights[name] * features.get(name, 0.0) for name in FEATURE_NAMES)
            prob = 1.0 / (1.0 + math.exp(-max(min(z, 60), -60)))
            target = row["label"]
            error = (prob - target) * _sample_weight(row)
            for name in FEATURE_NAMES:
                gradient = error * features.get(name, 0.0) + l2 * weights[name]
                weights[name] -= learning_rate * gradient
            bias -= learning_rate * error

    model = StudentModel(feature_names=FEATURE_NAMES, weights=weights, bias=bias)
    manifest = {
        "feature_names": FEATURE_NAMES,
        "label_source_weights": LABEL_SOURCE_WEIGHTS,
    }
    return model, manifest


def _top_feature_contributions(model: StudentModel, features: dict[str, float], limit: int = 3) -> list[str]:
    contributions = [
        (name, model.weights[name] * features.get(name, 0.0)) for name in model.feature_names if features.get(name, 0.0)
    ]
    top = sorted(contributions, key=lambda item: abs(item[1]), reverse=True)[:limit]
    return [f"{name}={features[name]:.2f}" for name, _ in top]


def predict_packets(model: StudentModel, packets: list[dict], retrieval_by_packet: dict[str, list[dict]]) -> list[dict]:
    scored: list[dict] = []
    for packet in packets:
        refs = retrieval_by_packet.get(packet["packet_id"], [])
        features = extract_packet_features(packet, refs)
        score = model.predict_proba(features)
        novelty_score = max(features["template_novelty_max"], 1.0 - features["similar_severe_score"])
        confidence = abs(score - 0.5) * 2.0
        scored.append(
            {
                "packet_id": packet["packet_id"],
                "student_score": round(score, 4),
                "student_confidence": round(confidence, 4),
                "novelty_score": round(min(max(novelty_score, 0.0), 1.0), 4),
                "features": features,
                "explanations": _top_feature_contributions(model, features),
            }
        )
    return scored
