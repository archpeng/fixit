#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fixit_ai.common import read_jsonl, read_yaml, write_json, write_jsonl, write_pickle, write_text
from fixit_ai.student import FEATURE_NAMES, predict_packets, train_student_model


def _retrieval_map(records: list[dict]) -> dict[str, list[dict]]:
    return {item["packet_id"]: item.get("references", []) for item in records}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packets", default=str(REPO_ROOT / "data/samples/incident-packets.jsonl"))
    parser.add_argument("--retrieval", default=str(REPO_ROOT / "data/samples/retrieval-results.jsonl"))
    parser.add_argument("--training", default=str(REPO_ROOT / "data/eval/training_examples.jsonl"))
    parser.add_argument("--thresholds", default=str(REPO_ROOT / "configs/thresholds.yaml"))
    parser.add_argument("--model", default=str(REPO_ROOT / "data/eval/model.pkl"))
    parser.add_argument("--scores", default=str(REPO_ROOT / "data/eval/student-scores.jsonl"))
    parser.add_argument("--feature-manifest", default=str(REPO_ROOT / "data/eval/feature-manifest.json"))
    parser.add_argument("--label-sources", default=str(REPO_ROOT / "data/eval/label-sources.json"))
    parser.add_argument("--feature-importance", default=str(REPO_ROOT / "data/eval/feature-importance.md"))
    parser.add_argument("--threshold-proposal", default=str(REPO_ROOT / "data/eval/student-threshold-proposal.json"))
    args = parser.parse_args()

    packets = read_jsonl(args.packets)
    retrieval_records = read_jsonl(args.retrieval)
    retrieval_map = _retrieval_map(retrieval_records)
    training_rows = read_jsonl(args.training)
    thresholds = read_yaml(args.thresholds)

    model, manifest = train_student_model(training_rows, thresholds)
    scores = predict_packets(model, packets, retrieval_map)
    write_pickle(args.model, model)
    write_jsonl(args.scores, scores)
    write_json(args.feature_manifest, manifest)
    write_json(
        args.label_sources,
        {
            "weights": manifest["label_source_weights"],
            "training_examples": len(training_rows),
            "feature_names": FEATURE_NAMES,
        },
    )
    ranked = sorted(model.weights.items(), key=lambda item: abs(item[1]), reverse=True)
    lines = ["# Feature Importance", ""]
    for name, weight in ranked:
        lines.append(f"- `{name}`: `{weight:.4f}`")
    write_text(args.feature_importance, "\n".join(lines) + "\n")
    write_json(
        args.threshold_proposal,
        {
            "recommended_thresholds": thresholds["student"]["score_thresholds"],
            "observed_score_band": {
                "max": max((item["student_score"] for item in scores), default=0.0),
                "min": min((item["student_score"] for item in scores), default=0.0),
            },
            "note": "Keep initial thresholds aligned with MVP docs until larger replay data justifies recalibration.",
        },
    )
    print(f"trained student model -> {args.model}; scored {len(scores)} packets")


if __name__ == "__main__":
    main()
