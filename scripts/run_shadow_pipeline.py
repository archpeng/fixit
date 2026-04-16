#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

STEPS = [
    [sys.executable, str(REPO_ROOT / "scripts/generate_candidate_windows.py")],
    [sys.executable, str(REPO_ROOT / "scripts/build_packets.py")],
    [sys.executable, str(REPO_ROOT / "scripts/run_retrieval.py")],
    [sys.executable, str(REPO_ROOT / "scripts/train_student.py")],
    [sys.executable, str(REPO_ROOT / "scripts/run_teacher_review.py")],
    [sys.executable, str(REPO_ROOT / "scripts/evaluate_shadow.py")],
    [sys.executable, str(REPO_ROOT / "scripts/generate_shadow_report.py")],
]


def main() -> None:
    for step in STEPS:
        subprocess.run(step, cwd=REPO_ROOT, check=True)
    print("shadow pipeline completed")


if __name__ == "__main__":
    main()
