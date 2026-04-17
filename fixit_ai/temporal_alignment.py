from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from fixit_ai.common import read_jsonl, read_yaml
from fixit_ai.eval import compute_eval_metrics
from fixit_ai.retrieval_index import build_retrieval_index, search_retrieval_index
from fixit_ai.schema_tools import SchemaBundle
from fixit_ai.shadow import build_triage_decisions
from fixit_ai.student import TEMPORAL_FEATURE_NAMES, predict_packets, train_student_model

TIME_HINT_RE = re.compile(r"\b(20\d{2}-\d{2}-\d{2}|20\d{2}-\d{2})\b")


def _packet_time_index(root: Path) -> dict[str, dict[str, Any]]:
    packets = read_jsonl(root / "data/samples/incident-packets.jsonl")
    return {
        packet["packet_id"]: {
            "packet_id": packet["packet_id"],
            "derived_ts_start": packet.get("ts_start"),
            "derived_ts_end": packet.get("ts_end"),
            "service": packet.get("service"),
            "operation": packet.get("operation"),
        }
        for packet in packets
        if packet.get("packet_id")
    }


def _time_hints(*texts: str | None) -> list[str]:
    hints: set[str] = set()
    for text in texts:
        if not text:
            continue
        hints.update(TIME_HINT_RE.findall(text))
    return sorted(hints)


def _lineage_record(
    *,
    record_type: str,
    record_id: str,
    source_path: str,
    derived_ts_start: str | None,
    derived_ts_end: str | None,
    time_granularity: str,
    timestamp_quality: str,
    time_source: str,
    time_source_refs: list[str] | None = None,
    cutoff_safe: bool = False,
    packet_id: str | None = None,
    derived_time_hints: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "record_type": record_type,
        "record_id": record_id,
        "source_path": source_path,
        "packet_id": packet_id,
        "derived_ts_start": derived_ts_start,
        "derived_ts_end": derived_ts_end,
        "time_granularity": time_granularity,
        "timestamp_quality": timestamp_quality,
        "time_source": time_source,
        "time_source_refs": list(time_source_refs or []),
        "derived_time_hints": list(derived_time_hints or []),
        "cutoff_safe": cutoff_safe,
    }


def build_temporal_lineage(root: Path | str) -> list[dict[str, Any]]:
    root = Path(root)
    packet_index = _packet_time_index(root)
    lineage: list[dict[str, Any]] = []

    for packet_id, packet in sorted(packet_index.items()):
        lineage.append(
            _lineage_record(
                record_type="packet",
                record_id=packet_id,
                source_path="data/samples/incident-packets.jsonl",
                packet_id=packet_id,
                derived_ts_start=packet["derived_ts_start"],
                derived_ts_end=packet["derived_ts_end"],
                time_granularity="window",
                timestamp_quality="exact_window_time",
                time_source="packet_window",
                time_source_refs=[packet_id],
                cutoff_safe=True,
            )
        )

    for outcome in read_jsonl(root / "data/eval/outcomes.jsonl"):
        packet_id = outcome.get("packet_id")
        packet = packet_index.get(packet_id)
        lineage.append(
            _lineage_record(
                record_type="outcome",
                record_id=packet_id or "unknown_outcome",
                source_path="data/eval/outcomes.jsonl",
                packet_id=packet_id,
                derived_ts_start=packet.get("derived_ts_start") if packet else None,
                derived_ts_end=packet.get("derived_ts_end") if packet else None,
                time_granularity="window" if packet else "unknown",
                timestamp_quality="exact_time_inherited" if packet else "unknown_time",
                time_source="packet_id" if packet else "missing_packet_id",
                time_source_refs=[packet_id] if packet_id else [],
                cutoff_safe=bool(packet),
            )
        )

    for judgement in read_jsonl(root / "data/eval/manual_teacher_judgements.jsonl"):
        packet_id = judgement.get("packet_id")
        packet = packet_index.get(packet_id)
        lineage.append(
            _lineage_record(
                record_type="manual_teacher_judgement",
                record_id=packet_id or "unknown_teacher_judgement",
                source_path="data/eval/manual_teacher_judgements.jsonl",
                packet_id=packet_id,
                derived_ts_start=packet.get("derived_ts_start") if packet else None,
                derived_ts_end=packet.get("derived_ts_end") if packet else None,
                time_granularity="window" if packet else "unknown",
                timestamp_quality="exact_time_inherited" if packet else "unknown_time",
                time_source="packet_id" if packet else "missing_packet_id",
                time_source_refs=[packet_id] if packet_id else [],
                cutoff_safe=bool(packet),
            )
        )

    for training in read_jsonl(root / "data/eval/training_examples.jsonl"):
        example_id = training.get("example_id", "unknown_training_example")
        packet_id = training.get("packet_id")
        packet = packet_index.get(packet_id)
        if packet:
            lineage.append(
                _lineage_record(
                    record_type="training_example",
                    record_id=example_id,
                    source_path="data/eval/training_examples.jsonl",
                    packet_id=packet_id,
                    derived_ts_start=packet["derived_ts_start"],
                    derived_ts_end=packet["derived_ts_end"],
                    time_granularity="window",
                    timestamp_quality="exact_time_inherited",
                    time_source="packet_id",
                    time_source_refs=[packet_id],
                    cutoff_safe=True,
                )
            )
        else:
            lineage.append(
                _lineage_record(
                    record_type="training_example",
                    record_id=example_id,
                    source_path="data/eval/training_examples.jsonl",
                    packet_id=packet_id,
                    derived_ts_start=None,
                    derived_ts_end=None,
                    time_granularity="unknown",
                    timestamp_quality="unknown_time",
                    time_source="unlinked_training_example",
                    time_source_refs=[packet_id] if packet_id else [],
                    cutoff_safe=False,
                )
            )

    for incident in read_jsonl(root / "data/eval/historical_incidents.jsonl"):
        incident_id = incident.get("incident_id", "unknown_historical_incident")
        source_packet_ids = [packet_id for packet_id in incident.get("source_packet_ids", []) if packet_id]
        if incident.get("source_packet_id"):
            source_packet_ids.append(incident["source_packet_id"])
        source_packet_ids = list(dict.fromkeys(source_packet_ids))
        source_packets = [packet_index[packet_id] for packet_id in source_packet_ids if packet_id in packet_index]
        if source_packets and len(source_packets) == len(source_packet_ids):
            lineage.append(
                _lineage_record(
                    record_type="historical_incident",
                    record_id=incident_id,
                    source_path="data/eval/historical_incidents.jsonl",
                    derived_ts_start=min(packet["derived_ts_start"] for packet in source_packets),
                    derived_ts_end=max(packet["derived_ts_end"] for packet in source_packets),
                    time_granularity="episode",
                    timestamp_quality="exact_time_inherited",
                    time_source="source_packet_ids",
                    time_source_refs=source_packet_ids,
                    cutoff_safe=True,
                )
            )
        else:
            lineage.append(
                _lineage_record(
                    record_type="historical_incident",
                    record_id=incident_id,
                    source_path="data/eval/historical_incidents.jsonl",
                    derived_ts_start=None,
                    derived_ts_end=None,
                    time_granularity="unknown",
                    timestamp_quality="unknown_time",
                    time_source="missing_source_packet_ids",
                    time_source_refs=source_packet_ids,
                    cutoff_safe=False,
                )
            )

    for memory in read_jsonl(root / "data/samples/replay/memory_summaries.jsonl"):
        service = memory.get("service", "unknown_service")
        hints = _time_hints(
            *(memory.get("similar_summaries", []) or []),
            *(memory.get("recent_incidents", []) or []),
        )
        lineage.append(
            _lineage_record(
                record_type="memory_summary",
                record_id=service,
                source_path="data/samples/replay/memory_summaries.jsonl",
                derived_ts_start=None,
                derived_ts_end=None,
                time_granularity="month_hint" if hints else "unknown",
                timestamp_quality="coarse_text_time" if hints else "unknown_time",
                time_source="text_time_hint" if hints else "no_time_hint",
                derived_time_hints=hints,
                cutoff_safe=False,
            )
        )

    lineage.sort(key=lambda item: (item["record_type"], item["record_id"]))
    return lineage


def build_temporal_alignment_summary(lineage: list[dict[str, Any]]) -> dict[str, Any]:
    counts_by_quality: dict[str, int] = {}
    counts_by_record_type: dict[str, int] = {}
    exact_starts: list[str] = []
    exact_ends: list[str] = []

    for item in lineage:
        quality = item.get("timestamp_quality", "unknown")
        counts_by_quality[quality] = counts_by_quality.get(quality, 0) + 1
        record_type = item.get("record_type", "unknown")
        counts_by_record_type[record_type] = counts_by_record_type.get(record_type, 0) + 1
        if quality in {"exact_window_time", "exact_time_inherited"}:
            if item.get("derived_ts_start"):
                exact_starts.append(item["derived_ts_start"])
            if item.get("derived_ts_end"):
                exact_ends.append(item["derived_ts_end"])

    cutoff_safe_count = sum(1 for item in lineage if item.get("cutoff_safe"))
    return {
        "record_count": len(lineage),
        "counts_by_timestamp_quality": counts_by_quality,
        "counts_by_record_type": counts_by_record_type,
        "cutoff_safe_count": cutoff_safe_count,
        "exact_time_range": {
            "earliest": min(exact_starts) if exact_starts else None,
            "latest": max(exact_ends) if exact_ends else None,
        },
    }


