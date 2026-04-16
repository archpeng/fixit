from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from fixit_ai.common import read_jsonl, read_yaml


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _schema_stability_days(root: Path, reference_date: date) -> int:
    schema_root = root / "schemas"
    mtimes = [date.fromtimestamp(path.stat().st_mtime) for path in schema_root.glob("*.json")]
    latest = max(mtimes)
    return max((reference_date - latest).days, 0)


def build_readiness_rubric() -> dict[str, Any]:
    return {
        "criteria": [
            {
                "criterion_id": "schema_stability_2_to_4_weeks",
                "question": "Has the packet/schema surface remained stable long enough to justify a local model implementation cycle?",
                "go_bar": "schema stability >= 14 days and no active schema churn family",
            },
            {
                "criterion_id": "teacher_judgement_volume_sufficient",
                "question": "Is there enough reviewed teacher/human judgement volume to support distillation or tuning?",
                "go_bar": "reviewed teacher cases >= 10 and fallback ratio <= 0.2 on the bounded review lane",
            },
            {
                "criterion_id": "baseline_recall_ceiling_clear",
                "question": "Do replay/calibration artifacts show where the current baseline plateaus?",
                "go_bar": "expanded replay coverage, calibration artifact, and clear remaining recall/precision pain",
            },
            {
                "criterion_id": "hard_cases_are_small_model_worthy",
                "question": "Are the remaining hard cases primarily semantic understanding problems rather than review/data gaps?",
                "go_bar": "semantic-failure count exceeds review-gap count and affects important severe cases",
            },
            {
                "criterion_id": "local_budget_latency_and_rollback_ready",
                "question": "Are budget, latency, deployment, and rollback constraints explicit enough for implementation?",
                "go_bar": "budget defined, latency bar defined, rollback path defined, offline/online success bar frozen",
            },
        ],
        "verdict_standards": {
            "go": "All criteria met, or only non-blocking partial items remain.",
            "not-yet": "Direction still looks plausible, but one or more blocking readiness criteria remain unmet.",
            "no-go": "Current evidence suggests small-model implementation is not the right next move or ROI is not justified.",
        },
        "non_goals": [
            "training a local small model in this family",
            "replacing the baseline student during review",
            "production auto-action enablement",
        ],
    }


def build_evidence_ledger(root: Path | str, reference_date: date | None = None) -> dict[str, Any]:
    root = Path(root)
    reference_date = reference_date or date.today()

    manifest = _load_json(root / "data/samples/replay-pack-manifest.json")
    label_ledger = _load_json(root / "data/eval/label-ledger.json")
    calibration = _load_json(root / "data/eval/calibration-report.json")
    teacher_summary = _load_json(root / "data/eval/teacher-queue-summary.json")
    live_readback = _load_json(root / "data/eval/control-plane-live-readback.json")
    metrics = _load_json(root / "data/eval/metrics-summary.json")
    services = read_yaml(root / "configs/services.yaml")

    return {
        "reference_date": reference_date.isoformat(),
        "schema_stability_days": _schema_stability_days(root, reference_date),
        "pilot_service_count": 1 if services.get("pilot_family", {}).get("service") else 0,
        "replay_dataset_count": len(manifest.get("datasets", [])),
        "replay_generated_at": manifest.get("generated_at"),
        "teacher_reviewed_count": teacher_summary.get("reviewed_count", 0),
        "teacher_fallback_count": teacher_summary.get("fallback_count", 0),
        "teacher_selected_count": teacher_summary.get("selected_count", 0),
        "outcome_total": label_ledger.get("outcome_total", 0),
        "outcome_severe_total": label_ledger.get("outcome_severe_total", 0),
        "label_sources": label_ledger.get("counts_by_source", {}),
        "calibration_bucket_count": len(calibration.get("bucket_summary", [])),
        "threshold_review_action": calibration.get("threshold_review", {}).get("recommended_action"),
        "severe_recall": metrics.get("severe_recall", 0.0),
        "top_k_precision": metrics.get("top_k_precision", 0.0),
        "teacher_escalation_rate": metrics.get("teacher_escalation_rate", 0.0),
        "missed_severe_count": metrics.get("missed_severe_count", 0),
        "control_plane_live_ok": bool(live_readback.get("health_ok")),
        "control_plane_service_entry_found": bool(live_readback.get("service_entry_found")),
        "control_plane_fallback_expected": bool(live_readback.get("fallback_expected")),
        "local_budget_defined": False,
        "latency_budget_defined": False,
        "rollback_plan_defined": False,
        "evidence_paths": [
            "data/samples/replay-pack-manifest.json",
            "data/eval/label-ledger.json",
            "data/eval/calibration-report.json",
            "data/eval/teacher-queue-summary.json",
            "data/eval/control-plane-live-readback.json",
            "data/eval/metrics-summary.json",
        ],
    }


