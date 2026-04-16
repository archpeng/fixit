from __future__ import annotations

from typing import Iterable

from fixit_ai.schema_tools import SchemaBundle


def _index_by(records: Iterable[dict], key: str) -> dict[str, dict]:
    return {record[key]: record for record in records}


def build_packets(
    candidates: Iterable[dict],
    log_rows: Iterable[dict],
    trace_rows: Iterable[dict],
    topology_rows: Iterable[dict],
    memory_rows: Iterable[dict],
    schemas: SchemaBundle,
) -> list[dict]:
    logs_by_window = _index_by(log_rows, "window_id")
    traces_by_window = _index_by(trace_rows, "window_id")
    topology_by_service = _index_by(topology_rows, "service")
    memory_by_service = _index_by(memory_rows, "service")

    packets: list[dict] = []
    for candidate in candidates:
        log_row = logs_by_window.get(candidate["window_id"], {"top_templates": [], "severity_mix": {}})
        trace_row = traces_by_window.get(
            candidate["window_id"],
            {"top_error_operation": candidate.get("operation"), "error_span_ratio": 0.0},
        )
        topology = topology_by_service.get(
            candidate["service"],
            {
                "tier": None,
                "owner": None,
                "repos": [],
                "blast_radius_score": 0.0,
                "upstream_count": 0,
                "downstream_count": 0,
            },
        )
        memory = memory_by_service.get(candidate["service"], {"similar_summaries": [], "recent_incidents": []})

        packet = {
            "packet_id": candidate["packet_id"],
            "ts_start": candidate["ts_start"],
            "ts_end": candidate["ts_end"],
            "env": candidate.get("env", "prod"),
            "service": candidate["service"],
            "operation": candidate.get("operation"),
            "metrics": dict(candidate["metrics"]),
            "logs": {
                "top_templates": list(log_row.get("top_templates", [])),
                "severity_mix": dict(log_row.get("severity_mix", {})),
            },
            "traces": {
                "top_error_operation": trace_row.get("top_error_operation"),
                "error_span_ratio": trace_row.get("error_span_ratio", 0.0),
                "status_message": trace_row.get("status_message"),
                "sample_trace_ids": list(trace_row.get("sample_trace_ids", [])),
            },
            "topology": {
                "tier": topology.get("tier"),
                "owner": topology.get("owner"),
                "repos": list(topology.get("repos", [])),
                "blast_radius_score": topology.get("blast_radius_score", 0.0),
                "upstream_count": topology.get("upstream_count", 0),
                "downstream_count": topology.get("downstream_count", 0),
            },
            "rules": dict(candidate["rules"]),
            "memory": {
                "similar_summaries": list(memory.get("similar_summaries", [])),
                "recent_incidents": list(memory.get("recent_incidents", [])),
            },
            "history": {
                "recent_deploy": bool(candidate.get("recent_deploy", False)),
            },
            "anomaly_signals": list(candidate.get("anomaly_signals", [])),
            "rule_missed": bool(candidate.get("rule_missed", False)),
        }
        schemas.validate("incident-packet.v1.json", packet)
        packets.append(packet)

    return packets
