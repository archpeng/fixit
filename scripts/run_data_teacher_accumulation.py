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
    build_followup_family_closeout,
    build_human_writeback_audit,
    build_phase2_refresh,
    build_replay_coverage,
    build_residual_phase2_recheck,
    build_runtime_baseline,
    build_schema_dayspan_progress,
    build_schema_stability_history,
    build_stability_volume_residual_closeout,
    build_target_ledger,
    build_teacher_accumulation_ledger,
    build_teacher_daily_review_batch,
    build_volume_capacity,
    render_accumulation_report,
    render_family_closeout_markdown,
    render_human_writeback_audit_markdown,
    render_phase2_refresh_markdown,
    render_runtime_baseline_markdown,
    render_schema_dayspan_progress_markdown,
    render_teacher_daily_review_batch_markdown,
    render_volume_capacity_markdown,
)


def main() -> None:
    reference_date = date.today()
    coverage = build_replay_coverage(REPO_ROOT)
    runtime = build_runtime_baseline(REPO_ROOT)
    baseline = build_accumulation_baseline(REPO_ROOT, reference_date=reference_date)
    targets = build_target_ledger(baseline)
    teacher_ledger = build_teacher_accumulation_ledger(REPO_ROOT)
    teacher_batch = build_teacher_daily_review_batch(REPO_ROOT)
    human_writeback = build_human_writeback_audit(REPO_ROOT)
    volume_capacity = build_volume_capacity(REPO_ROOT)
    schema_history = build_schema_stability_history(REPO_ROOT, reference_date=reference_date)
    schema_dayspan = build_schema_dayspan_progress(REPO_ROOT, reference_date=reference_date, schema_history=schema_history)
    phase2_refresh = build_phase2_refresh(REPO_ROOT, baseline, teacher_ledger, schema_history)
    residual_recheck = build_residual_phase2_recheck(volume_capacity, teacher_batch, schema_dayspan)
    closeout = build_family_closeout(baseline, teacher_ledger, schema_history, phase2_refresh)
    followup_closeout = build_followup_family_closeout(runtime, teacher_batch, human_writeback, schema_history, phase2_refresh)
    residual_closeout = build_stability_volume_residual_closeout(
        volume_capacity,
        teacher_batch,
        human_writeback,
        schema_dayspan,
        residual_recheck,
    )

    write_json(REPO_ROOT / "data/eval/data-teacher-replay-coverage.json", coverage)
    write_json(REPO_ROOT / "data/eval/data-teacher-runtime-baseline.json", runtime)
    write_json(REPO_ROOT / "data/eval/data-teacher-accumulation-baseline.json", baseline)
    write_json(REPO_ROOT / "data/eval/data-teacher-target-ledger.json", targets)
    write_json(REPO_ROOT / "data/eval/data-teacher-review-ledger.json", teacher_ledger)
    write_json(REPO_ROOT / "data/eval/data-teacher-daily-review-batch.json", teacher_batch)
    write_json(REPO_ROOT / "data/eval/data-teacher-human-writeback-audit.json", human_writeback)
    write_json(REPO_ROOT / "data/eval/data-teacher-volume-capacity.json", volume_capacity)
    write_json(REPO_ROOT / "data/eval/schema-stability-history.json", schema_history)
    write_json(REPO_ROOT / "data/eval/schema-dayspan-progress.json", schema_dayspan)
    write_json(REPO_ROOT / "data/eval/data-teacher-phase2-refresh.json", phase2_refresh)
    write_json(REPO_ROOT / "data/eval/data-teacher-residual-phase2-recheck.json", residual_recheck)
    write_json(REPO_ROOT / "data/eval/data-teacher-family-closeout.json", closeout)
    write_json(REPO_ROOT / "data/eval/data-teacher-followup-closeout.json", followup_closeout)
    write_json(REPO_ROOT / "data/eval/data-teacher-stability-volume-closeout.json", residual_closeout)
    write_text(REPO_ROOT / "data/eval/data-teacher-runtime-baseline.md", render_runtime_baseline_markdown(runtime))
    write_text(REPO_ROOT / "data/eval/data-teacher-daily-review-batch.md", render_teacher_daily_review_batch_markdown(teacher_batch))
    write_text(REPO_ROOT / "data/eval/data-teacher-human-writeback-audit.md", render_human_writeback_audit_markdown(human_writeback))
    write_text(REPO_ROOT / "data/eval/data-teacher-volume-capacity.md", render_volume_capacity_markdown(volume_capacity))
    write_text(REPO_ROOT / "data/eval/schema-dayspan-progress.md", render_schema_dayspan_progress_markdown(schema_dayspan))
    write_text(REPO_ROOT / "data/eval/data-teacher-accumulation-report.md", render_accumulation_report(baseline, targets))
    write_text(REPO_ROOT / "data/eval/data-teacher-phase2-refresh.md", render_phase2_refresh_markdown(phase2_refresh))
    write_text(REPO_ROOT / "data/eval/data-teacher-residual-phase2-recheck.md", render_phase2_refresh_markdown(residual_recheck))
    write_text(REPO_ROOT / "data/eval/data-teacher-family-closeout.md", render_family_closeout_markdown(closeout))
    write_text(REPO_ROOT / "data/eval/data-teacher-followup-closeout.md", render_family_closeout_markdown(followup_closeout))
    write_text(REPO_ROOT / "data/eval/data-teacher-stability-volume-closeout.md", render_family_closeout_markdown(residual_closeout))
    print("data and teacher accumulation artifacts refreshed")


if __name__ == "__main__":
    main()
