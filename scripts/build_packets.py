#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fixit_ai.common import read_jsonl, write_jsonl
from fixit_ai.packet_builder import build_packets
from fixit_ai.schema_tools import SchemaBundle


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", default=str(REPO_ROOT / "data/samples/candidate-windows.jsonl"))
    parser.add_argument("--logs", default=str(REPO_ROOT / "data/samples/raw/log_evidence.jsonl"))
    parser.add_argument("--traces", default=str(REPO_ROOT / "data/samples/raw/trace_evidence.jsonl"))
    parser.add_argument("--topology", default=str(REPO_ROOT / "data/samples/raw/topology.jsonl"))
    parser.add_argument("--memory", default=str(REPO_ROOT / "data/samples/raw/memory_summaries.jsonl"))
    parser.add_argument("--schemas", default=str(REPO_ROOT / "schemas"))
    parser.add_argument("--output", default=str(REPO_ROOT / "data/samples/incident-packets.jsonl"))
    args = parser.parse_args()

    packets = build_packets(
        read_jsonl(args.candidates),
        read_jsonl(args.logs),
        read_jsonl(args.traces),
        read_jsonl(args.topology),
        read_jsonl(args.memory),
        SchemaBundle(args.schemas),
    )
    write_jsonl(args.output, packets)
    print(f"built {len(packets)} packets -> {args.output}")


if __name__ == "__main__":
    main()
