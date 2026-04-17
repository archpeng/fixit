#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fixit_ai.common import write_json, write_jsonl
from fixit_ai.temporal_alignment import build_temporal_lineage, build_temporal_overlay_summary, build_temporal_overlays


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outcomes-output", default=str(REPO_ROOT / "data/eval/replay/outcomes.temporal.jsonl"))
    parser.add_argument(
        "--teacher-output",
        default=str(REPO_ROOT / "data/eval/replay/manual_teacher_judgements.temporal.jsonl"),
    )
    parser.add_argument(
        "--training-output",
        default=str(REPO_ROOT / "data/eval/replay/training_examples.temporal.jsonl"),
    )
    parser.add_argument(
        "--incidents-output",
        default=str(REPO_ROOT / "data/eval/replay/historical_incidents.temporal.jsonl"),
    )
    parser.add_argument("--summary-output", default=str(REPO_ROOT / "data/eval/temporal-overlay-summary.json"))
    args = parser.parse_args()

    lineage = build_temporal_lineage(REPO_ROOT)
    overlays = build_temporal_overlays(REPO_ROOT, lineage=lineage)
    summary = build_temporal_overlay_summary(overlays)

    write_jsonl(args.outcomes_output, overlays["outcomes"])
    write_jsonl(args.teacher_output, overlays["manual_teacher_judgements"])
    write_jsonl(args.training_output, overlays["training_examples"])
    write_jsonl(args.incidents_output, overlays["historical_incidents"])
    write_json(args.summary_output, summary)
    print(
        "temporal overlays built "
        f"outcomes={len(overlays['outcomes'])} "
        f"training={len(overlays['training_examples'])} "
        f"incidents={len(overlays['historical_incidents'])} -> {args.summary_output}"
    )


if __name__ == "__main__":
    main()