def _lineage_lookup(lineage: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {(item["record_type"], item["record_id"]): item for item in lineage}


def _merge_temporal_fields(row: dict[str, Any], lineage_item: dict[str, Any]) -> dict[str, Any]:
    merged = dict(row)
    merged["derived_ts_start"] = lineage_item.get("derived_ts_start")
    merged["derived_ts_end"] = lineage_item.get("derived_ts_end")
    merged["time_granularity"] = lineage_item.get("time_granularity")
    merged["timestamp_quality"] = lineage_item.get("timestamp_quality")
    merged["time_source"] = lineage_item.get("time_source")
    merged["time_source_refs"] = list(lineage_item.get("time_source_refs", []))
    merged["derived_time_hints"] = list(lineage_item.get("derived_time_hints", []))
    merged["cutoff_safe"] = bool(lineage_item.get("cutoff_safe"))
    return merged


def build_temporal_overlays(root: Path | str, lineage: list[dict[str, Any]] | None = None) -> dict[str, list[dict[str, Any]]]:
    root = Path(root)
    lineage = lineage or build_temporal_lineage(root)
    lookup = _lineage_lookup(lineage)

    outcomes = [
        _merge_temporal_fields(row, lookup[("outcome", row["packet_id"])])
        for row in read_jsonl(root / "data/eval/outcomes.jsonl")
        if row.get("packet_id") and ("outcome", row["packet_id"]) in lookup
    ]
    teacher = [
        _merge_temporal_fields(row, lookup[("manual_teacher_judgement", row["packet_id"])])
        for row in read_jsonl(root / "data/eval/manual_teacher_judgements.jsonl")
        if row.get("packet_id") and ("manual_teacher_judgement", row["packet_id"]) in lookup
    ]

    training_rows: list[dict[str, Any]] = []
    for row in read_jsonl(root / "data/eval/training_examples.jsonl"):
        example_id = row.get("example_id", "unknown_training_example")
        lineage_item = lookup.get(("training_example", example_id))
        if lineage_item:
            training_rows.append(_merge_temporal_fields(row, lineage_item))

    incidents: list[dict[str, Any]] = []
    for row in read_jsonl(root / "data/eval/historical_incidents.jsonl"):
        incident_id = row.get("incident_id", "unknown_historical_incident")
        lineage_item = lookup.get(("historical_incident", incident_id))
        if lineage_item:
            incidents.append(_merge_temporal_fields(row, lineage_item))

    return {
        "outcomes": outcomes,
        "manual_teacher_judgements": teacher,
        "training_examples": training_rows,
        "historical_incidents": incidents,
    }


def build_temporal_overlay_summary(overlays: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    datasets: dict[str, Any] = {}
    for name, rows in overlays.items():
        counts_by_quality: dict[str, int] = {}
        strict_eval_eligible_count = 0
        train_only_count = 0
        for row in rows:
            quality = row.get("timestamp_quality", "unknown")
            counts_by_quality[quality] = counts_by_quality.get(quality, 0) + 1
            if row.get("cutoff_safe") and quality in {"exact_window_time", "exact_time_inherited"}:
                strict_eval_eligible_count += 1
            else:
                train_only_count += 1
        datasets[name] = {
            "row_count": len(rows),
            "timestamp_quality_counts": counts_by_quality,
            "strict_eval_eligible_count": strict_eval_eligible_count,
            "train_only_count": train_only_count,
        }
    return {"datasets": datasets}


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _packet_group_tokens(packet: dict[str, Any]) -> set[str]:
    template = " ".join(item.get("template", "") for item in packet.get("logs", {}).get("top_templates", [])[:1])
    status = packet.get("traces", {}).get("status_message", "")
    tokens = set(re.findall(r"[a-zA-Z0-9]+", f"{template} {status}".lower()))
    return {token for token in tokens if token not in {"on", "the", "a", "an", "of"}}


def _episode_slug(service: str | None, operation: str | None) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", f"{service or 'unknown'}_{operation or 'unknown'}".lower()).strip("_")
    return normalized or "unknown"


def build_episode_index_from_records(
    packets: list[dict[str, Any]],
    incident_overlays: list[dict[str, Any]],
    heuristic_gap_minutes: int = 60,
) -> list[dict[str, Any]]:
    packet_by_id = {row["packet_id"]: row for row in packets if row.get("packet_id")}
    episodes: list[dict[str, Any]] = []
    covered_packet_ids: set[str] = set()

    for incident in incident_overlays:
        packet_ids = [packet_id for packet_id in incident.get("time_source_refs", []) if packet_id in packet_by_id]
        if not packet_ids:
            continue
        covered_packet_ids.update(packet_ids)
        episodes.append(
            {
                "episode_id": f"ep_{incident['incident_id']}",
                "incident_id": incident["incident_id"],
                "service": incident.get("service"),
                "operation": incident.get("operation"),
                "packet_ids": packet_ids,
                "episode_start_ts": incident.get("derived_ts_start"),
                "episode_end_ts": incident.get("derived_ts_end"),
                "episode_source": "historical_incident_source_packet_ids",
                "timestamp_quality": incident.get("timestamp_quality"),
            }
        )

    uncovered_packets = [packet for packet in packets if packet.get("packet_id") not in covered_packet_ids]
    uncovered_packets.sort(key=lambda item: (item.get("ts_start") or "", item.get("packet_id") or ""))
    cluster_counters: dict[str, int] = {}
    current_cluster: list[dict[str, Any]] = []

    def flush_cluster() -> None:
        nonlocal current_cluster
        if not current_cluster:
            return
        service = current_cluster[0].get("service")
        operation = current_cluster[0].get("operation")
        slug = _episode_slug(service, operation)
        cluster_counters[slug] = cluster_counters.get(slug, 0) + 1
        episodes.append(
            {
                "episode_id": f"ep_heuristic_{slug}_{cluster_counters[slug]:03d}",
                "incident_id": None,
                "service": service,
                "operation": operation,
                "packet_ids": [packet["packet_id"] for packet in current_cluster],
                "episode_start_ts": current_cluster[0].get("ts_start"),
                "episode_end_ts": current_cluster[-1].get("ts_end"),
                "episode_source": "heuristic_packet_cluster",
                "timestamp_quality": "exact_window_time",
            }
        )
        current_cluster = []

    for packet in uncovered_packets:
        if not current_cluster:
            current_cluster = [packet]
            continue
        previous = current_cluster[-1]
        same_service = packet.get("service") == previous.get("service")
        same_operation = packet.get("operation") == previous.get("operation")
        current_tokens = _packet_group_tokens(packet)
        previous_tokens = _packet_group_tokens(previous)
        token_overlap = len(current_tokens & previous_tokens)
        previous_end = _parse_ts(previous.get("ts_end"))
        current_start = _parse_ts(packet.get("ts_start"))
        gap_minutes = (
            (current_start - previous_end).total_seconds() / 60.0 if previous_end and current_start else heuristic_gap_minutes + 1
        )
        if same_service and same_operation and token_overlap >= 2 and gap_minutes <= heuristic_gap_minutes:
            current_cluster.append(packet)
        else:
            flush_cluster()
            current_cluster = [packet]
    flush_cluster()

    episodes.sort(key=lambda item: (item.get("episode_start_ts") or "", item["episode_id"]))
    return episodes


def build_episode_index(root: Path | str, overlays: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    root = Path(root)
    overlays = overlays or build_temporal_overlays(root)
    packet_rows = read_jsonl(root / "data/samples/incident-packets.jsonl")
    return build_episode_index_from_records(packet_rows, overlays.get("historical_incidents", []))


def _episode_metrics(decisions: list[dict[str, Any]], outcomes: list[dict[str, Any]], episodes: list[dict[str, Any]], top_k: int) -> dict[str, Any]:
    decisions_by_packet = {item["packet_id"]: item for item in decisions}
    outcomes_by_packet = {item["packet_id"]: item for item in outcomes if item.get("packet_id")}

    scored_episodes: list[dict[str, Any]] = []
    severe_episode_ids: set[str] = set()
    predicted_severe_episode_ids: set[str] = set()
    for episode in episodes:
        packet_ids = episode.get("packet_ids", [])
        actual_severe = any(outcomes_by_packet.get(packet_id, {}).get("actual_severe") for packet_id in packet_ids)
        predicted_severe = any(
            decisions_by_packet.get(packet_id, {}).get("final_priority") in {"P1", "P2"} for packet_id in packet_ids
        )
        episode_score = max(
            (decisions_by_packet.get(packet_id, {}).get("decision_score", 0.0) for packet_id in packet_ids),
            default=0.0,
        )
        if actual_severe:
            severe_episode_ids.add(episode["episode_id"])
        if predicted_severe:
            predicted_severe_episode_ids.add(episode["episode_id"])
        scored_episodes.append(
            {
                "episode_id": episode["episode_id"],
                "decision_score": round(episode_score, 4),
                "actual_severe": actual_severe,
                "predicted_severe": predicted_severe,
            }
        )

    severe_hits = severe_episode_ids & predicted_severe_episode_ids
    severe_episode_recall = len(severe_hits) / len(severe_episode_ids) if severe_episode_ids else 0.0
    top = sorted(scored_episodes, key=lambda item: item["decision_score"], reverse=True)[:top_k]
    top_k_episode_precision = sum(1 for item in top if item["actual_severe"]) / len(top) if top else 0.0
    missed = sorted(severe_episode_ids - predicted_severe_episode_ids)
    return {
        "episode_count": len(episodes),
        "severe_episode_recall": round(severe_episode_recall, 4),
        "top_k_episode_precision": round(top_k_episode_precision, 4),
        "missed_severe_episode_count": len(missed),
        "missed_severe_episode_ids": missed,
    }


def run_time_aware_historical_eval(root: Path | str) -> dict[str, Any]:
    root = Path(root)
    overlays = build_temporal_overlays(root)
    thresholds = read_yaml(root / "configs/thresholds.yaml")
    schemas = SchemaBundle(root / "schemas")
    top_k = thresholds["student"]["evaluation"]["top_k"]

    packets = read_jsonl(root / "data/samples/incident-packets.jsonl")
    packet_by_id = {packet["packet_id"]: packet for packet in packets if packet.get("packet_id")}
    outcomes = overlays["outcomes"]
    episodes = build_episode_index(root, overlays=overlays)
    strict_history_pool = [
        row
        for row in overlays["historical_incidents"]
        if row.get("cutoff_safe") and row.get("timestamp_quality") in {"exact_window_time", "exact_time_inherited"}
    ]

    all_decisions: list[dict[str, Any]] = []
    all_eval_outcomes: list[dict[str, Any]] = []
    folds: list[dict[str, Any]] = []

    for episode in episodes:
        episode_start_ts = episode.get("episode_start_ts")
        eval_packet_ids = set(episode.get("packet_ids", []))
        eval_packets = [packet_by_id[packet_id] for packet_id in episode.get("packet_ids", []) if packet_id in packet_by_id]

        training_rows = []
        unknown_time_train_rows = 0
        for row in overlays["training_examples"]:
            quality = row.get("timestamp_quality")
            row_packet_id = row.get("packet_id")
            if quality == "unknown_time":
                training_rows.append(row)
                unknown_time_train_rows += 1
                continue
            if not row.get("cutoff_safe"):
                continue
            if row_packet_id in eval_packet_ids:
                continue
            if row.get("derived_ts_end") and episode_start_ts and row["derived_ts_end"] < episode_start_ts:
                training_rows.append(row)

        strict_history = [
            row
            for row in strict_history_pool
            if row.get("derived_ts_end") and episode_start_ts and row["derived_ts_end"] < episode_start_ts
        ]
        relaxed_history = list(strict_history_pool)

        model, _ = train_student_model(training_rows, thresholds)
        strict_index = build_retrieval_index(strict_history)
        relaxed_index = build_retrieval_index(relaxed_history)
        strict_retrieval = {
            packet["packet_id"]: search_retrieval_index(packet, strict_index, top_k=top_k) for packet in eval_packets
        }
        recency_retrieval = {
            packet["packet_id"]: search_retrieval_index(
                packet,
                strict_index,
                top_k=top_k,
                reference_ts=packet.get("ts_start"),
                recency_half_life_minutes=60,
            )
            for packet in eval_packets
        }
        relaxed_retrieval = {
            packet["packet_id"]: search_retrieval_index(packet, relaxed_index, top_k=top_k) for packet in eval_packets
        }
        scores = predict_packets(model, eval_packets, strict_retrieval)
        decisions = build_triage_decisions(eval_packets, strict_retrieval, scores, [], thresholds, schemas)
        fold_outcomes = [row for row in outcomes if row.get("packet_id") in eval_packet_ids]

        for decision in decisions:
            all_decisions.append({**decision, "episode_id": episode["episode_id"]})
        all_eval_outcomes.extend(fold_outcomes)

        recency_delta = False
        for packet in eval_packets:
            packet_id = packet["packet_id"]
            strict_refs = strict_retrieval.get(packet_id, [])
            recency_refs = recency_retrieval.get(packet_id, [])
            if [item.get("incident_id") for item in strict_refs] != [item.get("incident_id") for item in recency_refs]:
                recency_delta = True
                break
            if [item.get("similarity_score") for item in strict_refs] != [item.get("similarity_score") for item in recency_refs]:
                recency_delta = True
                break

        folds.append(
            {
                "episode_id": episode["episode_id"],
                "eval_packet_ids": sorted(eval_packet_ids),
                "train_row_count": len(training_rows),
                "unknown_time_train_row_count": unknown_time_train_rows,
                "strict_history_incident_count": len(strict_history),
                "relaxed_history_incident_count": len(relaxed_history),
                "strict_retrieval_ref_count": sum(len(item) for item in strict_retrieval.values()),
                "recency_retrieval_ref_count": sum(len(item) for item in recency_retrieval.values()),
                "relaxed_retrieval_ref_count": sum(len(item) for item in relaxed_retrieval.values()),
                "recency_delta": recency_delta,
            }
        )

    packet_metrics = compute_eval_metrics(all_decisions, all_eval_outcomes, top_k=top_k)
    episode_metrics = _episode_metrics(all_decisions, all_eval_outcomes, episodes, top_k=top_k)
    cutoff_leakage_audit = {
        "folds_with_relaxed_history_gt_strict": sum(
            1 for fold in folds if fold["relaxed_history_incident_count"] > fold["strict_history_incident_count"]
        ),
        "folds_with_relaxed_refs_gt_strict": sum(
            1 for fold in folds if fold["relaxed_retrieval_ref_count"] > fold["strict_retrieval_ref_count"]
        ),
        "max_history_incident_gap": max(
            (fold["relaxed_history_incident_count"] - fold["strict_history_incident_count"] for fold in folds),
            default=0,
        ),
    }
    recency_compare = {
        "fold_count": len(folds),
        "strict_cutoff_fold_count": len(folds),
        "folds_with_recency_delta": sum(1 for fold in folds if fold["recency_delta"]),
    }
    return {
        "episode_count": len(episodes),
        "packet_count": len(all_decisions),
        "packet_metrics": packet_metrics,
        "episode_metrics": episode_metrics,
        "cutoff_leakage_audit": cutoff_leakage_audit,
        "recency_compare": recency_compare,
        "folds": folds,
    }


def _minutes_between(previous_ts: str | None, current_ts: str | None) -> float | None:
    previous = _parse_ts(previous_ts)
    current = _parse_ts(current_ts)
    if not previous or not current:
        return None
    return max((current - previous).total_seconds() / 60.0, 0.0)


def build_light_temporal_feature_map(packets: list[dict[str, Any]], lookback_minutes: int = 60) -> dict[str, dict[str, float]]:
    sorted_packets = sorted(packets, key=lambda item: (item.get("ts_start") or "", item.get("packet_id") or ""))
    prior_by_service: dict[str, list[dict[str, Any]]] = {}
    feature_map: dict[str, dict[str, float]] = {}

    for packet in sorted_packets:
        service = packet.get("service") or "unknown"
        history = prior_by_service.setdefault(service, [])
        current_start = packet.get("ts_start")
        recent_packets: list[dict[str, Any]] = []
        for prior in history:
            gap_minutes = _minutes_between(prior.get("ts_start"), current_start)
            if gap_minutes is not None and gap_minutes <= lookback_minutes:
                recent_packets.append(prior)

        previous_same_service = history[-1] if history else None
        gap_minutes = _minutes_between(previous_same_service.get("ts_start"), current_start) if previous_same_service else None
        feature_map[packet["packet_id"]] = {
            "same_service_recent_packet_count": min(len(recent_packets) / 5.0, 1.0),
            "same_service_recent_error_packet_count": min(
                sum(1 for prior in recent_packets if prior.get("metrics", {}).get("error_rate_delta", 0.0) >= 0.05) / 5.0,
                1.0,
            ),
            "same_service_prev_gap_inverse": 0.0
            if gap_minutes is None
            else max(0.0, min(1.0 - (gap_minutes / lookback_minutes), 1.0)),
        }
        history.append(packet)
    return feature_map


def _apply_temporal_features_to_training_rows(
    training_rows: list[dict[str, Any]],
    feature_map: dict[str, dict[str, float]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    packet_linked = 0
    legacy_zero_filled = 0
    enriched_rows: list[dict[str, Any]] = []
    for row in training_rows:
        packet_id = row.get("packet_id")
        features = dict(row.get("features", {}))
        temporal_features = feature_map.get(packet_id, {}) if packet_id else {}
        if packet_id and packet_id in feature_map:
            packet_linked += 1
        else:
            legacy_zero_filled += 1
        for name in TEMPORAL_FEATURE_NAMES:
            features[name] = temporal_features.get(name, 0.0)
        enriched_rows.append({**row, "features": features})
    return enriched_rows, {
        "packet_linked_training_count": packet_linked,
        "legacy_zero_filled_count": legacy_zero_filled,
    }


def build_temporal_feature_experiment(root: Path | str) -> dict[str, Any]:
    root = Path(root)
    overlays = build_temporal_overlays(root)
    thresholds = read_yaml(root / "configs/thresholds.yaml")
    schemas = SchemaBundle(root / "schemas")
    top_k = thresholds["student"]["evaluation"]["top_k"]
    packets = read_jsonl(root / "data/samples/incident-packets.jsonl")
    packet_by_id = {packet["packet_id"]: packet for packet in packets if packet.get("packet_id")}
    feature_map = build_light_temporal_feature_map(packets)
    outcomes = overlays["outcomes"]
    episodes = build_episode_index(root, overlays=overlays)
    strict_history_pool = [
        row
        for row in overlays["historical_incidents"]
        if row.get("cutoff_safe") and row.get("timestamp_quality") in {"exact_window_time", "exact_time_inherited"}
    ]

    baseline_decisions: list[dict[str, Any]] = []
    temporal_decisions: list[dict[str, Any]] = []
    eval_outcomes: list[dict[str, Any]] = []

    _, coverage = _apply_temporal_features_to_training_rows(overlays["training_examples"], feature_map)
    for episode in episodes:
        episode_start_ts = episode.get("episode_start_ts")
        eval_packet_ids = set(episode.get("packet_ids", []))
        eval_packets = [packet_by_id[packet_id] for packet_id in episode.get("packet_ids", []) if packet_id in packet_by_id]

        training_rows = []
        for row in overlays["training_examples"]:
            quality = row.get("timestamp_quality")
            row_packet_id = row.get("packet_id")
            if quality == "unknown_time":
                training_rows.append(row)
                continue
            if not row.get("cutoff_safe"):
                continue
            if row_packet_id in eval_packet_ids:
                continue
            if row.get("derived_ts_end") and episode_start_ts and row["derived_ts_end"] < episode_start_ts:
                training_rows.append(row)

        temporal_training_rows, _ = _apply_temporal_features_to_training_rows(training_rows, feature_map)

        strict_history = [
            row
            for row in strict_history_pool
            if row.get("derived_ts_end") and episode_start_ts and row["derived_ts_end"] < episode_start_ts
        ]
        strict_index = build_retrieval_index(strict_history)
        recency_retrieval = {
            packet["packet_id"]: search_retrieval_index(
                packet,
                strict_index,
                top_k=top_k,
                reference_ts=packet.get("ts_start"),
                recency_half_life_minutes=60,
            )
            for packet in eval_packets
        }

        baseline_model, _ = train_student_model(training_rows, thresholds)
        temporal_model, _ = train_student_model(temporal_training_rows, thresholds)
        baseline_scores = predict_packets(baseline_model, eval_packets, recency_retrieval)
        temporal_scores = predict_packets(temporal_model, eval_packets, recency_retrieval, temporal_context_by_packet=feature_map)

        baseline_fold_decisions = build_triage_decisions(eval_packets, recency_retrieval, baseline_scores, [], thresholds, schemas)
        temporal_fold_decisions = build_triage_decisions(eval_packets, recency_retrieval, temporal_scores, [], thresholds, schemas)
        fold_outcomes = [row for row in outcomes if row.get("packet_id") in eval_packet_ids]
        eval_outcomes.extend(fold_outcomes)
        baseline_decisions.extend(baseline_fold_decisions)
        temporal_decisions.extend(temporal_fold_decisions)

    return {
        "fold_count": len(episodes),
        "temporal_feature_names": TEMPORAL_FEATURE_NAMES,
        "temporal_feature_coverage": coverage,
        "baseline_packet_metrics": compute_eval_metrics(baseline_decisions, eval_outcomes, top_k=top_k),
        "temporal_packet_metrics": compute_eval_metrics(temporal_decisions, eval_outcomes, top_k=top_k),
    }


def _severity_label_from_supervision(judgement: dict[str, Any] | None, outcome: dict[str, Any] | None) -> str:
    if judgement:
        severity = judgement.get("severity", 0)
        if severity >= 4:
            return "severe"
        if severity >= 2:
            return "moderate"
        return "low"
    if outcome and outcome.get("actual_priority") in {"P1", "P2"}:
        return "severe"
    if outcome and outcome.get("actual_priority") == "P3":
        return "moderate"
    return "low"


def _action_from_supervision(judgement: dict[str, Any] | None, outcome: dict[str, Any] | None) -> str:
    if judgement and judgement.get("recommended_action"):
        return judgement["recommended_action"]
    priority = (outcome or {}).get("actual_priority")
    if priority in {"P1", "P2"}:
        return "page_owner"
    if priority == "P3":
        return "create_ticket"
    return "observe"


def _packet_prior_summary(packet: dict[str, Any], judgement: dict[str, Any] | None) -> str:
    parts: list[str] = []
    template = next(iter(packet.get("logs", {}).get("top_templates", [])), {}).get("template")
    status = packet.get("traces", {}).get("status_message")
    evidence = next(iter((judgement or {}).get("evidence", [])), None)
    for part in [template, status, evidence]:
        if part and part not in parts:
            parts.append(part)
    return " | ".join(parts)


def build_temporal_prior_catalog(
    root: Path | str,
    overlays: dict[str, list[dict[str, Any]]] | None = None,
    episodes: list[dict[str, Any]] | None = None,
    packets: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    root = Path(root)
    overlays = overlays or build_temporal_overlays(root)
    episodes = episodes or build_episode_index(root, overlays=overlays)
    packets = packets or read_jsonl(root / "data/samples/incident-packets.jsonl")

    outcome_by_packet = {row["packet_id"]: row for row in overlays["outcomes"] if row.get("packet_id")}
    judgement_by_packet = {
        row["packet_id"]: row for row in overlays["manual_teacher_judgements"] if row.get("packet_id")
    }
    episode_by_packet = {
        packet_id: episode
        for episode in episodes
        for packet_id in episode.get("packet_ids", [])
        if packet_id
    }

    priors: list[dict[str, Any]] = []
    for packet in sorted(packets, key=lambda item: (item.get("ts_start") or "", item.get("packet_id") or "")):
        packet_id = packet.get("packet_id")
        if not packet_id:
            continue
        outcome = outcome_by_packet.get(packet_id)
        judgement = judgement_by_packet.get(packet_id)
        if not outcome and not judgement:
            continue
        episode = episode_by_packet.get(packet_id, {})
        tags = list(
            dict.fromkeys(
                [
                    *(packet.get("anomaly_signals", []) or []),
                    packet.get("service") or "unknown_service",
                    packet.get("operation") or "unknown_operation",
                    episode.get("episode_source") or "unknown_episode_source",
                ]
            )
        )
        priors.append(
            {
                "prior_id": f"tprior_{packet_id}",
                "incident_id": f"tprior_{packet_id}",
                "source_packet_id": packet_id,
                "source_episode_id": episode.get("episode_id"),
                "service": packet.get("service"),
                "operation": packet.get("operation"),
                "summary": _packet_prior_summary(packet, judgement),
                "severity": _severity_label_from_supervision(judgement, outcome),
                "recommended_action": _action_from_supervision(judgement, outcome),
                "tags": tags,
                "derived_ts_start": packet.get("ts_start"),
                "derived_ts_end": packet.get("ts_end"),
                "time_granularity": "window",
                "timestamp_quality": "exact_time_inherited",
                "time_source": "packet_linked_reviewed_supervision",
                "time_source_refs": [packet_id],
                "cutoff_safe": True,
            }
        )
    return priors


def build_temporal_prior_summary(priors: list[dict[str, Any]]) -> dict[str, Any]:
    service_counts: dict[str, int] = {}
    severity_counts: dict[str, int] = {}
    action_counts: dict[str, int] = {}
    starts: list[str] = []
    ends: list[str] = []

    for prior in priors:
        service = prior.get("service") or "unknown_service"
        severity = prior.get("severity") or "unknown"
        action = prior.get("recommended_action") or "unknown"
        service_counts[service] = service_counts.get(service, 0) + 1
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        action_counts[action] = action_counts.get(action, 0) + 1
        if prior.get("derived_ts_start"):
            starts.append(prior["derived_ts_start"])
        if prior.get("derived_ts_end"):
            ends.append(prior["derived_ts_end"])

    return {
        "packet_linked_prior_count": len(priors),
        "service_counts": service_counts,
        "severity_counts": severity_counts,
        "recommended_action_counts": action_counts,
        "exact_time_range": {
            "earliest": min(starts) if starts else None,
            "latest": max(ends) if ends else None,
        },
    }


def _severity_rank_label(value: str | None) -> int:
    return {"severe": 3, "moderate": 2, "low": 1}.get(value or "", 0)


def _action_rank(value: str | None) -> int:
    return {"page_owner": 3, "create_ticket": 2, "observe": 1}.get(value or "", 0)


def build_episode_context_priors(priors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in priors:
        key = row.get("source_episode_id") or row.get("source_packet_id") or row.get("prior_id") or row.get("incident_id")
        grouped.setdefault(key, []).append(row)

    synthesized: list[dict[str, Any]] = []
    for key, rows in sorted(grouped.items()):
        representative = max(rows, key=_prior_rank)
        fragments: list[str] = []
        for row in sorted(rows, key=_prior_rank, reverse=True):
            for fragment in [part.strip() for part in (row.get("summary") or "").split("|") if part.strip()]:
                if fragment not in fragments:
                    fragments.append(fragment)
        summary_parts = [*fragments[:4], f"episode_packets={len(rows)}"]
        synthesized.append(
            {
                **representative,
                "prior_id": f"tectx_{key}",
                "incident_id": f"tectx_{key}",
                "source_packet_id": None,
                "source_packet_ids": [row.get("source_packet_id") for row in rows if row.get("source_packet_id")],
                "packet_count": len(rows),
                "summary": " | ".join(summary_parts),
                "severity": max((row.get("severity") for row in rows), key=_severity_rank_label),
                "recommended_action": max((row.get("recommended_action") for row in rows), key=_action_rank),
                "derived_ts_start": min((row.get("derived_ts_start") for row in rows if row.get("derived_ts_start")), default=None),
                "derived_ts_end": max((row.get("derived_ts_end") for row in rows if row.get("derived_ts_end")), default=None),
                "tags": list(
                    dict.fromkeys(
                        [tag for row in rows for tag in (row.get("tags", []) or [])] + ["episode_context_synthesized"]
                    )
                ),
                "time_source": "episode_context_prior_synthesis",
                "time_source_refs": [row.get("source_packet_id") for row in rows if row.get("source_packet_id")],
            }
        )
    return synthesized


def build_temporal_prior_probe(root: Path | str) -> dict[str, Any]:
    root = Path(root)
    overlays = build_temporal_overlays(root)
    thresholds = read_yaml(root / "configs/thresholds.yaml")
    schemas = SchemaBundle(root / "schemas")
    top_k = thresholds["student"]["evaluation"]["top_k"]
    packets = read_jsonl(root / "data/samples/incident-packets.jsonl")
    packet_by_id = {packet["packet_id"]: packet for packet in packets if packet.get("packet_id")}
    outcomes = overlays["outcomes"]
    episodes = build_episode_index(root, overlays=overlays)
    baseline_history_pool = [
        row
        for row in overlays["historical_incidents"]
        if row.get("cutoff_safe") and row.get("timestamp_quality") in {"exact_window_time", "exact_time_inherited"}
    ]
    packet_prior_pool = build_temporal_prior_catalog(root, overlays=overlays, episodes=episodes, packets=packets)

    baseline_decisions: list[dict[str, Any]] = []
    expanded_decisions: list[dict[str, Any]] = []
    eval_outcomes: list[dict[str, Any]] = []
    folds: list[dict[str, Any]] = []

    for episode in episodes:
        episode_id = episode["episode_id"]
        episode_start_ts = episode.get("episode_start_ts")
        eval_packet_ids = set(episode.get("packet_ids", []))
        eval_packets = [packet_by_id[packet_id] for packet_id in episode.get("packet_ids", []) if packet_id in packet_by_id]

        training_rows = []
        for row in overlays["training_examples"]:
            quality = row.get("timestamp_quality")
            row_packet_id = row.get("packet_id")
            if quality == "unknown_time":
                training_rows.append(row)
                continue
            if not row.get("cutoff_safe"):
                continue
            if row_packet_id in eval_packet_ids:
                continue
            if row.get("derived_ts_end") and episode_start_ts and row["derived_ts_end"] < episode_start_ts:
                training_rows.append(row)

        baseline_history = [
            row
            for row in baseline_history_pool
            if row.get("derived_ts_end") and episode_start_ts and row["derived_ts_end"] < episode_start_ts
        ]
        expanded_packet_priors = [
            row
            for row in packet_prior_pool
            if row.get("derived_ts_end")
            and episode_start_ts
            and row["derived_ts_end"] < episode_start_ts
            and row.get("source_episode_id") != episode_id
            and row.get("source_packet_id") not in eval_packet_ids
        ]
        expanded_history = [*baseline_history, *expanded_packet_priors]

        model, _ = train_student_model(training_rows, thresholds)
        baseline_index = build_retrieval_index(baseline_history)
        expanded_index = build_retrieval_index(expanded_history)
        baseline_retrieval = {
            packet["packet_id"]: search_retrieval_index(
                packet,
                baseline_index,
                top_k=top_k,
                reference_ts=packet.get("ts_start"),
                recency_half_life_minutes=60,
            )
            for packet in eval_packets
        }
        expanded_retrieval = {
            packet["packet_id"]: search_retrieval_index(
                packet,
                expanded_index,
                top_k=top_k,
                reference_ts=packet.get("ts_start"),
                recency_half_life_minutes=60,
            )
            for packet in eval_packets
        }
        baseline_scores = predict_packets(model, eval_packets, baseline_retrieval)
        expanded_scores = predict_packets(model, eval_packets, expanded_retrieval)
        baseline_fold_decisions = build_triage_decisions(eval_packets, baseline_retrieval, baseline_scores, [], thresholds, schemas)
        expanded_fold_decisions = build_triage_decisions(eval_packets, expanded_retrieval, expanded_scores, [], thresholds, schemas)
        fold_outcomes = [row for row in outcomes if row.get("packet_id") in eval_packet_ids]

        eval_outcomes.extend(fold_outcomes)
        baseline_decisions.extend(baseline_fold_decisions)
        expanded_decisions.extend(expanded_fold_decisions)

        top_hit_delta = False
        for packet in eval_packets:
            packet_id = packet["packet_id"]
            baseline_refs = baseline_retrieval.get(packet_id, [])
            expanded_refs = expanded_retrieval.get(packet_id, [])
            if [item.get("incident_id") for item in baseline_refs] != [item.get("incident_id") for item in expanded_refs]:
                top_hit_delta = True
                break
            if [item.get("similarity_score") for item in baseline_refs] != [item.get("similarity_score") for item in expanded_refs]:
                top_hit_delta = True
                break

        folds.append(
            {
                "episode_id": episode_id,
                "eval_packet_ids": sorted(eval_packet_ids),
                "baseline_history_doc_count": len(baseline_history),
                "expanded_packet_prior_doc_count": len(expanded_packet_priors),
                "expanded_history_doc_count": len(expanded_history),
                "baseline_retrieval_ref_count": sum(len(item) for item in baseline_retrieval.values()),
                "expanded_retrieval_ref_count": sum(len(item) for item in expanded_retrieval.values()),
                "top_hit_delta": top_hit_delta,
            }
        )

    return {
        "baseline_history_doc_count": len(baseline_history_pool),
        "expanded_packet_prior_count": len(packet_prior_pool),
        "expanded_total_doc_count": len(baseline_history_pool) + len(packet_prior_pool),
        "fold_count": len(episodes),
        "prior_summary": build_temporal_prior_summary(packet_prior_pool),
        "compare": {
            "folds_with_expanded_history_gt_baseline": sum(
                1 for fold in folds if fold["expanded_history_doc_count"] > fold["baseline_history_doc_count"]
            ),
            "folds_with_expanded_refs_gt_baseline": sum(
                1 for fold in folds if fold["expanded_retrieval_ref_count"] > fold["baseline_retrieval_ref_count"]
            ),
            "folds_with_top_hit_delta": sum(1 for fold in folds if fold["top_hit_delta"]),
            "max_added_history_docs": max(
                (fold["expanded_history_doc_count"] - fold["baseline_history_doc_count"] for fold in folds),
                default=0,
            ),
        },
        "baseline_packet_metrics": compute_eval_metrics(baseline_decisions, eval_outcomes, top_k=top_k),
        "expanded_packet_metrics": compute_eval_metrics(expanded_decisions, eval_outcomes, top_k=top_k),
        "baseline_episode_metrics": _episode_metrics(baseline_decisions, eval_outcomes, episodes, top_k=top_k),
        "expanded_episode_metrics": _episode_metrics(expanded_decisions, eval_outcomes, episodes, top_k=top_k),
        "folds": folds,
    }


def _admissible_history_rows(
    rows: list[dict[str, Any]],
    episode_start_ts: str | None,
    eval_packet_ids: set[str],
    eval_episode_id: str | None,
    inclusive: bool,
) -> tuple[list[dict[str, Any]], int, int]:
    cutoff = _parse_ts(episode_start_ts)
    if not cutoff:
        return [], 0, 0

    admitted: list[dict[str, Any]] = []
    equality_admitted_count = 0
    anti_leakage_violation_count = 0
    for row in rows:
        row_end = _parse_ts(row.get("derived_ts_end"))
        row_start = _parse_ts(row.get("derived_ts_start"))
        if not row_end:
            continue
        if row_end < cutoff:
            pass
        elif inclusive and row_end == cutoff:
            equality_admitted_count += 1
        else:
            continue

        if row.get("source_episode_id") == eval_episode_id:
            anti_leakage_violation_count += 1
            continue
        if row.get("source_packet_id") in eval_packet_ids:
            anti_leakage_violation_count += 1
            continue
        if row_start and row_start >= cutoff:
            anti_leakage_violation_count += 1
            continue
        admitted.append(row)
    return admitted, equality_admitted_count, anti_leakage_violation_count


def _prior_rank(row: dict[str, Any]) -> tuple[Any, ...]:
    severity_rank = {"severe": 3, "moderate": 2, "low": 1}.get(row.get("severity"), 0)
    return (
        row.get("derived_ts_end") or "",
        severity_rank,
        len(row.get("tags", []) or []),
        len(row.get("summary", "") or ""),
    )


def _compact_boundary_safe_priors(priors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in priors:
        key = row.get("source_episode_id") or row.get("source_packet_id") or row.get("prior_id") or row.get("incident_id")
        grouped.setdefault(key, []).append(row)

    compacted: list[dict[str, Any]] = []
    for key, rows in sorted(grouped.items()):
        representative = max(rows, key=_prior_rank)
        compacted.append(
            {
                **representative,
                "prior_id": f"tproto_{key}",
                "incident_id": f"tproto_{key}",
                "source_packet_ids": [row.get("source_packet_id") for row in rows if row.get("source_packet_id")],
                "tags": list(dict.fromkeys([*(representative.get("tags", []) or []), "prototype_compacted"])),
            }
        )
    return compacted


def build_temporal_boundary_safe_probe(root: Path | str) -> dict[str, Any]:
    root = Path(root)
    overlays = build_temporal_overlays(root)
    thresholds = read_yaml(root / "configs/thresholds.yaml")
    schemas = SchemaBundle(root / "schemas")
    top_k = thresholds["student"]["evaluation"]["top_k"]
    packets = read_jsonl(root / "data/samples/incident-packets.jsonl")
    packet_by_id = {packet["packet_id"]: packet for packet in packets if packet.get("packet_id")}
    outcomes = overlays["outcomes"]
    episodes = build_episode_index(root, overlays=overlays)
    incident_pool = [
        row
        for row in overlays["historical_incidents"]
        if row.get("cutoff_safe") and row.get("timestamp_quality") in {"exact_window_time", "exact_time_inherited"}
    ]
    raw_prior_pool = build_temporal_prior_catalog(root, overlays=overlays, episodes=episodes, packets=packets)

    strict_decisions: list[dict[str, Any]] = []
    boundary_safe_decisions: list[dict[str, Any]] = []
    prototype_decisions: list[dict[str, Any]] = []
    eval_outcomes: list[dict[str, Any]] = []
    folds: list[dict[str, Any]] = []

    for episode in episodes:
        episode_id = episode["episode_id"]
        episode_start_ts = episode.get("episode_start_ts")
        eval_packet_ids = set(episode.get("packet_ids", []))
        eval_packets = [packet_by_id[packet_id] for packet_id in episode.get("packet_ids", []) if packet_id in packet_by_id]

        training_rows = []
        for row in overlays["training_examples"]:
            quality = row.get("timestamp_quality")
            row_packet_id = row.get("packet_id")
            if quality == "unknown_time":
                training_rows.append(row)
                continue
            if not row.get("cutoff_safe"):
                continue
            if row_packet_id in eval_packet_ids:
                continue
            if row.get("derived_ts_end") and episode_start_ts and row["derived_ts_end"] < episode_start_ts:
                training_rows.append(row)

        strict_incidents, _, strict_incident_violations = _admissible_history_rows(
            incident_pool,
            episode_start_ts,
            eval_packet_ids,
            episode_id,
            inclusive=False,
        )
        strict_priors, _, strict_prior_violations = _admissible_history_rows(
            raw_prior_pool,
            episode_start_ts,
            eval_packet_ids,
            episode_id,
            inclusive=False,
        )
        boundary_incidents, boundary_incident_equal, boundary_incident_violations = _admissible_history_rows(
            incident_pool,
            episode_start_ts,
            eval_packet_ids,
            episode_id,
            inclusive=True,
        )
        boundary_priors, boundary_prior_equal, boundary_prior_violations = _admissible_history_rows(
            raw_prior_pool,
            episode_start_ts,
            eval_packet_ids,
            episode_id,
            inclusive=True,
        )
        compacted_priors = _compact_boundary_safe_priors(boundary_priors)

        strict_history = [*strict_incidents, *strict_priors]
        boundary_history = [*boundary_incidents, *boundary_priors]
        prototype_history = [*boundary_incidents, *compacted_priors]

        model, _ = train_student_model(training_rows, thresholds)
        strict_index = build_retrieval_index(strict_history)
        boundary_index = build_retrieval_index(boundary_history)
        prototype_index = build_retrieval_index(prototype_history)

        strict_retrieval = {
            packet["packet_id"]: search_retrieval_index(
                packet,
                strict_index,
                top_k=top_k,
                reference_ts=packet.get("ts_start"),
                recency_half_life_minutes=60,
            )
            for packet in eval_packets
        }
        boundary_retrieval = {
            packet["packet_id"]: search_retrieval_index(
                packet,
                boundary_index,
                top_k=top_k,
                reference_ts=packet.get("ts_start"),
                recency_half_life_minutes=60,
            )
            for packet in eval_packets
        }
        prototype_retrieval = {
            packet["packet_id"]: search_retrieval_index(
                packet,
                prototype_index,
                top_k=top_k,
                reference_ts=packet.get("ts_start"),
                recency_half_life_minutes=60,
            )
            for packet in eval_packets
        }

        strict_scores = predict_packets(model, eval_packets, strict_retrieval)
        boundary_scores = predict_packets(model, eval_packets, boundary_retrieval)
        prototype_scores = predict_packets(model, eval_packets, prototype_retrieval)

        strict_fold_decisions = build_triage_decisions(eval_packets, strict_retrieval, strict_scores, [], thresholds, schemas)
        boundary_fold_decisions = build_triage_decisions(eval_packets, boundary_retrieval, boundary_scores, [], thresholds, schemas)
        prototype_fold_decisions = build_triage_decisions(eval_packets, prototype_retrieval, prototype_scores, [], thresholds, schemas)
        fold_outcomes = [row for row in outcomes if row.get("packet_id") in eval_packet_ids]
        eval_outcomes.extend(fold_outcomes)
        strict_decisions.extend(strict_fold_decisions)
        boundary_safe_decisions.extend(boundary_fold_decisions)
        prototype_decisions.extend(prototype_fold_decisions)

        top_hit_overlap_count = 0
        for packet in eval_packets:
            packet_id = packet["packet_id"]
            boundary_top = next(iter(boundary_retrieval.get(packet_id, [])), None)
            prototype_top = next(iter(prototype_retrieval.get(packet_id, [])), None)
            boundary_key = (boundary_top or {}).get("source_episode_id") or (boundary_top or {}).get("incident_id")
            prototype_key = (prototype_top or {}).get("source_episode_id") or (prototype_top or {}).get("incident_id")
            if boundary_key and prototype_key and boundary_key == prototype_key:
                top_hit_overlap_count += 1

        folds.append(
            {
                "episode_id": episode_id,
                "eval_packet_ids": sorted(eval_packet_ids),
                "strict_history_doc_count": len(strict_history),
                "boundary_safe_history_doc_count": len(boundary_history),
                "equality_admitted_doc_count": boundary_incident_equal + boundary_prior_equal,
                "anti_leakage_violation_count": boundary_incident_violations + boundary_prior_violations,
                "boundary_safe_packet_prior_doc_count": len(boundary_priors),
                "compacted_packet_prior_doc_count": len(compacted_priors),
                "boundary_safe_retrieval_ref_count": sum(len(item) for item in boundary_retrieval.values()),
                "prototype_retrieval_ref_count": sum(len(item) for item in prototype_retrieval.values()),
                "prototype_top_hit_overlap": top_hit_overlap_count > 0,
                "prototype_top_hit_overlap_count": top_hit_overlap_count,
                "strict_history_anti_leakage_violation_count": strict_incident_violations + strict_prior_violations,
            }
        )

    return {
        "fold_count": len(episodes),
        "strict_compare": {
            "fold_count": len(episodes),
            "folds_with_boundary_safe_history_gt_strict": sum(
                1 for fold in folds if fold["boundary_safe_history_doc_count"] > fold["strict_history_doc_count"]
            ),
            "folds_with_equality_admitted_docs": sum(1 for fold in folds if fold["equality_admitted_doc_count"] > 0),
            "equality_admitted_doc_count": sum(fold["equality_admitted_doc_count"] for fold in folds),
            "anti_leakage_violation_count": sum(fold["anti_leakage_violation_count"] for fold in folds),
        },
        "prototype_compare": {
            "folds_with_compacted_doc_count_lt_boundary_safe": sum(
                1
                for fold in folds
                if fold["compacted_packet_prior_doc_count"] < fold["boundary_safe_packet_prior_doc_count"]
            ),
            "folds_with_top_hit_overlap": sum(1 for fold in folds if fold["prototype_top_hit_overlap"]),
            "max_docs_removed_by_compaction": max(
                (
                    fold["boundary_safe_packet_prior_doc_count"] - fold["compacted_packet_prior_doc_count"]
                    for fold in folds
                ),
                default=0,
            ),
        },
        "strict_packet_metrics": compute_eval_metrics(strict_decisions, eval_outcomes, top_k=top_k),
        "boundary_safe_packet_metrics": compute_eval_metrics(boundary_safe_decisions, eval_outcomes, top_k=top_k),
        "prototype_packet_metrics": compute_eval_metrics(prototype_decisions, eval_outcomes, top_k=top_k),
        "strict_episode_metrics": _episode_metrics(strict_decisions, eval_outcomes, episodes, top_k=top_k),
        "boundary_safe_episode_metrics": _episode_metrics(boundary_safe_decisions, eval_outcomes, episodes, top_k=top_k),
        "prototype_episode_metrics": _episode_metrics(prototype_decisions, eval_outcomes, episodes, top_k=top_k),
        "folds": folds,
    }


def _retrieval_group_key(item: dict[str, Any]) -> str:
    return (
        item.get("source_episode_id")
        or item.get("incident_id")
        or item.get("source_packet_id")
        or item.get("summary")
        or "unknown_retrieval_group"
    )


def _merge_hybrid_retrieval(
    raw_refs: list[dict[str, Any]],
    context_refs: list[dict[str, Any]],
    top_k: int,
    agreement_bonus: float = 0.05,
) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}

    def observe(ref: dict[str, Any], lane: str) -> None:
        key = _retrieval_group_key(ref)
        entry = grouped.setdefault(
            key,
            {
                "best_ref": None,
                "best_score": -1.0,
                "raw_score": None,
                "context_score": None,
                "source_episode_id": ref.get("source_episode_id"),
                "source_packet_id": ref.get("source_packet_id"),
            },
        )
        score = ref.get("similarity_score", 0.0)
        lane_key = f"{lane}_score"
        if entry[lane_key] is None or score > entry[lane_key]:
            entry[lane_key] = score
        if entry["best_ref"] is None or score > entry["best_score"]:
            entry["best_ref"] = dict(ref)
            entry["best_score"] = score
        if ref.get("source_episode_id"):
            entry["source_episode_id"] = ref.get("source_episode_id")
        if ref.get("source_packet_id"):
            entry["source_packet_id"] = ref.get("source_packet_id")

    for ref in raw_refs:
        observe(ref, "raw")
    for ref in context_refs:
        observe(ref, "context")

    merged: list[dict[str, Any]] = []
    for entry in grouped.values():
        raw_score = entry.get("raw_score")
        context_score = entry.get("context_score")
        fused = max(raw_score or 0.0, context_score or 0.0)
        bonus = agreement_bonus if entry.get("source_episode_id") and raw_score is not None and context_score is not None else 0.0
        best_ref = dict(entry["best_ref"] or {})
        best_ref["similarity_score"] = round(fused + bonus, 4)
        best_ref["agreement_bonus"] = round(bonus, 4)
        best_ref["raw_similarity_score"] = round(raw_score or 0.0, 4)
        best_ref["context_similarity_score"] = round(context_score or 0.0, 4)
        best_ref["lane_sources"] = sorted(
            lane
            for lane, value in [("raw", raw_score), ("context", context_score)]
            if value is not None
        )
        merged.append(best_ref)

    return sorted(merged, key=lambda item: item.get("similarity_score", 0.0), reverse=True)[:top_k]


def build_temporal_episode_context_probe(root: Path | str) -> dict[str, Any]:
    root = Path(root)
    overlays = build_temporal_overlays(root)
    thresholds = read_yaml(root / "configs/thresholds.yaml")
    schemas = SchemaBundle(root / "schemas")
    top_k = thresholds["student"]["evaluation"]["top_k"]
    packets = read_jsonl(root / "data/samples/incident-packets.jsonl")
    packet_by_id = {packet["packet_id"]: packet for packet in packets if packet.get("packet_id")}
    outcomes = overlays["outcomes"]
    episodes = build_episode_index(root, overlays=overlays)
    incident_pool = [
        row
        for row in overlays["historical_incidents"]
        if row.get("cutoff_safe") and row.get("timestamp_quality") in {"exact_window_time", "exact_time_inherited"}
    ]
    raw_prior_pool = build_temporal_prior_catalog(root, overlays=overlays, episodes=episodes, packets=packets)
    all_context_priors = build_episode_context_priors(raw_prior_pool)

    boundary_safe_decisions: list[dict[str, Any]] = []
    episode_context_decisions: list[dict[str, Any]] = []
    eval_outcomes: list[dict[str, Any]] = []
    folds: list[dict[str, Any]] = []

    for episode in episodes:
        episode_id = episode["episode_id"]
        episode_start_ts = episode.get("episode_start_ts")
        eval_packet_ids = set(episode.get("packet_ids", []))
        eval_packets = [packet_by_id[packet_id] for packet_id in episode.get("packet_ids", []) if packet_id in packet_by_id]

        training_rows = []
        for row in overlays["training_examples"]:
            quality = row.get("timestamp_quality")
            row_packet_id = row.get("packet_id")
            if quality == "unknown_time":
                training_rows.append(row)
                continue
            if not row.get("cutoff_safe"):
                continue
            if row_packet_id in eval_packet_ids:
                continue
            if row.get("derived_ts_end") and episode_start_ts and row["derived_ts_end"] < episode_start_ts:
                training_rows.append(row)

        boundary_incidents, _, boundary_incident_violations = _admissible_history_rows(
            incident_pool,
            episode_start_ts,
            eval_packet_ids,
            episode_id,
            inclusive=True,
        )
        boundary_priors, _, boundary_prior_violations = _admissible_history_rows(
            raw_prior_pool,
            episode_start_ts,
            eval_packet_ids,
            episode_id,
            inclusive=True,
        )
        episode_context_priors = build_episode_context_priors(boundary_priors)
        context_violations = 0

        boundary_history = [*boundary_incidents, *boundary_priors]
        episode_context_history = [*boundary_incidents, *episode_context_priors]

        model, _ = train_student_model(training_rows, thresholds)
        boundary_index = build_retrieval_index(boundary_history)
        context_index = build_retrieval_index(episode_context_history)
        boundary_retrieval = {
            packet["packet_id"]: search_retrieval_index(
                packet,
                boundary_index,
                top_k=top_k,
                reference_ts=packet.get("ts_start"),
                recency_half_life_minutes=60,
            )
            for packet in eval_packets
        }
        context_retrieval = {
            packet["packet_id"]: search_retrieval_index(
                packet,
                context_index,
                top_k=top_k,
                reference_ts=packet.get("ts_start"),
                recency_half_life_minutes=60,
            )
            for packet in eval_packets
        }
        boundary_scores = predict_packets(model, eval_packets, boundary_retrieval)
        context_scores = predict_packets(model, eval_packets, context_retrieval)
        boundary_fold_decisions = build_triage_decisions(eval_packets, boundary_retrieval, boundary_scores, [], thresholds, schemas)
        context_fold_decisions = build_triage_decisions(eval_packets, context_retrieval, context_scores, [], thresholds, schemas)
        fold_outcomes = [row for row in outcomes if row.get("packet_id") in eval_packet_ids]
        eval_outcomes.extend(fold_outcomes)
        boundary_safe_decisions.extend(boundary_fold_decisions)
        episode_context_decisions.extend(context_fold_decisions)

        top_hit_overlap_count = 0
        for packet in eval_packets:
            packet_id = packet["packet_id"]
            boundary_top = next(iter(boundary_retrieval.get(packet_id, [])), None)
            context_top = next(iter(context_retrieval.get(packet_id, [])), None)
            boundary_key = (boundary_top or {}).get("source_episode_id") or (boundary_top or {}).get("incident_id")
            context_key = (context_top or {}).get("source_episode_id") or (context_top or {}).get("incident_id")
            if boundary_key and context_key and boundary_key == context_key:
                top_hit_overlap_count += 1

        folds.append(
            {
                "episode_id": episode_id,
                "eval_packet_ids": sorted(eval_packet_ids),
                "boundary_safe_packet_prior_doc_count": len(boundary_priors),
                "episode_context_prior_doc_count": len(episode_context_priors),
                "boundary_safe_history_doc_count": len(boundary_history),
                "episode_context_history_doc_count": len(episode_context_history),
                "boundary_safe_retrieval_ref_count": sum(len(item) for item in boundary_retrieval.values()),
                "episode_context_retrieval_ref_count": sum(len(item) for item in context_retrieval.values()),
                "anti_leakage_violation_count": boundary_incident_violations + boundary_prior_violations + context_violations,
                "top_hit_overlap": top_hit_overlap_count > 0,
                "top_hit_overlap_count": top_hit_overlap_count,
            }
        )

    return {
        "episode_context_prior_count": len(all_context_priors),
        "fold_count": len(episodes),
        "episode_context_prior_summary": build_temporal_prior_summary(all_context_priors),
        "compare": {
            "folds_with_episode_context_doc_count_lt_boundary_safe": sum(
                1
                for fold in folds
                if fold["episode_context_prior_doc_count"] < fold["boundary_safe_packet_prior_doc_count"]
            ),
            "folds_with_top_hit_overlap": sum(1 for fold in folds if fold["top_hit_overlap"]),
            "max_docs_removed_by_episode_context": max(
                (
                    fold["boundary_safe_packet_prior_doc_count"] - fold["episode_context_prior_doc_count"]
                    for fold in folds
                ),
                default=0,
            ),
            "anti_leakage_violation_count": sum(fold["anti_leakage_violation_count"] for fold in folds),
        },
        "boundary_safe_packet_metrics": compute_eval_metrics(boundary_safe_decisions, eval_outcomes, top_k=top_k),
        "episode_context_packet_metrics": compute_eval_metrics(episode_context_decisions, eval_outcomes, top_k=top_k),
        "boundary_safe_episode_metrics": _episode_metrics(boundary_safe_decisions, eval_outcomes, episodes, top_k=top_k),
        "episode_context_episode_metrics": _episode_metrics(episode_context_decisions, eval_outcomes, episodes, top_k=top_k),
        "folds": folds,
    }


def render_temporal_episode_context_probe_markdown(result: dict[str, Any]) -> str:
    lines = ["# Temporal Episode-context Probe", "", "## Summary"]
    lines.append(f"- episode-context prior count: `{result['episode_context_prior_count']}`")
    lines.append(f"- fold count: `{result['fold_count']}`")
    lines.append(f"- episode-context prior summary: `{result['episode_context_prior_summary']}`")
    lines.extend(["", "## Compare"])
    for key, value in result.get("compare", {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Boundary-safe Packet Metrics"])
    for key, value in result.get("boundary_safe_packet_metrics", {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Episode-context Packet Metrics"])
    for key, value in result.get("episode_context_packet_metrics", {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Folds"])
    for fold in result.get("folds", []):
        lines.append(
            f"- `{fold['episode_id']}` packets={fold['eval_packet_ids']} raw_priors={fold['boundary_safe_packet_prior_doc_count']} episode_context_priors={fold['episode_context_prior_doc_count']} boundary_safe_history={fold['boundary_safe_history_doc_count']} episode_context_history={fold['episode_context_history_doc_count']} overlap={fold['top_hit_overlap']} leakage_violations={fold['anti_leakage_violation_count']}"
        )
    return "\n".join(lines) + "\n"


def build_temporal_hybrid_context_probe(root: Path | str) -> dict[str, Any]:
    root = Path(root)
    overlays = build_temporal_overlays(root)
    thresholds = read_yaml(root / "configs/thresholds.yaml")
    schemas = SchemaBundle(root / "schemas")
    top_k = thresholds["student"]["evaluation"]["top_k"]
    candidate_limit = max(top_k * 2, top_k)
    packets = read_jsonl(root / "data/samples/incident-packets.jsonl")
    packet_by_id = {packet["packet_id"]: packet for packet in packets if packet.get("packet_id")}
    outcomes = overlays["outcomes"]
    episodes = build_episode_index(root, overlays=overlays)
    incident_pool = [
        row
        for row in overlays["historical_incidents"]
        if row.get("cutoff_safe") and row.get("timestamp_quality") in {"exact_window_time", "exact_time_inherited"}
    ]
    raw_prior_pool = build_temporal_prior_catalog(root, overlays=overlays, episodes=episodes, packets=packets)
    all_context_priors = build_episode_context_priors(raw_prior_pool)

    raw_decisions: list[dict[str, Any]] = []
    hybrid_decisions: list[dict[str, Any]] = []
    eval_outcomes: list[dict[str, Any]] = []
    folds: list[dict[str, Any]] = []

    for episode in episodes:
        episode_id = episode["episode_id"]
        episode_start_ts = episode.get("episode_start_ts")
        eval_packet_ids = set(episode.get("packet_ids", []))
        eval_packets = [packet_by_id[packet_id] for packet_id in episode.get("packet_ids", []) if packet_id in packet_by_id]

        training_rows = []
        for row in overlays["training_examples"]:
            quality = row.get("timestamp_quality")
            row_packet_id = row.get("packet_id")
            if quality == "unknown_time":
                training_rows.append(row)
                continue
            if not row.get("cutoff_safe"):
                continue
            if row_packet_id in eval_packet_ids:
                continue
            if row.get("derived_ts_end") and episode_start_ts and row["derived_ts_end"] < episode_start_ts:
                training_rows.append(row)

        boundary_incidents, _, boundary_incident_violations = _admissible_history_rows(
            incident_pool,
            episode_start_ts,
            eval_packet_ids,
            episode_id,
            inclusive=True,
        )
        boundary_priors, _, boundary_prior_violations = _admissible_history_rows(
            raw_prior_pool,
            episode_start_ts,
            eval_packet_ids,
            episode_id,
            inclusive=True,
        )
        context_priors = build_episode_context_priors(boundary_priors)

        raw_history = [*boundary_incidents, *boundary_priors]
        context_history = [*boundary_incidents, *context_priors]

        model, _ = train_student_model(training_rows, thresholds)
        raw_index = build_retrieval_index(raw_history)
        context_index = build_retrieval_index(context_history)
        raw_candidates = {
            packet["packet_id"]: search_retrieval_index(
                packet,
                raw_index,
                top_k=candidate_limit,
                reference_ts=packet.get("ts_start"),
                recency_half_life_minutes=60,
            )
            for packet in eval_packets
        }
        context_candidates = {
            packet["packet_id"]: search_retrieval_index(
                packet,
                context_index,
                top_k=candidate_limit,
                reference_ts=packet.get("ts_start"),
                recency_half_life_minutes=60,
            )
            for packet in eval_packets
        }
        raw_retrieval = {packet_id: refs[:top_k] for packet_id, refs in raw_candidates.items()}
        hybrid_retrieval = {
            packet_id: _merge_hybrid_retrieval(raw_candidates.get(packet_id, []), context_candidates.get(packet_id, []), top_k=top_k)
            for packet_id in raw_candidates
        }

        raw_scores = predict_packets(model, eval_packets, raw_retrieval)
        hybrid_scores = predict_packets(model, eval_packets, hybrid_retrieval)
        raw_fold_decisions = build_triage_decisions(eval_packets, raw_retrieval, raw_scores, [], thresholds, schemas)
        hybrid_fold_decisions = build_triage_decisions(eval_packets, hybrid_retrieval, hybrid_scores, [], thresholds, schemas)
        fold_outcomes = [row for row in outcomes if row.get("packet_id") in eval_packet_ids]
        eval_outcomes.extend(fold_outcomes)
        raw_decisions.extend(raw_fold_decisions)
        hybrid_decisions.extend(hybrid_fold_decisions)

        hybrid_score_delta_packet_count = 0
        hybrid_agreement_packet_count = 0
        top_hit_overlap_count = 0
        max_top_score_delta = 0.0
        for packet in eval_packets:
            packet_id = packet["packet_id"]
            raw_top = next(iter(raw_retrieval.get(packet_id, [])), None)
            hybrid_top = next(iter(hybrid_retrieval.get(packet_id, [])), None)
            raw_top_score = (raw_top or {}).get("similarity_score", 0.0)
            hybrid_top_score = (hybrid_top or {}).get("similarity_score", 0.0)
            if hybrid_top_score > raw_top_score:
                hybrid_score_delta_packet_count += 1
            if (hybrid_top or {}).get("agreement_bonus", 0.0) > 0:
                hybrid_agreement_packet_count += 1
            raw_key = _retrieval_group_key(raw_top or {}) if raw_top else None
            hybrid_key = _retrieval_group_key(hybrid_top or {}) if hybrid_top else None
            if raw_key and hybrid_key and raw_key == hybrid_key:
                top_hit_overlap_count += 1
            max_top_score_delta = max(max_top_score_delta, round(hybrid_top_score - raw_top_score, 4))

        folds.append(
            {
                "episode_id": episode_id,
                "eval_packet_ids": sorted(eval_packet_ids),
                "raw_packet_prior_doc_count": len(boundary_priors),
                "hybrid_context_prior_doc_count": len(context_priors),
                "raw_retrieval_ref_count": sum(len(item) for item in raw_retrieval.values()),
                "hybrid_retrieval_ref_count": sum(len(item) for item in hybrid_retrieval.values()),
                "hybrid_score_delta_packet_count": hybrid_score_delta_packet_count,
                "hybrid_agreement_packet_count": hybrid_agreement_packet_count,
                "top_hit_overlap": top_hit_overlap_count > 0,
                "top_hit_overlap_count": top_hit_overlap_count,
                "max_top_score_delta": max_top_score_delta,
                "anti_leakage_violation_count": boundary_incident_violations + boundary_prior_violations,
            }
        )

    return {
        "hybrid_context_prior_count": len(all_context_priors),
        "fold_count": len(episodes),
        "compare": {
            "packets_with_hybrid_score_delta_gt_raw": sum(fold["hybrid_score_delta_packet_count"] for fold in folds),
            "packets_with_agreement_bonus": sum(fold["hybrid_agreement_packet_count"] for fold in folds),
            "folds_with_top_hit_overlap": sum(1 for fold in folds if fold["top_hit_overlap"]),
            "max_top_score_delta": max((fold["max_top_score_delta"] for fold in folds), default=0.0),
            "anti_leakage_violation_count": sum(fold["anti_leakage_violation_count"] for fold in folds),
        },
        "raw_packet_metrics": compute_eval_metrics(raw_decisions, eval_outcomes, top_k=top_k),
        "hybrid_packet_metrics": compute_eval_metrics(hybrid_decisions, eval_outcomes, top_k=top_k),
        "raw_episode_metrics": _episode_metrics(raw_decisions, eval_outcomes, episodes, top_k=top_k),
        "hybrid_episode_metrics": _episode_metrics(hybrid_decisions, eval_outcomes, episodes, top_k=top_k),
        "folds": folds,
    }


def build_temporal_selective_hybrid_probe(root: Path | str) -> dict[str, Any]:
    root = Path(root)
    overlays = build_temporal_overlays(root)
    thresholds = read_yaml(root / "configs/thresholds.yaml")
    schemas = SchemaBundle(root / "schemas")
    top_k = thresholds["student"]["evaluation"]["top_k"]
    candidate_limit = max(top_k * 2, top_k)
    packets = read_jsonl(root / "data/samples/incident-packets.jsonl")
    packet_by_id = {packet["packet_id"]: packet for packet in packets if packet.get("packet_id")}
    outcomes = overlays["outcomes"]
    episodes = build_episode_index(root, overlays=overlays)
    incident_pool = [
        row
        for row in overlays["historical_incidents"]
        if row.get("cutoff_safe") and row.get("timestamp_quality") in {"exact_window_time", "exact_time_inherited"}
    ]
    raw_prior_pool = build_temporal_prior_catalog(root, overlays=overlays, episodes=episodes, packets=packets)
    all_context_priors = build_episode_context_priors(raw_prior_pool)

    raw_decisions: list[dict[str, Any]] = []
    selective_decisions: list[dict[str, Any]] = []
    eval_outcomes: list[dict[str, Any]] = []
    folds: list[dict[str, Any]] = []

    for episode in episodes:
        episode_id = episode["episode_id"]
        episode_start_ts = episode.get("episode_start_ts")
        eval_packet_ids = set(episode.get("packet_ids", []))
        eval_packets = [packet_by_id[packet_id] for packet_id in episode.get("packet_ids", []) if packet_id in packet_by_id]

        training_rows = []
        for row in overlays["training_examples"]:
            quality = row.get("timestamp_quality")
            row_packet_id = row.get("packet_id")
            if quality == "unknown_time":
                training_rows.append(row)
                continue
            if not row.get("cutoff_safe"):
                continue
            if row_packet_id in eval_packet_ids:
                continue
            if row.get("derived_ts_end") and episode_start_ts and row["derived_ts_end"] < episode_start_ts:
                training_rows.append(row)

        boundary_incidents, _, boundary_incident_violations = _admissible_history_rows(
            incident_pool,
            episode_start_ts,
            eval_packet_ids,
            episode_id,
            inclusive=True,
        )
        boundary_priors, _, boundary_prior_violations = _admissible_history_rows(
            raw_prior_pool,
            episode_start_ts,
            eval_packet_ids,
            episode_id,
            inclusive=True,
        )
        context_priors = build_episode_context_priors(boundary_priors)

        raw_history = [*boundary_incidents, *boundary_priors]
        context_history = [*boundary_incidents, *context_priors]

        model, _ = train_student_model(training_rows, thresholds)
        raw_index = build_retrieval_index(raw_history)
        context_index = build_retrieval_index(context_history)
        raw_candidates = {
            packet["packet_id"]: search_retrieval_index(
                packet,
                raw_index,
                top_k=candidate_limit,
                reference_ts=packet.get("ts_start"),
                recency_half_life_minutes=60,
            )
            for packet in eval_packets
        }
        context_candidates = {
            packet["packet_id"]: search_retrieval_index(
                packet,
                context_index,
                top_k=candidate_limit,
                reference_ts=packet.get("ts_start"),
                recency_half_life_minutes=60,
            )
            for packet in eval_packets
        }
        raw_retrieval = {packet_id: refs[:top_k] for packet_id, refs in raw_candidates.items()}
        hybrid_retrieval = {
            packet_id: _merge_hybrid_retrieval(raw_candidates.get(packet_id, []), context_candidates.get(packet_id, []), top_k=top_k)
            for packet_id in raw_candidates
        }

        raw_scores = predict_packets(model, eval_packets, raw_retrieval)
        hybrid_scores = predict_packets(model, eval_packets, hybrid_retrieval)
        raw_score_by_packet = {item["packet_id"]: item for item in raw_scores}
        hybrid_score_by_packet = {item["packet_id"]: item for item in hybrid_scores}

        selective_retrieval: dict[str, list[dict[str, Any]]] = {}
        selective_scores: list[dict[str, Any]] = []
        selected_hybrid_packet_count = 0
        selected_score_delta_packet_count = 0
        selected_confidence_delta_packet_count = 0
        max_selected_top_score_delta = 0.0

        for packet in eval_packets:
            packet_id = packet["packet_id"]
            raw_top = next(iter(raw_retrieval.get(packet_id, [])), None)
            hybrid_top = next(iter(hybrid_retrieval.get(packet_id, [])), None)
            use_hybrid = bool(
                raw_top
                and hybrid_top
                and (hybrid_top.get("agreement_bonus", 0.0) > 0)
                and (_retrieval_group_key(raw_top) == _retrieval_group_key(hybrid_top))
            )
            if use_hybrid:
                selected_hybrid_packet_count += 1
                selective_retrieval[packet_id] = hybrid_retrieval.get(packet_id, [])
                selective_scores.append(hybrid_score_by_packet[packet_id])
                top_score_delta = round((hybrid_top or {}).get("similarity_score", 0.0) - (raw_top or {}).get("similarity_score", 0.0), 4)
                if top_score_delta > 0:
                    selected_score_delta_packet_count += 1
                if hybrid_score_by_packet[packet_id]["student_confidence"] > raw_score_by_packet[packet_id]["student_confidence"]:
                    selected_confidence_delta_packet_count += 1
                max_selected_top_score_delta = max(max_selected_top_score_delta, top_score_delta)
            else:
                selective_retrieval[packet_id] = raw_retrieval.get(packet_id, [])
                selective_scores.append(raw_score_by_packet[packet_id])

        raw_fold_decisions = build_triage_decisions(eval_packets, raw_retrieval, raw_scores, [], thresholds, schemas)
        selective_fold_decisions = build_triage_decisions(eval_packets, selective_retrieval, selective_scores, [], thresholds, schemas)
        fold_outcomes = [row for row in outcomes if row.get("packet_id") in eval_packet_ids]
        eval_outcomes.extend(fold_outcomes)
        raw_decisions.extend(raw_fold_decisions)
        selective_decisions.extend(selective_fold_decisions)

        top_hit_overlap_count = 0
        for packet in eval_packets:
            packet_id = packet["packet_id"]
            raw_top = next(iter(raw_retrieval.get(packet_id, [])), None)
            selective_top = next(iter(selective_retrieval.get(packet_id, [])), None)
            raw_key = _retrieval_group_key(raw_top or {}) if raw_top else None
            selective_key = _retrieval_group_key(selective_top or {}) if selective_top else None
            if raw_key and selective_key and raw_key == selective_key:
                top_hit_overlap_count += 1

        folds.append(
            {
                "episode_id": episode_id,
                "eval_packet_ids": sorted(eval_packet_ids),
                "raw_packet_prior_doc_count": len(boundary_priors),
                "selective_hybrid_context_prior_doc_count": len(context_priors),
                "selected_hybrid_packet_count": selected_hybrid_packet_count,
                "selected_score_delta_packet_count": selected_score_delta_packet_count,
                "selected_confidence_delta_packet_count": selected_confidence_delta_packet_count,
                "raw_retrieval_ref_count": sum(len(item) for item in raw_retrieval.values()),
                "selective_retrieval_ref_count": sum(len(item) for item in selective_retrieval.values()),
                "top_hit_overlap": top_hit_overlap_count > 0,
                "top_hit_overlap_count": top_hit_overlap_count,
                "max_selected_top_score_delta": max_selected_top_score_delta,
                "anti_leakage_violation_count": boundary_incident_violations + boundary_prior_violations,
            }
        )

    return {
        "fold_count": len(episodes),
        "compare": {
            "packets_selected_for_hybrid": sum(fold["selected_hybrid_packet_count"] for fold in folds),
            "packets_with_selected_score_delta_gt_raw": sum(fold["selected_score_delta_packet_count"] for fold in folds),
            "packets_with_selected_confidence_delta_gt_raw": sum(
                fold["selected_confidence_delta_packet_count"] for fold in folds
            ),
            "folds_with_selective_routing": sum(1 for fold in folds if fold["selected_hybrid_packet_count"] > 0),
            "folds_with_top_hit_overlap": sum(1 for fold in folds if fold["top_hit_overlap"]),
            "max_selected_top_score_delta": max((fold["max_selected_top_score_delta"] for fold in folds), default=0.0),
            "anti_leakage_violation_count": sum(fold["anti_leakage_violation_count"] for fold in folds),
        },
        "raw_packet_metrics": compute_eval_metrics(raw_decisions, eval_outcomes, top_k=top_k),
        "selective_packet_metrics": compute_eval_metrics(selective_decisions, eval_outcomes, top_k=top_k),
        "raw_episode_metrics": _episode_metrics(raw_decisions, eval_outcomes, episodes, top_k=top_k),
        "selective_episode_metrics": _episode_metrics(selective_decisions, eval_outcomes, episodes, top_k=top_k),
        "folds": folds,
    }


def render_temporal_selective_hybrid_probe_markdown(result: dict[str, Any]) -> str:
    lines = ["# Temporal Selective Hybrid Probe", "", "## Compare"]
    lines.append(f"- fold count: `{result['fold_count']}`")
    for key, value in result.get("compare", {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Raw Packet Metrics"])
    for key, value in result.get("raw_packet_metrics", {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Selective Packet Metrics"])
    for key, value in result.get("selective_packet_metrics", {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Folds"])
    for fold in result.get("folds", []):
        lines.append(
            f"- `{fold['episode_id']}` packets={fold['eval_packet_ids']} raw_priors={fold['raw_packet_prior_doc_count']} selective_context_priors={fold['selective_hybrid_context_prior_doc_count']} selected_hybrid_packets={fold['selected_hybrid_packet_count']} score_delta_packets={fold['selected_score_delta_packet_count']} confidence_delta_packets={fold['selected_confidence_delta_packet_count']} top_hit_overlap={fold['top_hit_overlap']} max_selected_top_score_delta={fold['max_selected_top_score_delta']} leakage_violations={fold['anti_leakage_violation_count']}"
        )
    return "\n".join(lines) + "\n"


def render_temporal_hybrid_context_probe_markdown(result: dict[str, Any]) -> str:
    lines = ["# Temporal Hybrid Context Probe", "", "## Compare"]
    lines.append(f"- hybrid context prior count: `{result['hybrid_context_prior_count']}`")
    lines.append(f"- fold count: `{result['fold_count']}`")
    for key, value in result.get("compare", {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Raw Packet Metrics"])
    for key, value in result.get("raw_packet_metrics", {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Hybrid Packet Metrics"])
    for key, value in result.get("hybrid_packet_metrics", {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Folds"])
    for fold in result.get("folds", []):
        lines.append(
            f"- `{fold['episode_id']}` packets={fold['eval_packet_ids']} raw_priors={fold['raw_packet_prior_doc_count']} hybrid_context_priors={fold['hybrid_context_prior_doc_count']} score_delta_packets={fold['hybrid_score_delta_packet_count']} agreement_bonus_packets={fold['hybrid_agreement_packet_count']} top_hit_overlap={fold['top_hit_overlap']} max_top_score_delta={fold['max_top_score_delta']} leakage_violations={fold['anti_leakage_violation_count']}"
        )
    return "\n".join(lines) + "\n"


def render_temporal_boundary_safe_probe_markdown(result: dict[str, Any]) -> str:
    lines = ["# Temporal Boundary-safe Probe", "", "## Strict vs Boundary-safe Compare"]
    for key, value in result.get("strict_compare", {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Prototype Compare"])
    for key, value in result.get("prototype_compare", {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Boundary-safe Packet Metrics"])
    for key, value in result.get("boundary_safe_packet_metrics", {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Prototype Packet Metrics"])
    for key, value in result.get("prototype_packet_metrics", {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Folds"])
    for fold in result.get("folds", []):
        lines.append(
            f"- `{fold['episode_id']}` packets={fold['eval_packet_ids']} strict_history={fold['strict_history_doc_count']} boundary_safe_history={fold['boundary_safe_history_doc_count']} equality_added={fold['equality_admitted_doc_count']} leakage_violations={fold['anti_leakage_violation_count']} raw_priors={fold['boundary_safe_packet_prior_doc_count']} compacted_priors={fold['compacted_packet_prior_doc_count']} prototype_top_hit_overlap={fold['prototype_top_hit_overlap']}"
        )
    return "\n".join(lines) + "\n"


def render_temporal_prior_probe_markdown(result: dict[str, Any]) -> str:
    lines = ["# Temporal Prior Probe", "", "## Summary"]
    lines.append(f"- baseline strict history docs: `{result['baseline_history_doc_count']}`")
    lines.append(f"- expanded packet prior count: `{result['expanded_packet_prior_count']}`")
    lines.append(f"- expanded total doc count: `{result['expanded_total_doc_count']}`")
    lines.append(f"- fold count: `{result['fold_count']}`")
    lines.extend(["", "## Prior Summary"])
    lines.append(f"- service counts: `{result['prior_summary']['service_counts']}`")
    lines.append(f"- severity counts: `{result['prior_summary']['severity_counts']}`")
    lines.append(f"- recommended action counts: `{result['prior_summary']['recommended_action_counts']}`")
    lines.extend(["", "## Compare"])
    for key, value in result.get("compare", {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Baseline Packet Metrics"])
    for key, value in result.get("baseline_packet_metrics", {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Expanded Packet Metrics"])
    for key, value in result.get("expanded_packet_metrics", {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Folds"])
    for fold in result.get("folds", []):
        lines.append(
            f"- `{fold['episode_id']}` packets={fold['eval_packet_ids']} baseline_history={fold['baseline_history_doc_count']} expanded_priors={fold['expanded_packet_prior_doc_count']} expanded_history={fold['expanded_history_doc_count']} baseline_refs={fold['baseline_retrieval_ref_count']} expanded_refs={fold['expanded_retrieval_ref_count']} top_hit_delta={fold['top_hit_delta']}"
        )
    return "\n".join(lines) + "\n"


def render_temporal_feature_experiment_markdown(result: dict[str, Any]) -> str:
    lines = ["# Temporal Feature Experiment", "", "## Coverage"]
    lines.append(f"- packet-linked training count: `{result['temporal_feature_coverage']['packet_linked_training_count']}`")
    lines.append(f"- legacy zero-filled count: `{result['temporal_feature_coverage']['legacy_zero_filled_count']}`")
    lines.append(f"- temporal feature names: `{result['temporal_feature_names']}`")
    lines.extend(["", "## Baseline Packet Metrics"])
    for key, value in result.get("baseline_packet_metrics", {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Temporal Packet Metrics"])
    for key, value in result.get("temporal_packet_metrics", {}).items():
        lines.append(f"- {key}: `{value}`")
    return "\n".join(lines) + "\n"


def render_time_aware_eval_markdown(result: dict[str, Any]) -> str:
    lines = ["# Time-aware Historical Eval", "", "## Summary"]
    lines.append(f"- episode count: `{result['episode_count']}`")
    lines.append(f"- packet count: `{result['packet_count']}`")
    lines.append(f"- severe recall: `{result['packet_metrics']['severe_recall']}`")
    lines.append(f"- top-K precision: `{result['packet_metrics']['top_k_precision']}`")
    lines.append(f"- teacher escalation rate: `{result['packet_metrics']['teacher_escalation_rate']}`")
    lines.append(f"- severe episode recall: `{result['episode_metrics']['severe_episode_recall']}`")
    lines.append(f"- top-K episode precision: `{result['episode_metrics']['top_k_episode_precision']}`")
    lines.extend(["", "## Cutoff Leakage Audit"])
    lines.append(
        f"- folds with relaxed history > strict: `{result['cutoff_leakage_audit']['folds_with_relaxed_history_gt_strict']}`"
    )
    lines.append(
        f"- folds with relaxed refs > strict: `{result['cutoff_leakage_audit']['folds_with_relaxed_refs_gt_strict']}`"
    )
    lines.append(f"- max history incident gap: `{result['cutoff_leakage_audit']['max_history_incident_gap']}`")
    lines.extend(["", "## Recency Compare"])
    lines.append(f"- fold count: `{result['recency_compare']['fold_count']}`")
    lines.append(f"- strict cutoff fold count: `{result['recency_compare']['strict_cutoff_fold_count']}`")
    lines.append(f"- folds with recency delta: `{result['recency_compare']['folds_with_recency_delta']}`")
    lines.extend(["", "## Folds"])
    for fold in result.get("folds", []):
        lines.append(
            f"- `{fold['episode_id']}` packets={fold['eval_packet_ids']} train_rows={fold['train_row_count']} "
            f"strict_history={fold['strict_history_incident_count']} recency_refs={fold['recency_retrieval_ref_count']} relaxed_history={fold['relaxed_history_incident_count']} recency_delta={fold['recency_delta']}"
        )
    return "\n".join(lines) + "\n"
