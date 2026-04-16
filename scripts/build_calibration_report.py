#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fixit_ai.calibration import build_calibration_report
from fixit_ai.common import read_jsonl, read_yaml, write_json, write_text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores", default=str(REPO_ROOT / "data/eval/student-scores.jsonl"))
    parser.add_argument("--outcomes", default=str(REPO_ROOT / "data/eval/replay/outcomes.jsonl"))
    parser.add_argument("--thresholds", default=str(REPO_ROOT / "configs/thresholds.yaml"))
    parser.add_argument("--json-out", default=str(REPO_ROOT / "data/eval/calibration-report.json"))
    parser.add_argument("--md-out", default=str(REPO_ROOT / "data/eval/calibration-report.md"))
    args = parser.parse_args()

    report = build_calibration_report(read_jsonl(args.scores), read_jsonl(args.outcomes), read_yaml(args.thresholds))
    write_json(args.json_out, report)
    lines = ["# Calibration Report", ""]
    for bucket in report["bucket_summary"]:
        lines.append(
            f"- bucket {bucket['range'][0]}-{bucket['range'][1]} count={bucket['count']} avg_score={bucket['avg_score']} actual_severe_rate={bucket['actual_severe_rate']}"
        )
    lines.extend([
        "",
        "## Threshold Review",
        f"- action: `{report['threshold_review']['recommended_action']}`",
        f"- reason: {report['threshold_review']['reason']}`".rstrip("`"),
    ])
    write_text(args.md_out, "\n".join(lines) + "\n")
    print(f"calibration report -> {args.json_out}")


if __name__ == "__main__":
    main()
