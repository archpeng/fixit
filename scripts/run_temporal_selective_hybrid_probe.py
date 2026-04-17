#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fixit_ai.common import write_json, write_text
from fixit_ai.temporal_alignment import build_temporal_selective_hybrid_probe, render_temporal_selective_hybrid_probe_markdown


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(REPO_ROOT / "data/eval/temporal-selective-hybrid-probe.json"))
    parser.add_argument("--markdown-output", default=str(REPO_ROOT / "data/eval/temporal-selective-hybrid-probe.md"))
    args = parser.parse_args()

    result = build_temporal_selective_hybrid_probe(REPO_ROOT)
    write_json(args.output, result)
    write_text(args.markdown_output, render_temporal_selective_hybrid_probe_markdown(result))
    print(
        "temporal selective hybrid probe "
        f"folds={result['fold_count']} -> {args.output}"
    )


if __name__ == "__main__":
    main()
