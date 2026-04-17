from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from fixit_ai.candidate_generation import generate_candidate_windows, resolve_allowed_services
from fixit_ai.common import read_jsonl, read_yaml
from fixit_ai.packet_builder import build_packets
from fixit_ai.retrieval_index import build_retrieval_index, search_retrieval_index
from fixit_ai.schema_tools import SchemaBundle
from fixit_ai.student import predict_packets, train_student_model
from fixit_ai.teacher import run_teacher_workflow

PHASE2_TARGETS = {
    "pilot_service_count": 2,
    "teacher_reviewed_count": 10,
    "teacher_fallback_ratio_max": 0.2,
    "schema_stability_days": 14,
}

TEACHER_BATCH_PATH = "data/eval/fixtures/teacher_review_batch.retained.jsonl"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _first_open_slice(workstreams: dict[str, dict[str, Any]]) -> str:
    for key in ["DW1", "DW2", "DW3"]:
        if workstreams[key]["status"] != "ready":
            return workstreams[key]["slice_id"]
    return "DW4.S1_CLOSEOUT_AND_SUCCESSOR_DECISION"


def build_replay_coverage(root: Path | str) -> dict[str, Any]:
    root = Path(root)
    metrics_rows = read_jsonl(root / "data/samples/replay/metrics_windows.jsonl")
    topology_rows = read_jsonl(root / "data/samples/replay/topology.jsonl")
    log_rows = read_jsonl(root / "data/samples/replay/log_evidence.jsonl")
    trace_rows = read_jsonl(root / "data/samples/replay/trace_evidence.jsonl")

    metric_services = sorted({row.get("service") for row in metrics_rows if row.get("service")})
    topology_services = sorted({row.get("service") for row in topology_rows if row.get("service")})
    services = sorted(set(metric_services) | set(topology_services))
    return {
        "services": services,
        "pilot_service_count": len(services),
        "metrics_window_count": len(metrics_rows),
        "log_window_count": len(log_rows),
        "trace_window_count": len(trace_rows),
        "topology_service_count": len(topology_services),
    }


