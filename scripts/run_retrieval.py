#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fixit_ai.common import read_jsonl, write_jsonl
from fixit_ai.retrieval import retrieve_similar_incidents


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packets", default=str(REPO_ROOT / "data/samples/incident-packets.jsonl"))
    parser.add_argument("--history", default=str(REPO_ROOT / "data/eval/historical_incidents.jsonl"))
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--output", default=str(REPO_ROOT / "data/samples/retrieval-results.jsonl"))
    args = parser.parse_args()

    packets = read_jsonl(args.packets)
    incidents = read_jsonl(args.history)
    records = [
        {"packet_id": packet["packet_id"], "references": retrieve_similar_incidents(packet, incidents, top_k=args.top_k)}
        for packet in packets
    ]
    write_jsonl(args.output, records)
    print(f"retrieval results for {len(records)} packets -> {args.output}")


if __name__ == "__main__":
    main()
