# ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_DAILY_VOLUME_AND_SCHEMA_RESIDUAL_WORKSET

- Family: `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_DAILY_VOLUME_AND_SCHEMA_RESIDUAL`
- Workstream: `DV1_REMAINING_REVIEW_VOLUME_TO_TEN` -> `DV3_DAILY_RECHECK_AND_SUCCESSOR_DECISION`
- Active slice count: `1`
- Active slice: `DV1.S1_REMAINING_BOUNDED_PACKET_REVIEW_APPEND_TO_TEN`
- Control rule: one active slice only; do not start `DV2` or `DV3` before `DV1` closes with honest reviewed-volume truth

---

## 1. Active Slice Card

### Slice ID

`DV1.S1_REMAINING_BOUNDED_PACKET_REVIEW_APPEND_TO_TEN`

### Type

`data + artifact + test + review`

### Goal

在当前 bounded packet pool 内，把 remaining `3` reviewed gap 压成真实落地结果，或者诚实证明当前 pool 仍然无法继续而不作弊。

### Primary surfaces

- `configs/teacher-budget.yaml`
- `data/eval/manual_teacher_judgements.jsonl`
- `data/eval/fixtures/teacher_review_batch.retained.jsonl`
- `data/eval/outcomes.jsonl`
- `data/eval/training_examples.jsonl`
- `data/eval/historical_incidents.jsonl`
- `fixit_ai/data_teacher_accumulation.py`
- `scripts/run_hardening_pipeline.py`
- `scripts/run_data_teacher_accumulation.py`
- `tests/test_data_teacher_accumulation.py`
- `tests/test_hardening_pipeline.py`
- `data/eval/data-teacher-daily-review-batch.json`
- `data/eval/data-teacher-review-ledger.json`
- `data/eval/data-teacher-human-writeback-audit.json`

### Target deliverable

- reviewed teacher count reaches `10`, or explicit proof that the current bounded pool cannot close the gap honestly
- widened reviewed lane remains fully backfilled
- updated burn-down truth for the remaining gap

### Expected verification

1. fail-first targeted unittest covering remaining reviewed-gap append
2. `python3 -m unittest tests.test_hardening_pipeline tests.test_data_teacher_accumulation -v`
3. `python3 scripts/run_hardening_pipeline.py`
4. `python3 scripts/run_data_teacher_accumulation.py`
5. artifact readback proves reviewed-volume outcome for the remaining `3` packets
6. `python3 -m unittest discover -s tests -v`
7. `STATUS/WORKSET` updated with the singular next slice

### Done when

- reviewed teacher count is `10`, or the current bounded pool is proven insufficient without cheating
- widened reviewed lane does not introduce new write-back gaps
- next slice is singular and evidence-backed

### Stop if

- closing the remaining gap requires synthetic / unprovenanced review
- closing the remaining gap requires unbounded scope expansion
- write-back regression cannot be closed in-scope
- multiple equally-primary next slices remain after the append attempt

### Handoff after close

- if reviewed count reaches `10` -> `DV2.S1_NEXT_DISTINCT_DATE_SCHEMA_PROGRESS_CHECKPOINT`
- else -> `plan-creator` or user decision

---

## 2. Planned Queue

| Slice ID | Type | Target output | Verification | Status |
|---|---|---|---|---|
| `DV1.S1_REMAINING_BOUNDED_PACKET_REVIEW_APPEND_TO_TEN` | data+artifact+test+review | close the remaining `3` reviewed gap or prove why not | targeted unittest + hardening pipeline + accumulation rerun + full regression | active |
| `DV2.S1_NEXT_DISTINCT_DATE_SCHEMA_PROGRESS_CHECKPOINT` | artifact+daily-proof | next real-date schema checkpoint and updated remaining-days truth | targeted unittest/proof + accumulation rerun + full regression | queued |
| `DV3.S1_DAILY_RECHECK_AND_SUCCESSOR_DECISION` | review+closeout | refreshed daily recheck + rerun admission or next residual successor | evidence audit + full unittest discover + plan closeout writeback | queued |

---

## 3. Control Notes

- 本 workset 默认不并行执行多个 slices。
- `DV1` 之前不跳到 `DV2` / `DV3`。
- `DV2` 之前不把 same-day snapshot_count 当成 elapsed days。
- `DV3` 之前不重开 small-model review，也不进入 implementation。

---

## 4. Residual Seed Pool

当前 residual seed：

- `teacher_reviewed_count: 7 -> 10`
- `remaining_review_gap: 3`
- `visible_unreviewed_packet_ids: ['ipk_w001', 'ipk_w005', 'ipk_w009']`
- `schema_stability_days: 0 -> 14`
- `distinct_observed_schema_dates: 1`
- `phase2_verdict: not-yet`
- `runtime scope: bounded multi-pilot allowlist` (must stay bounded)
