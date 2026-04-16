from __future__ import annotations

from typing import Iterable


def build_calibration_report(scores: list[dict], outcomes: Iterable[dict], thresholds: dict) -> dict:
    outcomes_by_packet = {item["packet_id"]: item for item in outcomes}
    bucket_edges = [(0.0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.01)]
    bucket_summary = []
    for start, end in bucket_edges:
        bucket = [item for item in scores if start <= item["student_score"] < end]
        if bucket:
            actual_rate = sum(1 for item in bucket if outcomes_by_packet.get(item["packet_id"], {}).get("actual_severe")) / len(bucket)
            avg_score = sum(item["student_score"] for item in bucket) / len(bucket)
        else:
            actual_rate = 0.0
            avg_score = 0.0
        bucket_summary.append(
            {
                "range": [start, min(end, 1.0)],
                "count": len(bucket),
                "avg_score": round(avg_score, 4),
                "actual_severe_rate": round(actual_rate, 4),
            }
        )

    limits = thresholds["student"]["score_thresholds"]
    severe_scores = [item["student_score"] for item in scores if outcomes_by_packet.get(item["packet_id"], {}).get("actual_severe")]
    non_severe_scores = [item["student_score"] for item in scores if not outcomes_by_packet.get(item["packet_id"], {}).get("actual_severe")]
    recommended_action = "keep"
    reason = "Current replay evidence does not justify changing the MVP thresholds."
    if severe_scores and min(severe_scores) < limits["p2"]:
        recommended_action = "adjust"
        reason = "At least one severe packet falls below the current P2 threshold in the expanded replay pack."
    elif non_severe_scores and max(non_severe_scores) >= limits["p1"]:
        recommended_action = "adjust"
        reason = "A non-severe packet crosses the current P1 threshold in the expanded replay pack."

    return {
        "bucket_summary": bucket_summary,
        "threshold_review": {
            "recommended_action": recommended_action,
            "current_thresholds": limits,
            "reason": reason,
        },
    }
