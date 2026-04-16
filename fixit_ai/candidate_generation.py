from __future__ import annotations

from typing import Iterable


def _count_numeric_signals(row: dict, cfg: dict) -> int:
    count = 0
    if row.get("error_rate_delta", 0.0) >= cfg["error_rate_delta"]:
        count += 1
    if row.get("p95_delta", 0.0) >= cfg["p95_delta"]:
        count += 1
    if row.get("qps_delta", 0.0) >= cfg["qps_delta"]:
        count += 1
    if row.get("saturation_delta", 0.0) >= cfg["saturation_delta"]:
        count += 1
    return count


def generate_candidate_windows(
    metrics_rows: Iterable[dict],
    thresholds: dict,
    allowed_services: set[str] | None = None,
) -> list[dict]:
    cfg = thresholds["candidate_generation"]
    candidates: list[dict] = []

    for row in metrics_rows:
        if allowed_services and row.get("service") not in allowed_services:
            continue

        anomaly_signals: list[str] = []
        rules = row.get("rules", {"fired": [], "scores": {}})
        if rules.get("fired"):
            anomaly_signals.append("rule_alert")
        if row.get("error_rate_delta", 0.0) >= cfg["error_rate_delta"]:
            anomaly_signals.append("error_rate_delta")
        if row.get("p95_delta", 0.0) >= cfg["p95_delta"]:
            anomaly_signals.append("latency_shift")
        if row.get("qps_delta", 0.0) >= cfg["qps_delta"]:
            anomaly_signals.append("traffic_shift")
        if row.get("saturation_delta", 0.0) >= cfg["saturation_delta"]:
            anomaly_signals.append("saturation_shift")

        numeric_signal_count = _count_numeric_signals(row, cfg)
        if numeric_signal_count >= cfg["multi_signal_min"]:
            anomaly_signals.append("multi_signal_shift")

        if not anomaly_signals:
            continue

        candidate = {
            "window_id": row["window_id"],
            "packet_id": f"ipk_{row['window_id']}",
            "service": row["service"],
            "operation": row.get("operation"),
            "env": row.get("env", "prod"),
            "ts_start": row["ts_start"],
            "ts_end": row["ts_end"],
            "metrics": {
                "error_rate": row.get("error_rate", 0.0),
                "error_rate_delta": row.get("error_rate_delta", 0.0),
                "p95_delta": row.get("p95_delta", 0.0),
                "p99_delta": row.get("p99_delta", 0.0),
                "qps_delta": row.get("qps_delta", 0.0),
                "alert_firing_duration_s": row.get("alert_firing_duration_s", 0.0),
                "current_calls": row.get("current_calls", 0.0),
                "current_errors": row.get("current_errors", 0.0),
            },
            "rules": {
                "fired": list(rules.get("fired", [])),
                "scores": dict(rules.get("scores", {})),
            },
            "recent_deploy": bool(row.get("recent_deploy", False)),
            "anomaly_signals": anomaly_signals,
            "rule_missed": not bool(rules.get("fired")),
        }
        candidates.append(candidate)

    return candidates
