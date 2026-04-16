from __future__ import annotations

from typing import Iterable

from fixit_ai.eval import compute_eval_metrics
from fixit_ai.schema_tools import SchemaBundle


def _default_action_priority(score: float, thresholds: dict) -> tuple[str, str]:
    limits = thresholds["student"]["score_thresholds"]
    if score >= limits["p1"]:
        return "page_owner", "P1"
    if score >= limits["p2"]:
        return "page_owner", "P2"
    if score >= limits["p3"]:
        return "create_ticket", "P3"
    return "observe", "P4"


def _teacher_override(judgement: dict) -> tuple[str, str, float]:
    severity = judgement["severity"]
    if severity >= 4:
        return judgement["recommended_action"], "P1", 1.0
    if severity == 3:
        return judgement["recommended_action"], "P2", 0.85
    if severity == 2:
        return judgement["recommended_action"], "P3", 0.60
    return judgement["recommended_action"], "P4", 0.35


def build_triage_decisions(
    packets: Iterable[dict],
    retrieval_by_packet: dict[str, list[dict]],
    scores: list[dict],
    teacher_reviews: list[dict],
    thresholds: dict,
    schemas: SchemaBundle,
) -> list[dict]:
    teacher_by_packet = {item["packet_id"]: item for item in teacher_reviews}
    packet_by_id = {packet["packet_id"]: packet for packet in packets}

    decisions: list[dict] = []
    for score in scores:
        packet = packet_by_id[score["packet_id"]]
        final_action, final_priority = _default_action_priority(score["student_score"], thresholds)
        decision_score = score["student_score"]
        teacher_used = False
        if score["packet_id"] in teacher_by_packet:
            teacher_used = True
            final_action, final_priority, decision_score = _teacher_override(teacher_by_packet[score["packet_id"]])

        decision = {
            "packet_id": score["packet_id"],
            "student_score": score["student_score"],
            "student_confidence": score["student_confidence"],
            "novelty_score": score["novelty_score"],
            "rule_signals": packet.get("rules", {}).get("fired", []),
            "retrieval_refs": [ref["incident_id"] for ref in retrieval_by_packet.get(score["packet_id"], [])],
            "teacher_used": teacher_used,
            "final_action": final_action,
            "final_priority": final_priority,
            "explanations": list(score.get("explanations", [])),
            "decision_score": round(decision_score, 4),
        }
        schemas.validate("triage-decision.v1.json", decision)
        decisions.append(decision)

    return sorted(decisions, key=lambda item: item.get("decision_score", item["student_score"]), reverse=True)


def build_shadow_report_data(
    packets: list[dict],
    retrieval_by_packet: dict[str, list[dict]],
    decisions: list[dict],
    teacher_reviews: list[dict],
    outcomes: list[dict],
    services_cfg: dict,
    top_k: int,
) -> dict:
    packet_by_id = {packet["packet_id"]: packet for packet in packets}
    metrics = compute_eval_metrics(decisions, outcomes, top_k=top_k)
    top_candidates = []
    for decision in decisions[:top_k]:
        packet = packet_by_id[decision["packet_id"]]
        top_candidates.append(
            {
                "packet_id": decision["packet_id"],
                "service": packet["service"],
                "operation": packet.get("operation"),
                "final_priority": decision["final_priority"],
                "final_action": decision["final_action"],
                "student_score": decision["student_score"],
                "teacher_used": decision["teacher_used"],
            }
        )

    rule_missed_high_ranked = [
        candidate
        for candidate in top_candidates
        if not packet_by_id[candidate["packet_id"]].get("rules", {}).get("fired")
        and candidate["final_priority"] in {"P1", "P2"}
    ]

    routing_hints = []
    for candidate in top_candidates:
        packet = packet_by_id[candidate["packet_id"]]
        routing_hints.append(
            {
                "packet_id": candidate["packet_id"],
                "owner": packet.get("topology", {}).get("owner"),
                "repos": packet.get("topology", {}).get("repos", []),
                "similar_incidents": packet.get("memory", {}).get("recent_incidents", []),
            }
        )

    return {
        "pilot_family": services_cfg.get("pilot_family", {}),
        "metrics": metrics,
        "top_severe_candidates": top_candidates,
        "rule_missed_high_ranked": rule_missed_high_ranked,
        "teacher_reviewed_hard_cases": teacher_reviews,
        "owner_repo_routing_hints": routing_hints,
    }


def render_shadow_report_markdown(report: dict) -> str:
    lines = [
        "# Daily Shadow Report",
        "",
        f"- Pilot family: `{report['pilot_family'].get('name', 'unknown')}`",
        f"- Service: `{report['pilot_family'].get('service', 'unknown')}`",
        f"- Replay window: `{report['pilot_family'].get('replay_window', 'unknown')}`",
        "",
        "## Metrics",
        f"- severe recall: `{report['metrics']['severe_recall']}`",
        f"- top-K precision: `{report['metrics']['top_k_precision']}`",
        f"- teacher escalation rate: `{report['metrics']['teacher_escalation_rate']}`",
        f"- missed severe count: `{report['metrics']['missed_severe_count']}`",
        "",
        "## Top Severe Candidates",
    ]
    for item in report["top_severe_candidates"]:
        lines.append(
            f"- `{item['packet_id']}` `{item['final_priority']}` `{item['final_action']}` score={item['student_score']} teacher={item['teacher_used']}"
        )
    lines.extend(["", "## Rule-missed but model ranked high"]) 
    if report["rule_missed_high_ranked"]:
        for item in report["rule_missed_high_ranked"]:
            lines.append(f"- `{item['packet_id']}` -> `{item['final_priority']}` `{item['final_action']}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Teacher Reviewed Hard Cases"])
    if report["teacher_reviewed_hard_cases"]:
        for item in report["teacher_reviewed_hard_cases"]:
            lines.append(
                f"- `{item['packet_id']}` severity={item['severity']} confidence={item['confidence']} action={item['recommended_action']}"
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Owner / Repo Routing Hints"])
    for item in report["owner_repo_routing_hints"]:
        repos = ", ".join(item["repos"])
        similar = ", ".join(item["similar_incidents"])
        lines.append(f"- `{item['packet_id']}` owner=`{item['owner']}` repos=[{repos}] similar=[{similar}]")
    lines.append("")
    return "\n".join(lines)
