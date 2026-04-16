#!/usr/bin/env python3
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fixit_ai.common import write_json, write_text
from fixit_ai.data_teacher_accumulation import (
    build_accumulation_baseline,
    build_family_closeout,
    build_phase2_refresh,
    build_replay_coverage,
    build_schema_stability_history,
    build_target_ledger,
    build_teacher_accumulation_ledger,
    render_accumulation_report,
    render_family_closeout_markdown,
    render_phase2_refresh_markdown,
)


def main() -> None:
    reference_date = date.today()
    coverage = build_replay_coverage(REPO_ROOT)
    baseline = build_accumulation_baseline(REPO_ROOT, reference_date=reference_date)
    targets = build_target_ledger(baseline)
    teacher_ledger = build_teacher_accumulation_ledger(REPO_ROOT)
    schema_history = build_schema_stability_history(REPO_ROOT, reference_date=reference_date)
    phase2_refresh = build_phase2_refresh(REPO_ROOT, baseline, teacher_ledger, schema_history)
    closeout = build_family_closeout(baseline, teacher_ledger, schema_history, phase2_refresh)

    write_json(REPO_ROOT / "data/eval/data-teacher-replay-coverage.json", coverage)
    write_json(REPO_ROOT / "data/eval/data-teacher-accumulation-baseline.json", baseline)
    write_json(REPO_ROOT / "data/eval/data-teacher-target-ledger.json", targets)
    write_json(REPO_ROOT / "data/eval/data-teacher-review-ledger.json", teacher_ledger)
    write_json(REPO_ROOT / "data/eval/schema-stability-history.json", schema_history)
    write_json(REPO_ROOT / "data/eval/data-teacher-phase2-refresh.json", phase2_refresh)
    write_json(REPO_ROOT / "data/eval/data-teacher-family-closeout.json", closeout)
    write_text(REPO_ROOT / "data/eval/data-teacher-accumulation-report.md", render_accumulation_report(baseline, targets))
    write_text(REPO_ROOT / "data/eval/data-teacher-phase2-refresh.md", render_phase2_refresh_markdown(phase2_refresh))
    write_text(REPO_ROOT / "data/eval/data-teacher-family-closeout.md", render_family_closeout_markdown(closeout))
    print("data and teacher accumulation artifacts refreshed")


if __name__ == "__main__":
    main()
