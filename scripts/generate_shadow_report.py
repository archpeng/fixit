#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import json

from fixit_ai.common import read_jsonl, read_yaml, write_json, write_text
from fixit_ai.shadow import build_shadow_report_data, render_shadow_report_markdown


def _retrieval_map(records: list[dict]) -> dict[str, list[dict]]:
    return {item["packet_id"]: item.get("references", []) for item in records}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packets", default=str(REPO_ROOT / "data/samples/incident-packets.jsonl"))
    parser.add_argument("--retrieval", default=str(REPO_ROOT / "data/samples/retrieval-results.jsonl"))
    parser.add_argument("--decisions", default=str(REPO_ROOT / "data/eval/triage-decisions.jsonl"))
    parser.add_argument("--teacher", default=str(REPO_ROOT / "data/eval/teacher-judgements.jsonl"))
    parser.add_argument("--outcomes", default=str(REPO_ROOT / "data/eval/outcomes.jsonl"))
    parser.add_argument("--services", default=str(REPO_ROOT / "configs/services.yaml"))
    parser.add_argument("--thresholds", default=str(REPO_ROOT / "configs/thresholds.yaml"))
    parser.add_argument("--manifest", default=None)
    parser.add_argument("--enrichment-usage", default=None)
    parser.add_argument("--teacher-summary", default=None)
    parser.add_argument("--json-out", default=str(REPO_ROOT / "data/reports/daily-shadow-report.json"))
    parser.add_argument("--md-out", default=str(REPO_ROOT / "data/reports/daily-shadow-report.md"))
    args = parser.parse_args()

    thresholds = read_yaml(args.thresholds)
    replay_manifest = json.loads(Path(args.manifest).read_text()) if args.manifest and Path(args.manifest).exists() else None
    enrichment_usage = json.loads(Path(args.enrichment_usage).read_text()) if args.enrichment_usage and Path(args.enrichment_usage).exists() else None
    teacher_summary = json.loads(Path(args.teacher_summary).read_text()) if args.teacher_summary and Path(args.teacher_summary).exists() else None
    report = build_shadow_report_data(
        read_jsonl(args.packets),
        _retrieval_map(read_jsonl(args.retrieval)),
        read_jsonl(args.decisions),
        read_jsonl(args.teacher),
        read_jsonl(args.outcomes),
        read_yaml(args.services),
        top_k=thresholds["student"]["evaluation"]["top_k"],
        replay_manifest=replay_manifest,
        enrichment_usage_summary=enrichment_usage,
        teacher_queue_summary=teacher_summary,
    )
    write_json(args.json_out, report)
    write_text(args.md_out, render_shadow_report_markdown(report))
    print(f"shadow report -> {args.md_out}")


if __name__ == "__main__":
    main()
