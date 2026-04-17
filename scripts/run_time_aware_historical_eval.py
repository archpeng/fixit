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
    build_episode_index,
    build_temporal_overlays,
    render_time_aware_eval_markdown,
    run_time_aware_historical_eval,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episode-index-output", default=str(REPO_ROOT / "data/eval/episode-index.json"))
    parser.add_argument("--eval-output", default=str(REPO_ROOT / "data/eval/time-aware-eval.json"))
    parser.add_argument("--markdown-output", default=str(REPO_ROOT / "data/eval/time-aware-eval.md"))
    args = parser.parse_args()

    overlays = build_temporal_overlays(REPO_ROOT)
    episodes = build_episode_index(REPO_ROOT, overlays=overlays)
    result = run_time_aware_historical_eval(REPO_ROOT)

    write_json(args.episode_index_output, {"episodes": episodes})
    write_json(args.eval_output, result)
    write_text(args.markdown_output, render_time_aware_eval_markdown(result))
    print(
        "time-aware historical eval "
        f"episodes={result['episode_count']} packets={result['packet_count']} -> {args.eval_output}"
    )


if __name__ == "__main__":
    main()
