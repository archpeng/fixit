#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fixit_ai.candidate_generation import generate_candidate_windows, resolve_allowed_services
from fixit_ai.common import read_jsonl, read_yaml, write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(REPO_ROOT / "data/samples/raw/metrics_windows.jsonl"))
    parser.add_argument("--thresholds", default=str(REPO_ROOT / "configs/thresholds.yaml"))
    parser.add_argument("--services", default=str(REPO_ROOT / "configs/services.yaml"))
    parser.add_argument("--output", default=str(REPO_ROOT / "data/samples/candidate-windows.jsonl"))
    args = parser.parse_args()

    rows = read_jsonl(args.input)
    thresholds = read_yaml(args.thresholds)
    services = read_yaml(args.services)
    allowed = resolve_allowed_services(services)
    candidates = generate_candidate_windows(rows, thresholds, allowed_services=allowed)
    write_jsonl(args.output, candidates)
    print(f"generated {len(candidates)} candidate windows -> {args.output}")


if __name__ == "__main__":
    main()
