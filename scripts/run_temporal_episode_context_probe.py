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
    build_episode_context_priors,
    build_temporal_episode_context_probe,
    build_temporal_prior_catalog,
    build_temporal_prior_summary,
    render_temporal_episode_context_probe_markdown,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--priors-output", default=str(REPO_ROOT / "data/eval/temporal-episode-context-priors.jsonl"))
    parser.add_argument("--summary-output", default=str(REPO_ROOT / "data/eval/temporal-episode-context-summary.json"))
    parser.add_argument("--probe-output", default=str(REPO_ROOT / "data/eval/temporal-episode-context-probe.json"))
    parser.add_argument("--markdown-output", default=str(REPO_ROOT / "data/eval/temporal-episode-context-probe.md"))
    args = parser.parse_args()

    packet_priors = build_temporal_prior_catalog(REPO_ROOT)
    episode_context_priors = build_episode_context_priors(packet_priors)
    summary = build_temporal_prior_summary(episode_context_priors)
    probe = build_temporal_episode_context_probe(REPO_ROOT)

    write_jsonl(args.priors_output, episode_context_priors)
    write_json(args.summary_output, summary)
    write_json(args.probe_output, probe)
    write_text(args.markdown_output, render_temporal_episode_context_probe_markdown(probe))
    print(
        "temporal episode-context probe "
        f"priors={len(episode_context_priors)} folds={probe['fold_count']} -> {args.probe_output}"
    )


if __name__ == "__main__":
    main()