def build_hard_case_taxonomy(root: Path | str) -> dict[str, Any]:
    root = Path(root)
    metrics = _load_json(root / "data/eval/metrics-summary.json")
    shadow_report = _load_json(root / "data/reports/daily-shadow-report.json")
    fallbacks = read_jsonl(root / "data/eval/teacher-fallback-ledger.jsonl")
    reviews = read_jsonl(root / "data/eval/teacher-review-ledger.jsonl")
    decisions = read_jsonl(root / "data/eval/triage-decisions.jsonl")

    review_gap_count = len(fallbacks)
    reviewed_hard_case_count = len(reviews)
    semantic_failure_count = int(metrics.get("missed_severe_count", 0))
    high_rank_rule_missed = len(shadow_report.get("rule_missed_high_ranked", []))
    send_to_review = sum(1 for item in decisions if item.get("final_action") == "send_to_human_review")

    dominant_gap = "review_gap" if review_gap_count >= semantic_failure_count else "semantic_gap"
    return {
        "review_gap_count": review_gap_count,
        "reviewed_hard_case_count": reviewed_hard_case_count,
        "semantic_failure_count": semantic_failure_count,
        "high_rank_rule_missed_count": high_rank_rule_missed,
        "send_to_human_review_count": send_to_review,
        "dominant_gap": dominant_gap,
        "small_model_worthy_today": semantic_failure_count > review_gap_count and semantic_failure_count > 0,
        "notes": [
            "Current severe misses are zero; remaining hard cases are mostly review-gap and fallback driven.",
            "High-novelty rule-missed packets still reach high priority through the current baseline plus teacher/fallback flow.",
        ],
    }


def build_deployment_review(evidence: dict[str, Any]) -> dict[str, Any]:
    ready = all(
        [
            evidence.get("local_budget_defined"),
            evidence.get("latency_budget_defined"),
            evidence.get("rollback_plan_defined"),
        ]
    )
    return {
        "budget_defined": evidence.get("local_budget_defined", False),
        "latency_budget_defined": evidence.get("latency_budget_defined", False),
        "rollback_plan_defined": evidence.get("rollback_plan_defined", False),
        "deployment_readiness": "ready" if ready else "not_ready",
        "blocking_reasons": [
            reason
            for flag, reason in [
                (evidence.get("local_budget_defined", False), "local model budget not frozen"),
                (evidence.get("latency_budget_defined", False), "latency budget not frozen"),
                (evidence.get("rollback_plan_defined", False), "rollback plan not frozen"),
            ]
            if not flag
        ],
    }


