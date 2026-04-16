from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any

from fixit_ai.common import read_jsonl

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


def build_accumulation_baseline(root: Path | str, reference_date: date | None = None) -> dict[str, Any]:
    root = Path(root)
    reference_date = reference_date or date.today()

    manifest = _load_json(root / "data/samples/replay-pack-manifest.json")
    teacher_summary = _load_json(root / "data/eval/teacher-queue-summary.json")
    label_ledger = _load_json(root / "data/eval/label-ledger.json")
    calibration = _load_json(root / "data/eval/calibration-report.json")
    evidence_ledger = _load_json(root / "data/eval/local-small-model-evidence-ledger.json")
    phase2_audit = _load_json(root / "data/eval/local-small-model-phase2-audit.json")
    final_verdict = _load_json(root / "data/eval/local-small-model-final-verdict.json")
    coverage = build_replay_coverage(root)

    teacher_requests = read_jsonl(root / "data/eval/teacher-request-ledger.jsonl")
    teacher_reviews = read_jsonl(root / "data/eval/teacher-review-ledger.jsonl")
    teacher_fallbacks = read_jsonl(root / "data/eval/teacher-fallback-ledger.jsonl")

    teacher_selected_count = teacher_summary.get("selected_count", len(teacher_requests))
    teacher_reviewed_count = len(teacher_reviews)
    teacher_fallback_count = len(teacher_fallbacks)
    teacher_fallback_ratio = round(teacher_fallback_count / max(teacher_selected_count, 1), 4)
    replay_output_row_total = sum(item.get("output_row_count", 0) for item in manifest.get("datasets", []))

    queue_summary_consistent = (
        teacher_summary.get("selected_count", 0) == len(teacher_requests)
        and teacher_summary.get("reviewed_count", 0) == teacher_reviewed_count
        and teacher_summary.get("fallback_count", 0) == teacher_fallback_count
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

    current_reviewed_count = len(retained_reviews)
    predecessor_reviewed_count = predecessor.get("teacher_reviewed_count", 0)
    current_packet_ids = sorted(item.get("packet_id") for item in retained_reviews if item.get("packet_id"))
    label_teacher_rubric_count = label_ledger.get("counts_by_source", {}).get("teacher_rubric", 0)

    return {
        "predecessor_teacher_reviewed_count": predecessor_reviewed_count,
        "current_teacher_reviewed_count": current_reviewed_count,
        "teacher_reviewed_delta": current_reviewed_count - predecessor_reviewed_count,
        "current_teacher_packet_ids": current_packet_ids,
        "label_teacher_rubric_count": label_teacher_rubric_count,
        "teacher_label_gap": max(current_reviewed_count - label_teacher_rubric_count, 0),
        "retained_review_batch_path": TEACHER_BATCH_PATH,
    }


def _schema_fingerprint(schema_root: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    schema_files = sorted(schema_root.glob("*.json"))
    for path in schema_files:
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest(), len(schema_files)


def build_schema_stability_history(root: Path | str, reference_date: date | None = None) -> dict[str, Any]:
    root = Path(root)
    reference_date = reference_date or date.today()
    schema_root = root / "schemas"
    fingerprint, schema_file_count = _schema_fingerprint(schema_root)
    latest_mtime = max(date.fromtimestamp(path.stat().st_mtime) for path in schema_root.glob("*.json"))
    return {
        "reference_date": reference_date.isoformat(),
        "schema_file_count": schema_file_count,
        "current_fingerprint": fingerprint,
        "current_elapsed_days": max((reference_date - latest_mtime).days, 0),
        "snapshots": [
            {
                "date": reference_date.isoformat(),
                "fingerprint": fingerprint,
            }
        ],
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
