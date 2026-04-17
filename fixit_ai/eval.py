from __future__ import annotations


def compute_eval_metrics(decisions: list[dict], outcomes: list[dict], top_k: int = 3) -> dict:
    decision_packet_ids = {item["packet_id"] for item in decisions}
    relevant_outcomes = [item for item in outcomes if item.get("packet_id") in decision_packet_ids]
    outcomes_by_packet = {item["packet_id"]: item for item in relevant_outcomes}
    severe_packets = {item["packet_id"] for item in relevant_outcomes if item.get("actual_severe")}
    predicted_severe = {
        item["packet_id"] for item in decisions if item.get("final_priority") in {"P1", "P2"}
    }
    severe_hits = severe_packets & predicted_severe
    severe_recall = len(severe_hits) / len(severe_packets) if severe_packets else 0.0

    sorted_decisions = sorted(decisions, key=lambda item: item.get("decision_score", item["student_score"]), reverse=True)
    top = sorted_decisions[:top_k]
    top_k_precision = (
        sum(1 for item in top if outcomes_by_packet.get(item["packet_id"], {}).get("actual_severe")) / len(top)
        if top
        else 0.0
    )
    teacher_escalation_rate = (
        sum(1 for item in decisions if item.get("teacher_used")) / len(decisions) if decisions else 0.0
    )
    missed_severe = sorted(severe_packets - predicted_severe)

    return {
        "severe_recall": round(severe_recall, 4),
        "top_k_precision": round(top_k_precision, 4),
        "teacher_escalation_rate": round(teacher_escalation_rate, 4),
        "missed_severe_count": len(missed_severe),
        "missed_severe_packets": missed_severe,
    }
