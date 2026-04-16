from __future__ import annotations

import re
from typing import Iterable

TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")


def _tokenize(*parts: str | None) -> set[str]:
    tokens: set[str] = set()
    for part in parts:
        if not part:
            continue
        tokens.update(token.lower() for token in TOKEN_RE.findall(part))
    return tokens


def _packet_text(packet: dict) -> str:
    templates = " ".join(item.get("template", "") for item in packet.get("logs", {}).get("top_templates", []))
    status_message = packet.get("traces", {}).get("status_message", "")
    return " ".join(filter(None, [packet.get("service"), packet.get("operation"), templates, status_message]))


def retrieve_similar_incidents(packet: dict, incidents: Iterable[dict], top_k: int = 3) -> list[dict]:
    packet_tokens = _tokenize(_packet_text(packet))
    results: list[dict] = []

    for incident in incidents:
        incident_tokens = _tokenize(
            incident.get("service"),
            incident.get("operation"),
            incident.get("summary"),
            " ".join(incident.get("tags", [])),
        )
        overlap = len(packet_tokens & incident_tokens)
        union = len(packet_tokens | incident_tokens) or 1
        jaccard = overlap / union
        service_bonus = 0.30 if incident.get("service") == packet.get("service") else 0.0
        operation_bonus = 0.25 if incident.get("operation") == packet.get("operation") else 0.0
        severe_bonus = 0.10 if incident.get("severity") == "severe" and overlap else 0.0
        similarity_score = min(1.0, jaccard + service_bonus + operation_bonus + severe_bonus)
        results.append(
            {
                "incident_id": incident["incident_id"],
                "similarity_score": round(similarity_score, 4),
                "severity": incident.get("severity", "unknown"),
                "recommended_action": incident.get("recommended_action", "observe"),
                "summary": incident.get("summary", ""),
            }
        )

    return sorted(results, key=lambda item: item["similarity_score"], reverse=True)[:top_k]
