#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

STEPS = [
    [sys.executable, str(REPO_ROOT / "scripts/refresh_replay_pack.py")],
    [
        sys.executable,
        str(REPO_ROOT / "scripts/generate_candidate_windows.py"),
        "--input",
        str(REPO_ROOT / "data/samples/replay/metrics_windows.jsonl"),
    ],
    [sys.executable, str(REPO_ROOT / "scripts/check_control_plane_live_availability.py")],
    [
        sys.executable,
        str(REPO_ROOT / "scripts/build_packets.py"),
        "--candidates",
        str(REPO_ROOT / "data/samples/candidate-windows.jsonl"),
        "--logs",
        str(REPO_ROOT / "data/samples/replay/log_evidence.jsonl"),
        "--traces",
        str(REPO_ROOT / "data/samples/replay/trace_evidence.jsonl"),
        "--topology",
        str(REPO_ROOT / "data/samples/replay/topology.jsonl"),
        "--memory",
        str(REPO_ROOT / "data/samples/replay/memory_summaries.jsonl"),
        "--services-config",
        str(REPO_ROOT / "configs/services.yaml"),
        "--live-enrichment",
        str(REPO_ROOT / "data/live/control_plane_service_context.jsonl"),
        "--enrichment-usage",
        str(REPO_ROOT / "data/eval/enrichment-usage.json"),
    ],
    [sys.executable, str(REPO_ROOT / "scripts/build_retrieval_index.py")],
    [
        sys.executable,
        str(REPO_ROOT / "scripts/run_retrieval.py"),
        "--history",
        str(REPO_ROOT / "data/eval/replay/historical_incidents.jsonl"),
        "--index",
        str(REPO_ROOT / "data/eval/retrieval-index.json"),
    ],
    [
        sys.executable,
        str(REPO_ROOT / "scripts/train_student.py"),
        "--training",
        str(REPO_ROOT / "data/eval/replay/training_examples.jsonl"),
    ],
    [sys.executable, str(REPO_ROOT / "scripts/build_label_ledger.py")],
    [
        sys.executable,
        str(REPO_ROOT / "scripts/run_teacher_review.py"),
        "--seed-judgements",
        str(REPO_ROOT / "data/eval/replay/manual_teacher_judgements.jsonl"),
    ],
    [
        sys.executable,
        str(REPO_ROOT / "scripts/evaluate_shadow.py"),
        "--outcomes",
        str(REPO_ROOT / "data/eval/replay/outcomes.jsonl"),
        "--teacher-fallbacks",
        str(REPO_ROOT / "data/eval/teacher-fallback-ledger.jsonl"),
    ],
    [
        sys.executable,
        str(REPO_ROOT / "scripts/build_calibration_report.py"),
    ],
    [sys.executable, str(REPO_ROOT / "scripts/refresh_replay_pack.py")],
    [
        sys.executable,
        str(REPO_ROOT / "scripts/generate_shadow_report.py"),
        "--outcomes",
        str(REPO_ROOT / "data/eval/replay/outcomes.jsonl"),
        "--manifest",
        str(REPO_ROOT / "data/samples/replay-pack-manifest.json"),
        "--enrichment-usage",
        str(REPO_ROOT / "data/eval/enrichment-usage.json"),
        "--teacher-summary",
        str(REPO_ROOT / "data/eval/teacher-queue-summary.json"),
    ],
]


def main() -> None:
    for step in STEPS:
        subprocess.run(step, cwd=REPO_ROOT, check=True)
    print("hardening pipeline completed")


if __name__ == "__main__":
    main()