def audit_phase2_conditions(
    rubric: dict[str, Any],
    evidence: dict[str, Any],
    hard_cases: dict[str, Any],
    deployment: dict[str, Any],
) -> dict[str, Any]:
    criteria = []
    for criterion in rubric["criteria"]:
        cid = criterion["criterion_id"]
        status = "partial"
        rationale = "needs review"
        if cid == "schema_stability_2_to_4_weeks":
            if evidence["schema_stability_days"] >= 14:
                status = "met"
                rationale = f"schema stability days={evidence['schema_stability_days']}"
            else:
                status = "unmet"
                rationale = f"schema stability days={evidence['schema_stability_days']} < 14"
        elif cid == "teacher_judgement_volume_sufficient":
            if evidence["teacher_reviewed_count"] >= 10 and (evidence["teacher_fallback_count"] / max(evidence["teacher_selected_count"], 1)) <= 0.2:
                status = "met"
                rationale = "reviewed teacher volume and fallback ratio are sufficient"
            else:
                status = "unmet"
                rationale = f"reviewed={evidence['teacher_reviewed_count']} fallback={evidence['teacher_fallback_count']} selected={evidence['teacher_selected_count']}"
        elif cid == "baseline_recall_ceiling_clear":
            if evidence["replay_dataset_count"] >= 9 and evidence["calibration_bucket_count"] >= 4 and evidence["pilot_service_count"] == 1:
                status = "partial"
                rationale = "expanded replay and calibration exist, but evidence remains single-pilot"
            elif evidence["replay_dataset_count"] >= 9 and evidence["calibration_bucket_count"] >= 4 and evidence["pilot_service_count"] > 1:
                status = "met"
                rationale = "expanded replay and calibration cover multiple pilots"
            else:
                status = "unmet"
                rationale = "replay/calibration evidence is too thin"
        elif cid == "hard_cases_are_small_model_worthy":
            if hard_cases["small_model_worthy_today"]:
                status = "met"
                rationale = "semantic failures dominate remaining hard cases"
            else:
                status = "unmet"
                rationale = f"dominant_gap={hard_cases['dominant_gap']} semantic_failure_count={hard_cases['semantic_failure_count']}"
        elif cid == "local_budget_latency_and_rollback_ready":
            if deployment["deployment_readiness"] == "ready":
                status = "met"
                rationale = "budget, latency, and rollback constraints are explicit"
            else:
                status = "unmet"
                rationale = "; ".join(deployment["blocking_reasons"])
        criteria.append({
            "criterion_id": cid,
            "status": status,
            "rationale": rationale,
        })

    summary = {
        "met": sum(1 for item in criteria if item["status"] == "met"),
        "partial": sum(1 for item in criteria if item["status"] == "partial"),
        "unmet": sum(1 for item in criteria if item["status"] == "unmet"),
    }
    return {"criteria": criteria, "summary": summary}


def build_model_option_matrix(evidence: dict[str, Any], hard_cases: dict[str, Any]) -> dict[str, Any]:
    options = [
        {
            "option_id": "keep_classic_baseline",
            "fit": "Current baseline already achieves severe_recall=1.0 on the bounded pilot and remaining hard cases are dominated by review/data gaps.",
            "operational_risk": "low",
            "recommendation": "preferred_now",
        },
        {
            "option_id": "small_encoder_classifier",
            "fit": "Future candidate if replay coverage and reviewed teacher volume materially increase.",
            "operational_risk": "medium",
            "recommendation": "future_candidate",
        },
        {
            "option_id": "small_instruct_reranker",
            "fit": "Would add deployment and latency complexity before the repo has enough evidence that semantic failures dominate.",
            "operational_risk": "high",
            "recommendation": "defer",
        },
    ]
    preferred_current_path = "keep_baseline_and_accumulate_data"
    if hard_cases["small_model_worthy_today"] and evidence["teacher_reviewed_count"] >= 10:
        preferred_current_path = "small_encoder_first"
    return {"options": options, "preferred_current_path": preferred_current_path}


def build_guardrail_bars(evidence: dict[str, Any], option_matrix: dict[str, Any], deployment: dict[str, Any]) -> dict[str, Any]:
    success_bar = {
        "offline_recall_floor": evidence.get("severe_recall", 0.0),
        "top_k_precision_floor": max(0.95, evidence.get("top_k_precision", 0.0)),
        "teacher_escalation_ceiling": max(0.15, evidence.get("teacher_escalation_rate", 0.0)),
        "note": "Implementation family may only proceed if it can beat or match the current bounded replay baseline without widening fallback load.",
    }
    rollback_bar = {
        "recall_drop_trigger": evidence.get("severe_recall", 0.0),
        "precision_drop_trigger": max(0.90, evidence.get("top_k_precision", 0.0) - 0.05),
        "fallback_rate_ceiling": max(evidence.get("teacher_fallback_count", 0) / max(evidence.get("teacher_selected_count", 1), 1), 0.25),
        "latency_budget_defined": deployment.get("latency_budget_defined", False),
    }
    return {"success_bar": success_bar, "rollback_bar": rollback_bar}


