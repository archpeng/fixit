from __future__ import annotations

import math
import re
from datetime import datetime
from collections import Counter, defaultdict
from typing import Iterable

TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")


def _tokenize(*parts: str | None) -> list[str]:
    tokens: list[str] = []
    for part in parts:
        if not part:
            continue
        tokens.extend(token.lower() for token in TOKEN_RE.findall(part))
    return tokens


def _packet_tokens(packet: dict) -> list[str]:
    templates = " ".join(item.get("template", "") for item in packet.get("logs", {}).get("top_templates", []))
    status = packet.get("traces", {}).get("status_message", "")
    return _tokenize(packet.get("service"), packet.get("operation"), templates, status)


def build_retrieval_index(incidents: Iterable[dict]) -> dict:
    docs = []
    doc_freq = defaultdict(int)
    for incident in incidents:
        tokens = _tokenize(
            incident.get("service"),
            incident.get("operation"),
            incident.get("summary"),
            " ".join(incident.get("tags", [])),
        )
        counter = Counter(tokens)
        docs.append({"incident": incident, "tokens": counter})
        for token in counter:
            doc_freq[token] += 1
    size = len(docs) or 1
    idf = {token: math.log((1 + size) / (1 + freq)) + 1.0 for token, freq in doc_freq.items()}
    return {"docs": docs, "idf": idf, "size": size}


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _recency_bonus(reference_ts: str | None, incident_ts: str | None, half_life_minutes: int | None) -> float:
    if not reference_ts or not incident_ts or not half_life_minutes or half_life_minutes <= 0:
        return 0.0
    ref = _parse_ts(reference_ts)
    inc = _parse_ts(incident_ts)
    if not ref or not inc or inc > ref:
        return 0.0
    gap_minutes = max((ref - inc).total_seconds() / 60.0, 0.0)
    decay = math.exp(-math.log(2) * (gap_minutes / half_life_minutes))
    return 0.20 * decay


def search_retrieval_index(
    packet: dict,
    index: dict,
    top_k: int = 3,
    reference_ts: str | None = None,
    recency_half_life_minutes: int | None = None,
) -> list[dict]:
    packet_counter = Counter(_packet_tokens(packet))
    results = []
    for doc in index.get("docs", []):
        incident = doc["incident"]
        matched_terms = sorted(set(packet_counter) & set(doc["tokens"]))
        overlap_score = sum(index["idf"].get(token, 1.0) * min(packet_counter[token], doc["tokens"][token]) for token in matched_terms)
        service_bonus = 0.30 if incident.get("service") == packet.get("service") else 0.0
        operation_bonus = 0.25 if incident.get("operation") == packet.get("operation") else 0.0
        severe_bonus = 0.10 if incident.get("severity") == "severe" and matched_terms else 0.0
        recency_bonus = _recency_bonus(reference_ts, incident.get("derived_ts_end"), recency_half_life_minutes)
        score = overlap_score + service_bonus + operation_bonus + severe_bonus + recency_bonus
        results.append(
            {
                "incident_id": incident["incident_id"],
                "similarity_score": round(score, 4),
                "severity": incident.get("severity", "unknown"),
                "recommended_action": incident.get("recommended_action", "observe"),
                "summary": incident.get("summary", ""),
                "matched_terms": matched_terms,
                "recency_bonus": round(recency_bonus, 4),
            }
        )
    return sorted(results, key=lambda item: item["similarity_score"], reverse=True)[:top_k]
