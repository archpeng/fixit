#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fixit_ai.common import read_jsonl, read_yaml, write_json, write_jsonl
from fixit_ai.eval import compute_eval_metrics
from fixit_ai.schema_tools import SchemaBundle
from fixit_ai.shadow import build_triage_decisions


def _retrieval_map(records: list[dict]) -> dict[str, list[dict]]:
    return {item["packet_id"]: item.get("references", []) for item in records}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packets", default=str(REPO_ROOT / "data/samples/incident-packets.jsonl"))
    parser.add_argument("--retrieval", default=str(REPO_ROOT / "data/samples/retrieval-results.jsonl"))
    parser.add_argument("--scores", default=str(REPO_ROOT / "data/eval/student-scores.jsonl"))
    parser.add_argument("--teacher", default=str(REPO_ROOT / "data/eval/teacher-judgements.jsonl"))
    parser.add_argument("--outcomes", default=str(REPO_ROOT / "data/eval/outcomes.jsonl"))
    parser.add_argument("--thresholds", default=str(REPO_ROOT / "configs/thresholds.yaml"))
    parser.add_argument("--schemas", default=str(REPO_ROOT / "schemas"))
    parser.add_argument("--decisions", default=str(REPO_ROOT / "data/eval/triage-decisions.jsonl"))
    parser.add_argument("--metrics", default=str(REPO_ROOT / "data/eval/metrics-summary.json"))
    args = parser.parse_args()

    packets = read_jsonl(args.packets)
    retrieval_records = read_jsonl(args.retrieval)
    scores = read_jsonl(args.scores)
    teacher_reviews = read_jsonl(args.teacher)
    outcomes = read_jsonl(args.outcomes)
    thresholds = read_yaml(args.thresholds)
    schemas = SchemaBundle(args.schemas)

    decisions = build_triage_decisions(
        packets,
        _retrieval_map(retrieval_records),
        scores,
        teacher_reviews,
        thresholds,
        schemas,
    )
    metrics = compute_eval_metrics(
        decisions,
        outcomes,
        top_k=thresholds["student"]["evaluation"]["top_k"],
    )
    write_jsonl(args.decisions, decisions)
    write_json(args.metrics, metrics)
    print(f"evaluated {len(decisions)} triage decisions -> {args.metrics}")


if __name__ == "__main__":
    main()
