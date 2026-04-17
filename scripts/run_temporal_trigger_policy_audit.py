#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fixit_ai.common import write_json, write_text
from fixit_ai.temporal_alignment import (
    build_temporal_calibration_threshold_audit,
    build_temporal_trigger_policy_audit,
    render_temporal_calibration_threshold_audit_markdown,
    render_temporal_trigger_policy_audit_markdown,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trigger-output", default=str(REPO_ROOT / "data/eval/temporal-trigger-policy-audit.json"))
    parser.add_argument("--trigger-markdown-output", default=str(REPO_ROOT / "data/eval/temporal-trigger-policy-audit.md"))
    parser.add_argument("--calibration-output", default=str(REPO_ROOT / "data/eval/temporal-calibration-threshold-audit.json"))
    parser.add_argument(
        "--calibration-markdown-output",
        default=str(REPO_ROOT / "data/eval/temporal-calibration-threshold-audit.md"),
    )
    args = parser.parse_args()

    trigger_audit = build_temporal_trigger_policy_audit(REPO_ROOT)
    calibration_audit = build_temporal_calibration_threshold_audit(REPO_ROOT)

    write_json(args.trigger_output, trigger_audit)
    write_text(args.trigger_markdown_output, render_temporal_trigger_policy_audit_markdown(trigger_audit))
    write_json(args.calibration_output, calibration_audit)
    write_text(
        args.calibration_markdown_output,
        render_temporal_calibration_threshold_audit_markdown(calibration_audit),
    )
    print(
        "temporal trigger policy audit "
        f"folds={trigger_audit['fold_count']} policy_delta={trigger_audit['compare']['packets_with_policy_delta_gt_raw']}"
    )


if __name__ == "__main__":
    main()
