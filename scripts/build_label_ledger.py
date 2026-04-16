#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fixit_ai.common import read_jsonl, write_json
from fixit_ai.labeling import build_label_ledger


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--training", default=str(REPO_ROOT / "data/eval/replay/training_examples.jsonl"))
    parser.add_argument("--outcomes", default=str(REPO_ROOT / "data/eval/replay/outcomes.jsonl"))
    parser.add_argument("--output", default=str(REPO_ROOT / "data/eval/label-ledger.json"))
    args = parser.parse_args()

    ledger = build_label_ledger(read_jsonl(args.training), read_jsonl(args.outcomes))
    write_json(args.output, ledger)
    print(f"label ledger -> {args.output}")


if __name__ == "__main__":
    main()
