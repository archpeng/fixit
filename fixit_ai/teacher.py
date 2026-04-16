from __future__ import annotations

from typing import Iterable


def _severity_rank(score: dict) -> float:
    return score.get("novelty_score", 0.0) + score.get("student_score", 0.0)


def build_teacher_payload(packet: dict, retrieval_refs: list[dict], score: dict, triggers: list[str]) -> dict:
    return {
        "packet_id": packet["packet_id"],
        "service": packet["service"],
        "operation": packet.get("operation"),
        "triggers": triggers,
        "metrics_summary": {
            "error_rate_delta": packet.get("metrics", {}).get("error_rate_delta", 0.0),
            "p95_delta": packet.get("metrics", {}).get("p95_delta", 0.0),
            "qps_delta": packet.get("metrics", {}).get("qps_delta", 0.0),
        },
        "top_log_templates": [item.get("template") for item in packet.get("logs", {}).get("top_templates", [])[:2]],
        "retrieval_refs": [ref["incident_id"] for ref in retrieval_refs[:2]],
        "student_summary": {
            "score": score.get("student_score", 0.0),
            "confidence": score.get("student_confidence", 0.0),
            "novelty": score.get("novelty_score", 0.0),
        },
    }


def select_teacher_reviews(
    packets: Iterable[dict],
    retrieval_by_packet: dict[str, list[dict]],
    scores: list[dict],
    teacher_budget: dict,
    seed_judgements: Iterable[dict] | None = None,
) -> tuple[list[dict], list[dict]]:
    packet_by_id = {packet["packet_id"]: packet for packet in packets}
    judgement_by_id = {item["packet_id"]: item for item in (seed_judgements or [])}
    cfg = teacher_budget["trigger_thresholds"]

    selected_payloads: list[dict] = []
    for score in scores:
        packet = packet_by_id[score["packet_id"]]
        triggers: list[str] = []
        if score.get("student_confidence", 0.0) < cfg["confidence_below"]:
            triggers.append("low_confidence")
        if score.get("novelty_score", 0.0) >= cfg["novelty_at_or_above"]:
            triggers.append("high_novelty")
        if packet.get("topology", {}).get("blast_radius_score", 0.0) >= cfg["blast_radius_at_or_above"]:
            triggers.append("high_blast_radius")
        if score.get("student_score", 0.0) >= cfg["severity_score_at_or_above"] and not packet.get("rules", {}).get("fired"):
            triggers.append("rule_missed_high_score")

        if not triggers:
            continue
        selected_payloads.append(
            build_teacher_payload(packet, retrieval_by_packet.get(packet["packet_id"], []), score, triggers)
        )

    selected_payloads.sort(key=_severity_rank, reverse=True)
    selected_payloads = selected_payloads[: teacher_budget["max_reviews_per_run"]]
    judgements = [judgement_by_id[item["packet_id"]] for item in selected_payloads if item["packet_id"] in judgement_by_id]
    return judgements, selected_payloads