def _count_by_service(records: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in records:
        service = row.get("service")
        if service:
            counts[service] += 1
    return dict(sorted(counts.items()))


def build_runtime_baseline(root: Path | str) -> dict[str, Any]:
    root = Path(root)
    services_cfg = read_yaml(root / "configs/services.yaml")
    thresholds = read_yaml(root / "configs/thresholds.yaml")
    allowed_services = sorted(resolve_allowed_services(services_cfg) or [])

    metrics_rows = read_jsonl(root / "data/samples/replay/metrics_windows.jsonl")
    logs = read_jsonl(root / "data/samples/replay/log_evidence.jsonl")
    traces = read_jsonl(root / "data/samples/replay/trace_evidence.jsonl")
    topology = read_jsonl(root / "data/samples/replay/topology.jsonl")
    memory = read_jsonl(root / "data/samples/replay/memory_summaries.jsonl")

    candidates = generate_candidate_windows(
        metrics_rows,
        thresholds,
        allowed_services=set(allowed_services) if allowed_services else None,
    )
    packets = build_packets(candidates, logs, traces, topology, memory, SchemaBundle(root / "schemas"))

    metrics_windows_by_service = _count_by_service(metrics_rows)
    candidate_windows_by_service = _count_by_service(candidates)
    packets_by_service = _count_by_service(packets)
    packet_ids_by_service = {
        service: [packet["packet_id"] for packet in packets if packet.get("service") == service]
        for service in sorted(packets_by_service)
    }
    observed_metric_services = sorted(metrics_windows_by_service)
    candidate_services = sorted(candidate_windows_by_service)
    packet_services = sorted(packets_by_service)

    return {
        "runtime_mode": "multi_pilot_allowlist" if len(allowed_services) > 1 else "single_pilot_allowlist",
        "runtime_allowlist_services": allowed_services,
        "runtime_allowlist_count": len(allowed_services),
        "observed_metric_services": observed_metric_services,
        "candidate_services": candidate_services,
        "packet_services": packet_services,
        "services_without_candidates": [service for service in allowed_services if service not in candidate_windows_by_service],
        "metrics_windows_by_service": metrics_windows_by_service,
        "candidate_windows_by_service": candidate_windows_by_service,
        "packets_by_service": packets_by_service,
        "packet_ids_by_service": packet_ids_by_service,
    }


def _derive_teacher_workflow(root: Path) -> dict[str, Any]:
    services_cfg = read_yaml(root / "configs/services.yaml")
    thresholds = read_yaml(root / "configs/thresholds.yaml")
    teacher_budget = read_yaml(root / "configs/teacher-budget.yaml")
    metrics = read_jsonl(root / "data/samples/replay/metrics_windows.jsonl")
    logs = read_jsonl(root / "data/samples/replay/log_evidence.jsonl")
    traces = read_jsonl(root / "data/samples/replay/trace_evidence.jsonl")
    topology = read_jsonl(root / "data/samples/replay/topology.jsonl")
    memory = read_jsonl(root / "data/samples/replay/memory_summaries.jsonl")
    training = read_jsonl(root / "data/eval/replay/training_examples.jsonl")
    incidents = read_jsonl(root / "data/eval/replay/historical_incidents.jsonl")
    seed_judgements = read_jsonl(root / "data/eval/replay/manual_teacher_judgements.jsonl")

    candidates = generate_candidate_windows(
        metrics,
        thresholds,
        allowed_services=resolve_allowed_services(services_cfg),
    )
    packets = build_packets(candidates, logs, traces, topology, memory, SchemaBundle(root / "schemas"))
    index = build_retrieval_index(incidents)
    retrieval = {packet["packet_id"]: search_retrieval_index(packet, index, top_k=3) for packet in packets}
    model, _ = train_student_model(training, thresholds)
    scores = predict_packets(model, packets, retrieval)
    return run_teacher_workflow(packets, retrieval, scores, teacher_budget, seed_judgements=seed_judgements)


def build_accumulation_baseline(root: Path | str, reference_date: date | None = None) -> dict[str, Any]:
    root = Path(root)
    reference_date = reference_date or date.today()

    manifest = _load_json(root / "data/samples/replay-pack-manifest.json")
    teacher_summary_artifact = _load_json(root / "data/eval/teacher-queue-summary.json")
    label_ledger = _load_json(root / "data/eval/label-ledger.json")
    calibration = _load_json(root / "data/eval/calibration-report.json")
    evidence_ledger = _load_json(root / "data/eval/local-small-model-evidence-ledger.json")
    phase2_audit = _load_json(root / "data/eval/local-small-model-phase2-audit.json")
    final_verdict = _load_json(root / "data/eval/local-small-model-final-verdict.json")
    coverage = build_replay_coverage(root)

    teacher_workflow = _derive_teacher_workflow(root)
    teacher_requests = teacher_workflow["requests"]
    teacher_reviews = teacher_workflow["reviews"]
    teacher_fallbacks = teacher_workflow["fallbacks"]
    teacher_summary = teacher_workflow["summary"]

    teacher_selected_count = teacher_summary.get("selected_count", len(teacher_requests))
    teacher_reviewed_count = len(teacher_reviews)
    teacher_fallback_count = len(teacher_fallbacks)
    teacher_fallback_ratio = round(teacher_fallback_count / max(teacher_selected_count, 1), 4)
    replay_output_row_total = sum(item.get("output_row_count", 0) for item in manifest.get("datasets", []))

    queue_summary_consistent = (
        teacher_summary_artifact.get("selected_count", teacher_selected_count) == teacher_selected_count
        and teacher_summary_artifact.get("reviewed_count", teacher_reviewed_count) == teacher_reviewed_count
        and teacher_summary_artifact.get("fallback_count", teacher_fallback_count) == teacher_fallback_count
    )

    return {
        "reference_date": reference_date.isoformat(),
        "predecessor_family": "LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW",
        "predecessor_verdict": final_verdict.get("verdict"),
        "recommended_successor": final_verdict.get("recommended_successor"),
        "predecessor_reason": final_verdict.get("reason"),
        "phase2_summary": dict(phase2_audit.get("summary", {})),
        "pilot_service_count": coverage["pilot_service_count"],
        "coverage_services": coverage["services"],
        "metrics_window_count": coverage["metrics_window_count"],
        "replay_dataset_count": evidence_ledger.get("replay_dataset_count", 0),
        "replay_output_row_total": replay_output_row_total,
        "teacher_request_count": len(teacher_requests),
        "teacher_selected_count": teacher_selected_count,
        "teacher_reviewed_count": teacher_reviewed_count,
        "teacher_fallback_count": teacher_fallback_count,
        "teacher_fallback_ratio": teacher_fallback_ratio,
        "queue_summary_consistent": queue_summary_consistent,
        "label_sources": dict(label_ledger.get("counts_by_source", {})),
        "outcome_total": evidence_ledger.get("outcome_total", 0),
        "outcome_severe_total": evidence_ledger.get("outcome_severe_total", 0),
        "calibration_bucket_count": evidence_ledger.get("calibration_bucket_count", len(calibration.get("bucket_summary", []))),
        "threshold_review_action": evidence_ledger.get(
            "threshold_review_action", calibration.get("threshold_review", {}).get("recommended_action")
        ),
        "schema_stability_days": evidence_ledger.get("schema_stability_days", 0),
        "severe_recall": evidence_ledger.get("severe_recall", 0.0),
        "top_k_precision": evidence_ledger.get("top_k_precision", 0.0),
    }


def build_target_ledger(baseline: dict[str, Any]) -> dict[str, Any]:
    teacher_rubric_labels = baseline.get("label_sources", {}).get("teacher_rubric", 0)
    dw1 = {
        "slice_id": "DW1.S1_MULTI_PILOT_REPLAY_COVERAGE_EXPANSION",
        "focus": "expand bounded replay evidence beyond the single current pilot",
        "current_pilot_service_count": baseline.get("pilot_service_count", 0),
        "target_pilot_service_count": PHASE2_TARGETS["pilot_service_count"],
        "pilot_service_count_gap": max(PHASE2_TARGETS["pilot_service_count"] - baseline.get("pilot_service_count", 0), 0),
        "current_replay_dataset_count": baseline.get("replay_dataset_count", 0),
        "status": "open" if baseline.get("pilot_service_count", 0) < PHASE2_TARGETS["pilot_service_count"] else "ready",
    }
    dw2 = {
        "slice_id": "DW2.S1_TEACHER_REVIEW_BATCH_AND_LABEL_SOURCE_EXPANSION",
        "focus": "grow reviewed teacher volume and keep label-source mix moving with provenance",
        "current_teacher_reviewed_count": baseline.get("teacher_reviewed_count", 0),
        "target_teacher_reviewed_count": PHASE2_TARGETS["teacher_reviewed_count"],
        "teacher_reviewed_count_gap": max(
            PHASE2_TARGETS["teacher_reviewed_count"] - baseline.get("teacher_reviewed_count", 0), 0
        ),
        "current_teacher_fallback_ratio": baseline.get("teacher_fallback_ratio", 0.0),
        "target_teacher_fallback_ratio_max": PHASE2_TARGETS["teacher_fallback_ratio_max"],
        "teacher_fallback_ratio_gap": round(
            max(baseline.get("teacher_fallback_ratio", 0.0) - PHASE2_TARGETS["teacher_fallback_ratio_max"], 0.0),
            4,
        ),
        "current_teacher_rubric_label_count": teacher_rubric_labels,
        "teacher_rubric_label_growth_needed": teacher_rubric_labels <= baseline.get("teacher_reviewed_count", 0),
        "status": "open"
        if baseline.get("teacher_reviewed_count", 0) < PHASE2_TARGETS["teacher_reviewed_count"]
        or baseline.get("teacher_fallback_ratio", 0.0) > PHASE2_TARGETS["teacher_fallback_ratio_max"]
        else "ready",
    }
    dw3 = {
        "slice_id": "DW3.S1_SCHEMA_STABILITY_HISTORY_AND_PHASE2_REFRESH",
        "focus": "track schema stability over time and re-evaluate phase-2 readiness with refreshed evidence",
        "current_schema_stability_days": baseline.get("schema_stability_days", 0),
        "target_schema_stability_days": PHASE2_TARGETS["schema_stability_days"],
        "schema_stability_days_gap": max(
            PHASE2_TARGETS["schema_stability_days"] - baseline.get("schema_stability_days", 0), 0
        ),
        "phase2_summary": dict(baseline.get("phase2_summary", {})),
        "refresh_preconditions": [
            "multi-pilot replay evidence exceeds 1 bounded pilot",
            "reviewed teacher volume materially exceeds predecessor baseline",
            "schema fingerprint history has at least one persisted checkpoint",
        ],
        "status": "open" if baseline.get("schema_stability_days", 0) < PHASE2_TARGETS["schema_stability_days"] else "ready",
    }
    workstreams = {"DW1": dw1, "DW2": dw2, "DW3": dw3}
    execution_order = [dw1["slice_id"], dw2["slice_id"], dw3["slice_id"]]
    return {
        "recommended_next_slice": _first_open_slice(workstreams),
        "execution_order": execution_order,
        "workstreams": workstreams,
    }


def build_teacher_accumulation_ledger(root: Path | str) -> dict[str, Any]:
    root = Path(root)
    predecessor = _load_json(root / "data/eval/local-small-model-evidence-ledger.json")
    label_ledger = _load_json(root / "data/eval/label-ledger.json")
    retained_reviews = read_jsonl(root / TEACHER_BATCH_PATH)
    training_rows = read_jsonl(root / "data/eval/training_examples.jsonl")

    current_reviewed_count = len(retained_reviews)
    predecessor_reviewed_count = predecessor.get("teacher_reviewed_count", 0)
    current_packet_ids = sorted(item.get("packet_id") for item in retained_reviews if item.get("packet_id"))
    label_teacher_rubric_count = label_ledger.get("counts_by_source", {}).get("teacher_rubric", 0)
    training_packet_ids = {row.get("packet_id") for row in training_rows if row.get("packet_id")}
    training_backfill_count = sum(1 for packet_id in current_packet_ids if packet_id in training_packet_ids)

    return {
        "predecessor_teacher_reviewed_count": predecessor_reviewed_count,
        "current_teacher_reviewed_count": current_reviewed_count,
        "teacher_reviewed_delta": current_reviewed_count - predecessor_reviewed_count,
        "current_teacher_packet_ids": current_packet_ids,
        "label_teacher_rubric_count": label_teacher_rubric_count,
        "training_backfill_count": training_backfill_count,
        "teacher_label_gap": max(current_reviewed_count - training_backfill_count, 0),
        "retained_review_batch_path": TEACHER_BATCH_PATH,
    }


def build_teacher_daily_review_batch(root: Path | str) -> dict[str, Any]:
    root = Path(root)
    teacher_budget = read_yaml(root / "configs/teacher-budget.yaml")
    workflow = _derive_teacher_workflow(root)
    requests = workflow["requests"]
    reviews = workflow["reviews"]
    fallbacks = workflow["fallbacks"]

    selected_count = len(requests)
    reviewed_count = len(reviews)
    fallback_count = len(fallbacks)

    return {
        "selection_lane": "bounded_teacher_hard_case_batch",
        "max_reviews_per_run": teacher_budget.get("max_reviews_per_run", 0),
        "max_tokens_per_run": teacher_budget.get("max_tokens_per_run", 0),
        "selected_count": selected_count,
        "reviewed_count": reviewed_count,
        "fallback_count": fallback_count,
        "reviewed_packet_ids": sorted(item.get("packet_id") for item in reviews if item.get("packet_id")),
        "fallback_packet_ids": sorted(item.get("packet_id") for item in fallbacks if item.get("packet_id")),
        "review_rate": round(reviewed_count / max(selected_count, 1), 4),
        "remaining_to_phase2_target": max(PHASE2_TARGETS["teacher_reviewed_count"] - reviewed_count, 0),
    }


def _historical_incident_packet_ids(incidents: list[dict[str, Any]]) -> set[str]:
    packet_ids: set[str] = set()
    for row in incidents:
        if row.get("source_packet_id"):
            packet_ids.add(row["source_packet_id"])
        for packet_id in row.get("source_packet_ids", []):
            if packet_id:
                packet_ids.add(packet_id)
    return packet_ids


def build_human_writeback_audit(root: Path | str) -> dict[str, Any]:
    root = Path(root)
    batch = build_teacher_daily_review_batch(root)
    target_packet_ids = list(batch.get("reviewed_packet_ids", []))

    outcomes = read_jsonl(root / "data/eval/outcomes.jsonl")
    training_rows = read_jsonl(root / "data/eval/training_examples.jsonl")
    incidents = read_jsonl(root / "data/eval/historical_incidents.jsonl")

    outcome_packet_ids = {row.get("packet_id") for row in outcomes if row.get("packet_id")}
    training_packet_ids = {row.get("packet_id") for row in training_rows if row.get("packet_id")}
    incident_packet_ids = _historical_incident_packet_ids(incidents)

    coverage = []
    for packet_id in target_packet_ids:
        outcome_present = packet_id in outcome_packet_ids
        training_present = packet_id in training_packet_ids
        incident_present = packet_id in incident_packet_ids
        coverage.append(
            {
                "packet_id": packet_id,
                "outcome_present": outcome_present,
                "training_present": training_present,
                "incident_present": incident_present,
                "fully_backfilled": outcome_present and training_present and incident_present,
            }
        )

    return {
        "target_packet_ids": target_packet_ids,
        "outcome_backfilled_count": sum(1 for item in coverage if item["outcome_present"]),
        "training_backfilled_count": sum(1 for item in coverage if item["training_present"]),
        "incident_backfilled_count": sum(1 for item in coverage if item["incident_present"]),
        "fully_backfilled_count": sum(1 for item in coverage if item["fully_backfilled"]),
        "missing_outcome_packet_ids": [item["packet_id"] for item in coverage if not item["outcome_present"]],
        "missing_training_packet_ids": [item["packet_id"] for item in coverage if not item["training_present"]],
        "missing_incident_packet_ids": [item["packet_id"] for item in coverage if not item["incident_present"]],
        "coverage": coverage,
    }


def build_volume_capacity(root: Path | str) -> dict[str, Any]:
    root = Path(root)
    runtime = build_runtime_baseline(root)
    teacher_batch = build_teacher_daily_review_batch(root)

    reviewed_packet_ids = list(teacher_batch.get("reviewed_packet_ids", []))
    packet_ids = [
        packet_id
        for packet_ids in runtime.get("packet_ids_by_service", {}).values()
        for packet_id in packet_ids
        if packet_id
    ]
    current_packet_ids = sorted(dict.fromkeys(packet_ids))
    visible_unreviewed_packet_ids = [packet_id for packet_id in current_packet_ids if packet_id not in reviewed_packet_ids]

    current_reviewed_count = teacher_batch.get("reviewed_count", 0)
    current_packet_count = len(current_packet_ids)
    visible_unreviewed_remainder = len(visible_unreviewed_packet_ids)
    visible_maximum_reviewed_ceiling = current_reviewed_count + visible_unreviewed_remainder
    remaining_to_phase2_target = max(PHASE2_TARGETS["teacher_reviewed_count"] - current_reviewed_count, 0)

    if visible_maximum_reviewed_ceiling < PHASE2_TARGETS["teacher_reviewed_count"]:
        next_slice = "RW2A.S1_BOUNDED_PACKET_SUPPLY_EXPANSION_TO_CLEAR_VOLUME_GATE"
        routing_reason = "current bounded packet supply cannot clear reviewed-volume target"
    else:
        next_slice = "RW2B.S1_DAILY_REVIEW_APPEND_AND_GAP_BURNDOWN"
        routing_reason = "current bounded packet supply can clear reviewed-volume target"

    return {
        "current_reviewed_count": current_reviewed_count,
        "reviewed_packet_ids": reviewed_packet_ids,
        "current_packet_count": current_packet_count,
        "current_packet_ids": current_packet_ids,
        "visible_unreviewed_remainder": visible_unreviewed_remainder,
        "visible_unreviewed_packet_ids": visible_unreviewed_packet_ids,
        "visible_maximum_reviewed_ceiling": visible_maximum_reviewed_ceiling,
        "phase2_target_reviewed_count": PHASE2_TARGETS["teacher_reviewed_count"],
        "remaining_to_phase2_target": remaining_to_phase2_target,
        "runtime_allowlist_services": runtime.get("runtime_allowlist_services", []),
        "candidate_services": runtime.get("candidate_services", []),
        "packet_services": runtime.get("packet_services", []),
        "services_without_candidates": runtime.get("services_without_candidates", []),
        "next_slice": next_slice,
        "routing_reason": routing_reason,
    }


def _schema_fingerprint(schema_root: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    schema_files = sorted(schema_root.glob("*.json"))
    for path in schema_files:
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest(), len(schema_files)


def build_schema_stability_history(
    root: Path | str,
    reference_date: date | None = None,
    captured_at: str | None = None,
) -> dict[str, Any]:
    root = Path(root)
    reference_date = reference_date or date.today()
    captured_at = captured_at or datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    schema_root = root / "schemas"
    history_path = root / "data/eval/schema-stability-history.json"
    fingerprint, schema_file_count = _schema_fingerprint(schema_root)

    existing = _load_json(history_path) if history_path.exists() else {}
    snapshots = list(existing.get("snapshots", []))
    snapshots.append(
        {
            "date": reference_date.isoformat(),
            "captured_at": captured_at,
            "fingerprint": fingerprint,
        }
    )

    normalized = []
    seen: set[tuple[str | None, str | None, str | None]] = set()
    for item in sorted(snapshots, key=lambda row: (row.get("date", ""), row.get("captured_at", ""), row.get("fingerprint", ""))):
        key = (item.get("date"), item.get("captured_at"), item.get("fingerprint"))
        if key in seen:
            continue
        seen.add(key)
        normalized.append(item)

    first_observed = min(
        (date.fromisoformat(item["date"]) for item in normalized if item.get("fingerprint") == fingerprint),
        default=reference_date,
    )
    return {
        "reference_date": reference_date.isoformat(),
        "schema_file_count": schema_file_count,
        "current_fingerprint": fingerprint,
        "first_observed_date": first_observed.isoformat(),
        "current_elapsed_days": max((reference_date - first_observed).days, 0),
        "snapshot_count": len(normalized),
        "snapshots": normalized,
    }


def build_schema_dayspan_progress(
    root: Path | str,
    reference_date: date | None = None,
    schema_history: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(root)
    reference_date = reference_date or date.today()
    schema_history = schema_history or (
        _load_json(root / "data/eval/schema-stability-history.json")
        if (root / "data/eval/schema-stability-history.json").exists()
        else build_schema_stability_history(root, reference_date=reference_date)
    )

    distinct_observed_dates = sorted({item.get("date") for item in schema_history.get("snapshots", []) if item.get("date")})
    distinct_observed_date_count = len(distinct_observed_dates)
    current_elapsed_days = schema_history.get("current_elapsed_days", 0)
    remaining_days_to_target = max(PHASE2_TARGETS["schema_stability_days"] - current_elapsed_days, 0)
    rerun_admissible_from_schema_gate = current_elapsed_days >= PHASE2_TARGETS["schema_stability_days"]

    return {
        "reference_date": reference_date.isoformat(),
        "first_observed_date": schema_history.get("first_observed_date"),
        "latest_observed_date": max(distinct_observed_dates) if distinct_observed_dates else None,
        "distinct_observed_dates": distinct_observed_dates,
        "distinct_observed_date_count": distinct_observed_date_count,
        "snapshot_count": schema_history.get("snapshot_count", 0),
        "current_elapsed_days": current_elapsed_days,
        "remaining_days_to_target": remaining_days_to_target,
        "schema_target_days": PHASE2_TARGETS["schema_stability_days"],
        "schema_gate_status": "ready" if rerun_admissible_from_schema_gate else "blocked",
        "rerun_admissible_from_schema_gate": rerun_admissible_from_schema_gate,
        "reason": "same-day snapshots do not count as multi-day schema stability",
    }


def build_phase2_refresh(
    root: Path | str,
    baseline: dict[str, Any],
    teacher_ledger: dict[str, Any],
    schema_history: dict[str, Any],
) -> dict[str, Any]:
    _ = Path(root)
    criteria: list[dict[str, Any]] = []

    replay_status = "met" if baseline.get("pilot_service_count", 0) >= PHASE2_TARGETS["pilot_service_count"] else "unmet"
    criteria.append(
        {
            "criterion_id": "multi_pilot_replay_coverage",
            "status": replay_status,
            "rationale": f"pilot_service_count={baseline.get('pilot_service_count', 0)} services={baseline.get('coverage_services', [])}",
        }
    )

    current_reviewed = teacher_ledger.get("current_teacher_reviewed_count", 0)
    if current_reviewed >= PHASE2_TARGETS["teacher_reviewed_count"]:
        teacher_status = "met"
    elif current_reviewed > teacher_ledger.get("predecessor_teacher_reviewed_count", 0):
        teacher_status = "partial"
    else:
        teacher_status = "unmet"
    criteria.append(
        {
            "criterion_id": "teacher_reviewed_volume_growth",
            "status": teacher_status,
            "rationale": f"current_reviewed={current_reviewed} predecessor={teacher_ledger.get('predecessor_teacher_reviewed_count', 0)} target={PHASE2_TARGETS['teacher_reviewed_count']}",
        }
    )

    schema_days = schema_history.get("current_elapsed_days", 0)
    schema_status = "met" if schema_days >= PHASE2_TARGETS["schema_stability_days"] else "unmet"
    criteria.append(
        {
            "criterion_id": "schema_stability_window",
            "status": schema_status,
            "rationale": f"schema_stability_days={schema_days} target={PHASE2_TARGETS['schema_stability_days']}",
        }
    )

    if replay_status == "met" and teacher_status == "met" and schema_status == "met":
        verdict = "rerun-review"
        successor = "LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_RERUN"
        reason = "Replay coverage, reviewed teacher volume, and schema stability all satisfy the minimum accumulation gates."
    else:
        verdict = "not-yet"
        successor = "ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP"
        reason = "Replay breadth improved, but teacher volume and schema stability still block a small-model review rerun."

    summary = {
        "met": sum(1 for item in criteria if item["status"] == "met"),
        "partial": sum(1 for item in criteria if item["status"] == "partial"),
        "unmet": sum(1 for item in criteria if item["status"] == "unmet"),
    }
    return {
        "criteria": criteria,
        "summary": summary,
        "verdict": verdict,
        "recommended_successor": successor,
        "reason": reason,
    }


def render_runtime_baseline_markdown(runtime: dict[str, Any]) -> str:
    lines = ["# Data and Teacher Runtime Baseline"]
    lines.extend(["", "## Runtime Allowlist"])
    lines.append(f"- runtime mode: `{runtime['runtime_mode']}`")
    lines.append(f"- allowlist services: `{runtime['runtime_allowlist_services']}`")
    lines.append(f"- observed metric services: `{runtime['observed_metric_services']}`")
    lines.append(f"- candidate services: `{runtime['candidate_services']}`")
    lines.append(f"- packet services: `{runtime['packet_services']}`")
    lines.append(f"- services without candidates: `{runtime['services_without_candidates']}`")
    lines.extend(["", "## Counts By Service"])
    lines.append(f"- metrics windows: `{runtime['metrics_windows_by_service']}`")
    lines.append(f"- candidate windows: `{runtime['candidate_windows_by_service']}`")
    lines.append(f"- packets: `{runtime['packets_by_service']}`")
    lines.append(f"- packet ids: `{runtime['packet_ids_by_service']}`")
    return "\n".join(lines) + "\n"


def render_teacher_daily_review_batch_markdown(batch: dict[str, Any]) -> str:
    lines = ["# Data and Teacher Daily Review Batch"]
    lines.extend(["", "## Daily Review Batch"])
    lines.append(f"- selection lane: `{batch['selection_lane']}`")
    lines.append(f"- max reviews per run: `{batch['max_reviews_per_run']}`")
    lines.append(f"- max tokens per run: `{batch['max_tokens_per_run']}`")
    lines.append(f"- selected count: `{batch['selected_count']}`")
    lines.append(f"- reviewed count: `{batch['reviewed_count']}`")
    lines.append(f"- fallback count: `{batch['fallback_count']}`")
    lines.append(f"- reviewed packet ids: `{batch['reviewed_packet_ids']}`")
    lines.append(f"- fallback packet ids: `{batch['fallback_packet_ids']}`")
    lines.append(f"- review rate: `{batch['review_rate']}`")
    lines.append(f"- remaining to phase-2 target: `{batch['remaining_to_phase2_target']}`")
    return "\n".join(lines) + "\n"


def render_human_writeback_audit_markdown(audit: dict[str, Any]) -> str:
    lines = ["# Data and Teacher Human Write-back Audit"]
    lines.extend(["", "## Human Write-back Coverage"])
    lines.append(f"- target packet ids: `{audit['target_packet_ids']}`")
    lines.append(f"- outcome backfilled count: `{audit['outcome_backfilled_count']}`")
    lines.append(f"- training backfilled count: `{audit['training_backfilled_count']}`")
    lines.append(f"- incident backfilled count: `{audit['incident_backfilled_count']}`")
    lines.append(f"- fully backfilled count: `{audit['fully_backfilled_count']}`")
    lines.append(f"- missing outcomes: `{audit['missing_outcome_packet_ids']}`")
    lines.append(f"- missing training rows: `{audit['missing_training_packet_ids']}`")
    lines.append(f"- missing incident summaries: `{audit['missing_incident_packet_ids']}`")
    return "\n".join(lines) + "\n"


def render_volume_capacity_markdown(capacity: dict[str, Any]) -> str:
    lines = ["# Data and Teacher Review Volume Capacity"]
    lines.extend(["", "## Review Volume Capacity"])
    lines.append(f"- current reviewed count: `{capacity['current_reviewed_count']}`")
    lines.append(f"- phase-2 target reviewed count: `{capacity['phase2_target_reviewed_count']}`")
    lines.append(f"- remaining to phase-2 target: `{capacity['remaining_to_phase2_target']}`")
    lines.append(f"- current packet count: `{capacity['current_packet_count']}`")
    lines.append(f"- current packet ids: `{capacity['current_packet_ids']}`")
    lines.append(f"- visible unreviewed remainder: `{capacity['visible_unreviewed_remainder']}`")
    lines.append(f"- visible unreviewed packet ids: `{capacity['visible_unreviewed_packet_ids']}`")
    lines.append(f"- visible maximum reviewed ceiling: `{capacity['visible_maximum_reviewed_ceiling']}`")
    lines.append(f"- runtime allowlist services: `{capacity['runtime_allowlist_services']}`")
    lines.append(f"- candidate services: `{capacity['candidate_services']}`")
    lines.append(f"- services without candidates: `{capacity['services_without_candidates']}`")
    lines.append(f"- next slice: `{capacity['next_slice']}`")
    lines.append(f"- routing reason: {capacity['routing_reason']}")
    return "\n".join(lines) + "\n"


def render_schema_dayspan_progress_markdown(progress: dict[str, Any]) -> str:
    lines = ["# Data and Teacher Schema Day-span Progress"]
    lines.extend(["", "## Schema Day-span Progress"])
    lines.append(f"- first observed date: `{progress['first_observed_date']}`")
    lines.append(f"- latest observed date: `{progress['latest_observed_date']}`")
    lines.append(f"- distinct observed dates: `{progress['distinct_observed_dates']}`")
    lines.append(f"- distinct observed date count: `{progress['distinct_observed_date_count']}`")
    lines.append(f"- snapshot count: `{progress['snapshot_count']}`")
    lines.append(f"- current elapsed days: `{progress['current_elapsed_days']}`")
    lines.append(f"- remaining days to target: `{progress['remaining_days_to_target']}`")
    lines.append(f"- schema gate status: `{progress['schema_gate_status']}`")
    lines.append(f"- rerun admissible from schema gate: `{progress['rerun_admissible_from_schema_gate']}`")
    lines.append(f"- reason: {progress['reason']}")
    return "\n".join(lines) + "\n"


def render_accumulation_report(baseline: dict[str, Any], targets: dict[str, Any]) -> str:
    lines = ["# Data and Teacher Accumulation Baseline"]
    lines.extend(["", "## Predecessor Readback"])
    lines.append(f"- predecessor family: `{baseline['predecessor_family']}`")
    lines.append(f"- predecessor verdict: `{baseline['predecessor_verdict']}`")
    lines.append(f"- recommended successor: `{baseline['recommended_successor']}`")
    lines.append(f"- predecessor reason: {baseline['predecessor_reason']}")
    lines.append(f"- phase-2 summary: `{baseline['phase2_summary']}`")

    lines.extend(["", "## Current Baseline"])
    lines.append(f"- pilot service count: `{baseline['pilot_service_count']}`")
    lines.append(f"- coverage services: `{baseline['coverage_services']}`")
    lines.append(f"- replay dataset count: `{baseline['replay_dataset_count']}`")
    lines.append(f"- replay output row total: `{baseline['replay_output_row_total']}`")
    lines.append(f"- teacher request count: `{baseline['teacher_request_count']}`")
    lines.append(f"- teacher reviewed count: `{baseline['teacher_reviewed_count']}`")
    lines.append(f"- teacher fallback count: `{baseline['teacher_fallback_count']}`")
    lines.append(f"- teacher fallback ratio: `{baseline['teacher_fallback_ratio']}`")
    lines.append(f"- queue summary consistent: `{baseline['queue_summary_consistent']}`")
    lines.append(f"- label sources: `{baseline['label_sources']}`")
    lines.append(f"- schema stability days: `{baseline['schema_stability_days']}`")
    lines.append(f"- severe recall: `{baseline['severe_recall']}`")
    lines.append(f"- top-K precision: `{baseline['top_k_precision']}`")

    lines.extend(["", "## Target Gaps by Workstream"])
    for key in ["DW1", "DW2", "DW3"]:
        item = targets["workstreams"][key]
        lines.append(f"- `{item['slice_id']}` :: {item['focus']}")
        if key == "DW1":
            lines.append(
                f"  - pilot service count `{item['current_pilot_service_count']}` -> `{item['target_pilot_service_count']}` (gap `{item['pilot_service_count_gap']}`)"
            )
        elif key == "DW2":
            lines.append(
                f"  - teacher reviewed count `{item['current_teacher_reviewed_count']}` -> `{item['target_teacher_reviewed_count']}` (gap `{item['teacher_reviewed_count_gap']}`)"
            )
            lines.append(
                f"  - teacher fallback ratio `{item['current_teacher_fallback_ratio']}` <= `{item['target_teacher_fallback_ratio_max']}` (gap `{item['teacher_fallback_ratio_gap']}`)"
            )
            lines.append(
                f"  - teacher rubric label growth needed: `{item['teacher_rubric_label_growth_needed']}` from current `{item['current_teacher_rubric_label_count']}`"
            )
        else:
            lines.append(
                f"  - schema stability days `{item['current_schema_stability_days']}` -> `{item['target_schema_stability_days']}` (gap `{item['schema_stability_days_gap']}`)"
            )
            lines.append(f"  - readiness refresh preconditions: `{item['refresh_preconditions']}`")

    lines.extend(["", "## Suggested Execution Order"])
    lines.append(f"- recommended next slice: `{targets['recommended_next_slice']}`")
    for slice_id in targets["execution_order"]:
        lines.append(f"- `{slice_id}`")
    return "\n".join(lines) + "\n"


def build_family_closeout(
    baseline: dict[str, Any],
    teacher_ledger: dict[str, Any],
    schema_history: dict[str, Any],
    refresh: dict[str, Any],
) -> dict[str, Any]:
    improvements = []
    if baseline.get("pilot_service_count", 0) >= PHASE2_TARGETS["pilot_service_count"]:
        improvements.append("bounded replay coverage now spans more than one service family")
    if teacher_ledger.get("teacher_reviewed_delta", 0) > 0:
        improvements.append("reviewed teacher batch exceeds predecessor baseline")
    if schema_history.get("schema_file_count", 0) > 0:
        improvements.append("schema fingerprint history artifact now exists")

    residuals = []
    if teacher_ledger.get("current_teacher_reviewed_count", 0) < PHASE2_TARGETS["teacher_reviewed_count"]:
        residuals.append("teacher volume still below phase-2 threshold")
    if schema_history.get("current_elapsed_days", 0) < PHASE2_TARGETS["schema_stability_days"]:
        residuals.append("schema stability window still below 14 days")
    if refresh.get("verdict") != "rerun-review":
        residuals.append("phase-2 readiness remains not-yet after refreshed evidence")

    return {
        "family": "ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION",
        "family_verdict": "accept_with_residuals",
        "completed_slices": [
            "DW0.S1_ACCUMULATION_BASELINE_TRACKER_AND_TARGET_REPORT",
            "DW1.S1_MULTI_PILOT_REPLAY_COVERAGE_EXPANSION",
            "DW2.S1_TEACHER_REVIEW_BATCH_AND_LABEL_SOURCE_EXPANSION",
            "DW3.S1_SCHEMA_STABILITY_HISTORY_AND_PHASE2_REFRESH",
            "DW4.S1_CLOSEOUT_AND_SUCCESSOR_DECISION",
        ],
        "recommended_successor": refresh.get("recommended_successor"),
        "phase2_verdict": refresh.get("verdict"),
        "improvements": improvements,
        "residuals": residuals,
    }


def build_followup_family_closeout(
    runtime: dict[str, Any],
    teacher_batch: dict[str, Any],
    writeback: dict[str, Any],
    schema_history: dict[str, Any],
    refresh: dict[str, Any],
) -> dict[str, Any]:
    improvements = []
    if runtime.get("runtime_mode") == "multi_pilot_allowlist":
        improvements.append("runtime entry is now bounded by a multi-pilot allowlist instead of a single pilot service")
    if teacher_batch.get("reviewed_count", 0) > 0 and teacher_batch.get("fallback_count", 0) == 0:
        improvements.append("daily teacher batch now reviews all selected hard cases without fallback")
    if writeback.get("fully_backfilled_count", 0) == len(writeback.get("target_packet_ids", [])) and writeback.get("target_packet_ids"):
        improvements.append("reviewed packets now have explicit outcome, training, and incident-summary backfill coverage")
    if schema_history.get("snapshot_count", 0) >= 2:
        improvements.append("schema stability history now preserves append-only checkpoints")

    residuals = []
    if teacher_batch.get("reviewed_count", 0) < PHASE2_TARGETS["teacher_reviewed_count"]:
        residuals.append("teacher volume still below phase-2 threshold")
    if schema_history.get("current_elapsed_days", 0) < PHASE2_TARGETS["schema_stability_days"]:
        residuals.append("schema stability window still below 14 days")
    if refresh.get("verdict") != "rerun-review":
        residuals.append("phase-2 readiness remains not-yet after refreshed followup evidence")

    return {
        "family": "ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP",
        "family_verdict": "accept_with_residuals",
        "completed_slices": [
            "FW1.S1_MULTI_PILOT_ALLOWLIST_AND_DAILY_RUNTIME_BASELINE",
            "FW2.S1_TEACHER_THROUGHPUT_AND_DAILY_REVIEW_BATCH",
            "FW3.S1_HUMAN_WRITEBACK_AND_LABEL_BACKFILL_CONTRACT",
            "FW4.S1_APPEND_ONLY_SCHEMA_CHECKPOINT_AND_ACCUMULATION_REFRESH",
            "FW5.S1_PHASE2_RERUN_AND_SUCCESSOR_DECISION",
        ],
        "recommended_successor": "ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_STABILITY_AND_VOLUME_RESIDUAL",
        "phase2_verdict": refresh.get("verdict"),
        "improvements": improvements,
        "residuals": residuals,
    }


def build_residual_phase2_recheck(
    volume_capacity: dict[str, Any],
    teacher_batch: dict[str, Any],
    schema_progress: dict[str, Any],
) -> dict[str, Any]:
    criteria = [
        {
            "criterion_id": "bounded_packet_supply_capacity",
            "status": "met" if volume_capacity.get("visible_maximum_reviewed_ceiling", 0) >= PHASE2_TARGETS["teacher_reviewed_count"] else "unmet",
            "rationale": (
                f"visible_maximum_reviewed_ceiling={volume_capacity.get('visible_maximum_reviewed_ceiling', 0)} "
                f"target={PHASE2_TARGETS['teacher_reviewed_count']}"
            ),
        },
        {
            "criterion_id": "reviewed_teacher_volume_growth",
            "status": "met"
            if teacher_batch.get("reviewed_count", 0) >= PHASE2_TARGETS["teacher_reviewed_count"]
            else "partial"
            if teacher_batch.get("reviewed_count", 0) > 3
            else "unmet",
            "rationale": (
                f"reviewed={teacher_batch.get('reviewed_count', 0)} "
                f"remaining={teacher_batch.get('remaining_to_phase2_target', 0)} "
                f"target={PHASE2_TARGETS['teacher_reviewed_count']}"
            ),
        },
        {
            "criterion_id": "schema_day_span_progress",
            "status": "met" if schema_progress.get("rerun_admissible_from_schema_gate") else "unmet",
            "rationale": (
                f"distinct_dates={schema_progress.get('distinct_observed_date_count', 0)} "
                f"elapsed_days={schema_progress.get('current_elapsed_days', 0)} "
                f"remaining_days={schema_progress.get('remaining_days_to_target', 0)}"
            ),
        },
    ]
    summary = {
        "met": sum(1 for item in criteria if item["status"] == "met"),
        "partial": sum(1 for item in criteria if item["status"] == "partial"),
        "unmet": sum(1 for item in criteria if item["status"] == "unmet"),
    }
    ready = all(item["status"] == "met" for item in criteria)
    return {
        "criteria": criteria,
        "summary": summary,
        "verdict": "rerun-review" if ready else "not-yet",
        "recommended_successor": "LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_RERUN"
        if ready
        else "ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_DAILY_VOLUME_AND_SCHEMA_RESIDUAL",
        "reason": "Reviewed volume and real schema day-span both still need daily accumulation before a rerun is honest."
        if not ready
        else "Reviewed volume and schema day-span both satisfy rerun gates.",
    }



def build_stability_volume_residual_closeout(
    volume_capacity: dict[str, Any],
    teacher_batch: dict[str, Any],
    writeback: dict[str, Any],
    schema_progress: dict[str, Any],
    recheck: dict[str, Any],
) -> dict[str, Any]:
    improvements = []
    if volume_capacity.get("visible_maximum_reviewed_ceiling", 0) >= PHASE2_TARGETS["teacher_reviewed_count"]:
        improvements.append("bounded packet supply can now theoretically clear the reviewed-volume gate")
    if teacher_batch.get("reviewed_count", 0) > 3 and teacher_batch.get("fallback_count", 0) == 0:
        improvements.append("reviewed teacher lane widened materially without introducing fallback")
    if writeback.get("fully_backfilled_count", 0) == len(writeback.get("target_packet_ids", [])) and writeback.get("target_packet_ids"):
        improvements.append("widened reviewed lane remains fully backfilled across outcome, training, and incident stores")
    if schema_progress.get("distinct_observed_date_count", 0) >= 1:
        improvements.append("schema gate is now interpreted through distinct-date progress instead of same-day snapshot count")

    residuals = []
    if teacher_batch.get("reviewed_count", 0) < PHASE2_TARGETS["teacher_reviewed_count"]:
        residuals.append("teacher volume still below phase-2 threshold")
    if schema_progress.get("current_elapsed_days", 0) < PHASE2_TARGETS["schema_stability_days"]:
        residuals.append("schema stability window still below 14 days")
    if recheck.get("verdict") != "rerun-review":
        residuals.append("phase-2 readiness remains not-yet after residual-family recheck")

    return {
        "family": "ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_STABILITY_AND_VOLUME_RESIDUAL",
        "family_verdict": "accept_with_residuals",
        "completed_slices": [
            "RW1.S1_REVIEW_VOLUME_CAPACITY_AND_DAILY_PROGRESS_BASELINE",
            "RW2A.S1_BOUNDED_PACKET_SUPPLY_EXPANSION_TO_CLEAR_VOLUME_GATE",
            "RW2B.S1_DAILY_REVIEW_APPEND_AND_GAP_BURNDOWN",
            "RW3.S1_MULTI_DAY_SCHEMA_PROGRESS_AND_DISTINCT_DATE_PROOF",
            "RW4.S1_PHASE2_RECHECK_AND_SUCCESSOR_DECISION",
        ],
        "recommended_successor": recheck.get("recommended_successor"),
        "phase2_verdict": recheck.get("verdict"),
        "improvements": improvements,
        "residuals": residuals,
    }


def render_phase2_refresh_markdown(refresh: dict[str, Any]) -> str:
    lines = ["# Data and Teacher Accumulation Phase-2 Refresh"]
    lines.extend(["", "## Criteria"])
    for item in refresh.get("criteria", []):
        lines.append(f"- `{item['criterion_id']}` => `{item['status']}` :: {item['rationale']}")
    lines.extend(["", "## Phase-2 Refresh Verdict"])
    lines.append(f"- verdict: `{refresh['verdict']}`")
    lines.append(f"- recommended successor: `{refresh['recommended_successor']}`")
    lines.append(f"- reason: {refresh['reason']}")
    return "\n".join(lines) + "\n"


def render_family_closeout_markdown(closeout: dict[str, Any]) -> str:
    lines = ["# Data and Teacher Accumulation Closeout"]
    lines.extend(["", "## Family Verdict"])
    lines.append(f"- family verdict: `{closeout['family_verdict']}`")
    lines.append(f"- phase-2 verdict: `{closeout['phase2_verdict']}`")
    lines.append(f"- recommended successor: `{closeout['recommended_successor']}`")
    lines.extend(["", "## Improvements"])
    for item in closeout.get("improvements", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Residuals"])
    for item in closeout.get("residuals", []):
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"
