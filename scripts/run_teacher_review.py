#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fixit_ai.common import read_jsonl, read_yaml, write_json, write_jsonl
from fixit_ai.teacher import run_teacher_workflow


def _retrieval_map(records: list[dict]) -> dict[str, list[dict]]:
    return {item["packet_id"]: item.get("references", []) for item in records}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packets", default=str(REPO_ROOT / "data/samples/incident-packets.jsonl"))
    parser.add_argument("--retrieval", default=str(REPO_ROOT / "data/samples/retrieval-results.jsonl"))
    parser.add_argument("--scores", default=str(REPO_ROOT / "data/eval/student-scores.jsonl"))
    parser.add_argument("--budget", default=str(REPO_ROOT / "configs/teacher-budget.yaml"))
    parser.add_argument("--seed-judgements", default=str(REPO_ROOT / "data/eval/manual_teacher_judgements.jsonl"))
    parser.add_argument("--output", default=str(REPO_ROOT / "data/eval/teacher-judgements.jsonl"))
    parser.add_argument("--payloads", default=str(REPO_ROOT / "data/eval/teacher-request-ledger.jsonl"))
    parser.add_argument("--review-ledger", default=str(REPO_ROOT / "data/eval/teacher-review-ledger.jsonl"))
    parser.add_argument("--fallback-ledger", default=str(REPO_ROOT / "data/eval/teacher-fallback-ledger.jsonl"))
    parser.add_argument("--summary", default=str(REPO_ROOT / "data/eval/teacher-queue-summary.json"))
    args = parser.parse_args()

    packets = read_jsonl(args.packets)
    retrieval_records = read_jsonl(args.retrieval)
    scores = read_jsonl(args.scores)
    budget = read_yaml(args.budget)
    workflow = run_teacher_workflow(
        packets,
        _retrieval_map(retrieval_records),
        scores,
        budget,
        read_jsonl(args.seed_judgements),
    )
    write_jsonl(args.output, workflow["judgements"])
    write_jsonl(args.payloads, workflow["requests"])
    write_jsonl(args.review_ledger, workflow["reviews"])
    write_jsonl(args.fallback_ledger, workflow["fallbacks"])
    write_json(args.summary, workflow["summary"])
    print(
        f"teacher reviews selected={workflow['summary']['selected_count']} reviewed={workflow['summary']['reviewed_count']} fallback={workflow['summary']['fallback_count']}"
    )


if __name__ == "__main__":
    main()
