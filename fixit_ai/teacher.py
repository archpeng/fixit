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


def _select_teacher_payloads(
    packets: Iterable[dict],
    retrieval_by_packet: dict[str, list[dict]],
    scores: list[dict],
    teacher_budget: dict,
) -> list[dict]:
    packet_by_id = {packet["packet_id"]: packet for packet in packets}
    cfg = teacher_budget["trigger_thresholds"]
    max_reviews = teacher_budget["max_reviews_per_run"]
    selected_payloads: list[dict] = []
    selected_packet_ids: set[str] = set()

    ranked_scores = sorted(scores, key=_severity_rank, reverse=True)
    for score in ranked_scores:
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
        if packet.get("rules", {}).get("fired") and score.get("student_score", 0.0) <= cfg.get("rule_alert_score_below", 0.0):
            triggers.append("rule_alert_score_conflict")

        if not triggers:
            continue
        selected_payloads.append(
            build_teacher_payload(packet, retrieval_by_packet.get(packet["packet_id"], []), score, triggers)
        )
        selected_packet_ids.add(packet["packet_id"])

    if teacher_budget.get("coverage_backfill_remaining_unreviewed", False) and len(selected_payloads) < max_reviews:
        coverage_trigger = teacher_budget.get("coverage_backfill_trigger", "bounded_review_gap_backfill")
        for score in ranked_scores:
            packet_id = score["packet_id"]
            if packet_id in selected_packet_ids:
                continue
            packet = packet_by_id[packet_id]
            selected_payloads.append(
                build_teacher_payload(packet, retrieval_by_packet.get(packet_id, []), score, [coverage_trigger])
            )
            selected_packet_ids.add(packet_id)
            if len(selected_payloads) >= max_reviews:
                break

    selected_payloads.sort(key=_severity_rank, reverse=True)
    return selected_payloads[:max_reviews]


def select_teacher_reviews(
    packets: Iterable[dict],
    retrieval_by_packet: dict[str, list[dict]],
    scores: list[dict],
    teacher_budget: dict,
    seed_judgements: Iterable[dict] | None = None,
) -> tuple[list[dict], list[dict]]:
    judgement_by_id = {item["packet_id"]: item for item in (seed_judgements or [])}
    selected_payloads = _select_teacher_payloads(packets, retrieval_by_packet, scores, teacher_budget)
    judgements = [judgement_by_id[item["packet_id"]] for item in selected_payloads if item["packet_id"] in judgement_by_id]
    return judgements, selected_payloads


def run_teacher_workflow(
    packets: Iterable[dict],
    retrieval_by_packet: dict[str, list[dict]],
    scores: list[dict],
    teacher_budget: dict,
    seed_judgements: Iterable[dict] | None = None,
) -> dict:
    judgement_by_id = {item["packet_id"]: item for item in (seed_judgements or [])}
    selected_payloads = _select_teacher_payloads(packets, retrieval_by_packet, scores, teacher_budget)

    judgements: list[dict] = []
    requests: list[dict] = []
    reviews: list[dict] = []
    fallbacks: list[dict] = []

    for payload in selected_payloads:
        packet_id = payload["packet_id"]
        request = {
            "packet_id": packet_id,
            "service": payload["service"],
            "operation": payload.get("operation"),
            "triggers": payload.get("triggers", []),
        }
        if packet_id in judgement_by_id:
            judgement = judgement_by_id[packet_id]
            judgements.append(judgement)
            reviews.append(
                {
                    "packet_id": packet_id,
                    "review_state": "reviewed",
                    "recommended_action": judgement["recommended_action"],
                    "confidence": judgement["confidence"],
                }
            )
            request["state"] = "reviewed"
        else:
            fallback = {
                "packet_id": packet_id,
                "fallback_action": teacher_budget["fallback_action"],
                "reason": "teacher judgement unavailable for selected hard case",
                "triggers": payload.get("triggers", []),
            }
            fallbacks.append(fallback)
            request["state"] = "fallback"
        requests.append(request)

    summary = {
        "selected_count": len(selected_payloads),
        "reviewed_count": len(reviews),
        "fallback_count": len(fallbacks),
        "pending_count": 0,
    }
    return {
        "judgements": judgements,
        "payloads": selected_payloads,
        "requests": requests,
        "reviews": reviews,
        "fallbacks": fallbacks,
        "summary": summary,
    }
