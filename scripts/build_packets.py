#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fixit_ai.common import read_jsonl, read_yaml, write_json, write_jsonl
from fixit_ai.enrichment import apply_live_first_enrichment, summarize_enrichment_usage
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
    parser.add_argument("--services-config", default=None)
    parser.add_argument("--live-enrichment", default=None)
    parser.add_argument("--enrichment-usage", default=None)
    parser.add_argument("--output", default=str(REPO_ROOT / "data/samples/incident-packets.jsonl"))
    args = parser.parse_args()

    topology_rows = read_jsonl(args.topology)
    if args.services_config:
        services_cfg = read_yaml(args.services_config)
        config_map = {row["service"]: row for row in topology_rows}
        for service, override in services_cfg.get("service_overrides", {}).items():
            config_map[service] = {"service": service, **override}
        live_records = read_jsonl(args.live_enrichment) if args.live_enrichment and Path(args.live_enrichment).exists() else []
        topology_rows, usage = apply_live_first_enrichment(topology_rows, config_map, live_records)
        if args.enrichment_usage:
            write_json(args.enrichment_usage, summarize_enrichment_usage(usage))

    packets = build_packets(
        read_jsonl(args.candidates),
        read_jsonl(args.logs),
        read_jsonl(args.traces),
        topology_rows,
        read_jsonl(args.memory),
        SchemaBundle(args.schemas),
    )
    write_jsonl(args.output, packets)
    print(f"built {len(packets)} packets -> {args.output}")


if __name__ == "__main__":
    main()
