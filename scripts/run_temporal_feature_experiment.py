#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fixit_ai.common import write_json, write_text
from fixit_ai.temporal_alignment import build_temporal_feature_experiment, render_temporal_feature_experiment_markdown


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(REPO_ROOT / "data/eval/temporal-feature-experiment.json"))
    parser.add_argument("--markdown-output", default=str(REPO_ROOT / "data/eval/temporal-feature-experiment.md"))
    args = parser.parse_args()

    result = build_temporal_feature_experiment(REPO_ROOT)
    write_json(args.output, result)
    write_text(args.markdown_output, render_temporal_feature_experiment_markdown(result))
    print(
        "temporal feature experiment "
        f"folds={result['fold_count']} -> {args.output}"
    )


if __name__ == "__main__":
    main()