def build_final_verdict(audit: dict[str, Any], option_matrix: dict[str, Any], deployment: dict[str, Any]) -> dict[str, Any]:
    unmet = audit["summary"]["unmet"]
    if unmet == 0 and option_matrix["preferred_current_path"] == "small_encoder_first" and deployment["deployment_readiness"] == "ready":
        verdict = "go"
        successor = "LOCAL_SMALL_MODEL_STUDENT_IMPLEMENTATION"
        reason = "Readiness criteria are satisfied and a bounded first implementation path is clear."
    elif option_matrix["preferred_current_path"] == "keep_baseline_and_accumulate_data":
        verdict = "not-yet"
        successor = "ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION"
        reason = "Current blockers are still dominated by replay breadth, teacher volume, and review-gap evidence rather than semantic model failure."
    else:
        verdict = "no-go"
        successor = "KEEP_BASELINE_STUDENT_AND_CONTINUE_HARDENING"
        reason = "Current evidence does not justify local small model ROI."
    return {"verdict": verdict, "recommended_successor": successor, "reason": reason}


def render_review_markdown(
    rubric: dict[str, Any],
    evidence: dict[str, Any],
    audit: dict[str, Any],
    hard_cases: dict[str, Any],
    option_matrix: dict[str, Any],
    deployment: dict[str, Any],
    verdict: dict[str, Any],
    bars: dict[str, Any],
) -> str:
    lines = [
        "# Local Small Model Student Upgrade Review",
        "",
        "## Readiness Rubric",
    ]
    for item in rubric["criteria"]:
        lines.append(f"- `{item['criterion_id']}`: {item['question']}")
    lines.extend(["", "## Evidence Ledger"])
    lines.extend([
        f"- schema stability days: `{evidence['schema_stability_days']}`",
        f"- replay dataset count: `{evidence['replay_dataset_count']}`",
        f"- teacher reviewed count: `{evidence['teacher_reviewed_count']}`",
        f"- teacher fallback count: `{evidence['teacher_fallback_count']}`",
        f"- outcome total: `{evidence['outcome_total']}`",
        f"- severe recall: `{evidence['severe_recall']}`",
        f"- top-K precision: `{evidence['top_k_precision']}`",
    ])
    lines.extend(["", "## Phase-2 Condition Audit"])
    for item in audit["criteria"]:
        lines.append(f"- `{item['criterion_id']}` => `{item['status']}` :: {item['rationale']}")
    lines.extend(["", "## Hard-case Taxonomy"])
    lines.extend([
        f"- review gap count: `{hard_cases['review_gap_count']}`",
        f"- semantic failure count: `{hard_cases['semantic_failure_count']}`",
        f"- dominant gap: `{hard_cases['dominant_gap']}`",
    ])
    lines.extend(["", "## Model Option Matrix"])
    for item in option_matrix["options"]:
        lines.append(f"- `{item['option_id']}` `{item['recommendation']}` risk=`{item['operational_risk']}` :: {item['fit']}")
    lines.extend(["", "## Deployment and Guardrails"])
    lines.append(f"- deployment readiness: `{deployment['deployment_readiness']}`")
    for reason in deployment["blocking_reasons"]:
        lines.append(f"- blocker: {reason}")
    lines.extend(["", "## Acceptance and Rollback Bars"])
    lines.append(f"- success recall floor: `{bars['success_bar']['offline_recall_floor']}`")
    lines.append(f"- success top-K precision floor: `{bars['success_bar']['top_k_precision_floor']}`")
    lines.append(f"- success teacher escalation ceiling: `{bars['success_bar']['teacher_escalation_ceiling']}`")
    lines.append(f"- rollback recall trigger: `{bars['rollback_bar']['recall_drop_trigger']}`")
    lines.append(f"- rollback precision trigger: `{bars['rollback_bar']['precision_drop_trigger']}`")
    lines.append(f"- rollback fallback rate ceiling: `{bars['rollback_bar']['fallback_rate_ceiling']}`")
    lines.extend(["", "## Final Verdict"])
    lines.append(f"- verdict: `{verdict['verdict']}`")
    lines.append(f"- recommended successor: `{verdict['recommended_successor']}`")
    lines.append(f"- reason: {verdict['reason']}")
    lines.append("")
    return "\n".join(lines)
