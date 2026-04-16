#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fixit_ai.common import read_jsonl, write_json
from fixit_ai.retrieval import retrieve_similar_incidents
from fixit_ai.retrieval_index import build_retrieval_index, search_retrieval_index


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", default=str(REPO_ROOT / "data/eval/replay/historical_incidents.jsonl"))
    parser.add_argument("--packets", default=str(REPO_ROOT / "data/samples/incident-packets.jsonl"))
    parser.add_argument("--index-out", default=str(REPO_ROOT / "data/eval/retrieval-index.json"))
    parser.add_argument("--compat-out", default=str(REPO_ROOT / "data/eval/retrieval-compat-readout.json"))
    args = parser.parse_args()

    incidents = read_jsonl(args.history)
    packets = read_jsonl(args.packets)
    index = build_retrieval_index(incidents)
    write_json(args.index_out, index)

    compat = []
    for packet in packets[:3]:
        legacy = retrieve_similar_incidents(packet, incidents, top_k=1)
        hardened = search_retrieval_index(packet, index, top_k=1)
        compat.append(
            {
                "packet_id": packet["packet_id"],
                "legacy_top_incident": legacy[0]["incident_id"] if legacy else None,
                "hardened_top_incident": hardened[0]["incident_id"] if hardened else None,
                "matched_terms": hardened[0].get("matched_terms", []) if hardened else [],
            }
        )
    write_json(args.compat_out, compat)
    print(f"retrieval index -> {args.index_out}; compat -> {args.compat_out}")


if __name__ == "__main__":
    main()
