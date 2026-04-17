from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from fixit_ai.common import read_jsonl, read_yaml
from fixit_ai.eval import compute_eval_metrics
from fixit_ai.retrieval_index import build_retrieval_index, search_retrieval_index
from fixit_ai.schema_tools import SchemaBundle
from fixit_ai.shadow import build_triage_decisions
from fixit_ai.student import predict_packets, train_student_model

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


def build_episode_index(root: Path | str, overlays: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    root = Path(root)
    overlays = overlays or build_temporal_overlays(root)
    packet_rows = read_jsonl(root / "data/samples/incident-packets.jsonl")
    packet_by_id = {row["packet_id"]: row for row in packet_rows if row.get("packet_id")}

    episodes: list[dict[str, Any]] = []
    covered_packet_ids: set[str] = set()
    for incident in overlays.get("historical_incidents", []):
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

    for packet_id in sorted(packet_by_id):
        if packet_id in covered_packet_ids:
            continue
        packet = packet_by_id[packet_id]
        episodes.append(
            {
                "episode_id": f"ep_packet_{packet_id}",
                "incident_id": None,
                "service": packet.get("service"),
                "operation": packet.get("operation"),
                "packet_ids": [packet_id],
                "episode_start_ts": packet.get("ts_start"),
                "episode_end_ts": packet.get("ts_end"),
                "episode_source": "single_packet_fallback",
                "timestamp_quality": "exact_window_time",
            }
        )

    episodes.sort(key=lambda item: (item.get("episode_start_ts") or "", item["episode_id"]))
    return episodes


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
        relaxed_retrieval = {
            packet["packet_id"]: search_retrieval_index(packet, relaxed_index, top_k=top_k) for packet in eval_packets
        }
        scores = predict_packets(model, eval_packets, strict_retrieval)
        decisions = build_triage_decisions(eval_packets, strict_retrieval, scores, [], thresholds, schemas)
        fold_outcomes = [row for row in outcomes if row.get("packet_id") in eval_packet_ids]

        for decision in decisions:
            all_decisions.append({**decision, "episode_id": episode["episode_id"]})
        all_eval_outcomes.extend(fold_outcomes)

        folds.append(
            {
                "episode_id": episode["episode_id"],
                "eval_packet_ids": sorted(eval_packet_ids),
                "train_row_count": len(training_rows),
                "unknown_time_train_row_count": unknown_time_train_rows,
                "strict_history_incident_count": len(strict_history),
                "relaxed_history_incident_count": len(relaxed_history),
                "strict_retrieval_ref_count": sum(len(item) for item in strict_retrieval.values()),
                "relaxed_retrieval_ref_count": sum(len(item) for item in relaxed_retrieval.values()),
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
    return {
        "episode_count": len(episodes),
        "packet_count": len(all_decisions),
        "packet_metrics": packet_metrics,
        "episode_metrics": episode_metrics,
        "cutoff_leakage_audit": cutoff_leakage_audit,
        "folds": folds,
    }


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
    lines.extend(["", "## Folds"])
    for fold in result.get("folds", []):
        lines.append(
            f"- `{fold['episode_id']}` packets={fold['eval_packet_ids']} train_rows={fold['train_row_count']} "
            f"strict_history={fold['strict_history_incident_count']} relaxed_history={fold['relaxed_history_incident_count']}"
        )
    return "\n".join(lines) + "\n"
