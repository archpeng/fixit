#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fixit_ai.common import write_json, write_jsonl
from fixit_ai.temporal_alignment import build_temporal_alignment_summary, build_temporal_lineage


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lineage-output", default=str(REPO_ROOT / "data/eval/temporal-lineage.jsonl"))
    parser.add_argument("--summary-output", default=str(REPO_ROOT / "data/eval/temporal-alignment-summary.json"))
    args = parser.parse_args()

    lineage = build_temporal_lineage(REPO_ROOT)
    summary = build_temporal_alignment_summary(lineage)
    write_jsonl(args.lineage_output, lineage)
    write_json(args.summary_output, summary)
    print(
        "temporal lineage built "
        f"records={summary['record_count']} "
        f"cutoff_safe={summary['cutoff_safe_count']} -> {args.lineage_output}"
    )


if __name__ == "__main__":
    main()
