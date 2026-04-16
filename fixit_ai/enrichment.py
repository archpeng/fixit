from __future__ import annotations

from typing import Iterable


def apply_live_first_enrichment(
    topology_rows: Iterable[dict],
    config_map: dict[str, dict],
    live_records: Iterable[dict],
) -> tuple[list[dict], list[dict]]:
    live_by_service = {item["service"]: item for item in live_records}
    enriched_rows: list[dict] = []
    usage: list[dict] = []

    for row in topology_rows:
        service = row["service"]
        if service in live_by_service:
            source = "live"
            payload = dict(live_by_service[service])
            reason = "live record available"
        else:
            source = "config_fallback"
            payload = dict(config_map.get(service, row))
            reason = "live record missing"
        enriched_rows.append(payload)
        usage.append({"service": service, "source": source, "reason": reason})

    return enriched_rows, usage


def summarize_enrichment_usage(usage: Iterable[dict]) -> dict:
    usage = list(usage)
    return {
        "total_count": len(usage),
        "live_count": sum(1 for item in usage if item.get("source") == "live"),
        "fallback_count": sum(1 for item in usage if item.get("source") == "config_fallback"),
        "details": usage,
    }
