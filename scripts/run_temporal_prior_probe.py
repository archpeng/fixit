#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fixit_ai.common import write_json, write_jsonl, write_text
from fixit_ai.temporal_alignment import (
    build_temporal_prior_catalog,
    build_temporal_prior_probe,
    build_temporal_prior_summary,
    render_temporal_prior_probe_markdown,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog-output", default=str(REPO_ROOT / "data/eval/temporal-prior-catalog.jsonl"))
    parser.add_argument("--summary-output", default=str(REPO_ROOT / "data/eval/temporal-prior-summary.json"))
    parser.add_argument("--probe-output", default=str(REPO_ROOT / "data/eval/temporal-prior-probe.json"))
    parser.add_argument("--markdown-output", default=str(REPO_ROOT / "data/eval/temporal-prior-probe.md"))
    args = parser.parse_args()

    priors = build_temporal_prior_catalog(REPO_ROOT)
    summary = build_temporal_prior_summary(priors)
    probe = build_temporal_prior_probe(REPO_ROOT)

    write_jsonl(args.catalog_output, priors)
    write_json(args.summary_output, summary)
    write_json(args.probe_output, probe)
    write_text(args.markdown_output, render_temporal_prior_probe_markdown(probe))
    print(
        "temporal prior probe "
        f"priors={len(priors)} folds={probe['fold_count']} -> {args.probe_output}"
    )


if __name__ == "__main__":
    main()
