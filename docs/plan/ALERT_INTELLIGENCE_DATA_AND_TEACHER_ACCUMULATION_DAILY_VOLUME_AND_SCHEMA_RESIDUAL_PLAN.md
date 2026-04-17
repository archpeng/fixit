# ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_DAILY_VOLUME_AND_SCHEMA_RESIDUAL_PLAN

- Status: active
- Family: `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_DAILY_VOLUME_AND_SCHEMA_RESIDUAL`
- Created: 2026-04-16
- Plan type: repo-global daily residual execution pack
- Primary handoff: `execute-plan`
- Predecessor family:
  - `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_STABILITY_AND_VOLUME_RESIDUAL`
- Source anchors:
  - `docs/architecture/alert-intelligence-architecture.md`
  - `docs/mvp/alert-intelligence-mvp.md`
  - `docs/architecture/fixit-next-stage-recommended-runtime-architecture.md`
  - `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_STABILITY_AND_VOLUME_RESIDUAL_CLOSEOUT_REVIEW.md`
  - `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_STABILITY_AND_VOLUME_RESIDUAL_SUCCESSOR_ADMISSION.md`
  - `data/eval/data-teacher-residual-phase2-recheck.json`
  - `data/eval/data-teacher-volume-capacity.json`
  - `data/eval/data-teacher-daily-review-batch.json`
  - `data/eval/schema-dayspan-progress.json`
  - `AGENTS.md`

---

## 1. Goal

把当前 residual truth 继续压成 **daily** execution family，而不是继续做同日结构性重构。

本 family 的唯一主目标是：

1. 把 reviewed teacher count 从 `7` 推到 phase-2 floor `10`
2. 让 schema gate 按真实 distinct dates / elapsed days 日更累计
3. 在真实时间推进下，持续重跑 daily recheck，直到：
   - 要么诚实 admit `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_RERUN`
   - 要么再次 honest closeout 并给出新的 residual successor

边界是：

> 当前 family 不是继续补 runtime 形态，而是围绕现有 bounded runtime 做 daily reviewed-volume burndown 与 schema day-span accumulation。

---

## 2. Scope

### 2.1 In scope

- remaining reviewed-volume gap `7 -> 10`
- current bounded unreviewed packet set consumption
- provenance-preserving teacher append for remaining bounded packets
- widened lane write-back continuity checks
- daily schema checkpoint / distinct-date progress readback
- daily phase-2 recheck and successor routing
- family closeout with honest rerun admission or residual carry-forward

### 2.2 Out of scope

- unbounded runtime expansion
- new multi-pilot scope growth beyond current allowlist
- local small model rerun before gates pass
- local small model implementation
- fake timestamps / backdating / synthetic schema days
- synthetic teacher labels without provenance

---

## 3. Entry Criteria

以下前置已满足：

- predecessor `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_STABILITY_AND_VOLUME_RESIDUAL` 已 closeout
- predecessor verdict = `accept_with_residuals`
- predecessor successor admission = `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_DAILY_VOLUME_AND_SCHEMA_RESIDUAL`
- 当前 bounded runtime / write-back truth 已冻结：
  - runtime allowlist count = `2`
  - current packet count = `10`
  - current reviewed teacher count = `7`
  - current fallback count = `0`
  - teacher label gap = `0`
  - widened reviewed lane fully backfilled count = `7`
  - visible unreviewed remainder = `3`
  - visible unreviewed packet ids = `['ipk_w001', 'ipk_w005', 'ipk_w009']`
  - visible maximum reviewed ceiling = `10`
  - distinct observed schema dates = `1`
  - current elapsed schema days = `0`
  - remaining schema days to target = `14`
  - residual-family recheck verdict = `not-yet`
- 当前结构性真相已经足够清楚：
  - 同日继续改架构，已经不是主要收益来源
  - 主要收益来自 bounded daily append + real day progression

---

## 4. Family Exit Criteria

当以下条件满足其一时，本 family 可 closeout：

### A. Rerun-ready closeout

1. reviewed teacher count `>= 10`
2. schema stability elapsed days `>= 14`
3. daily recheck no longer returns `not-yet`
4. `PLAN/STATUS/WORKSET` 已写回 rerun admission truth

### B. Honest residual closeout

1. remaining bounded reviewed-volume burndown path has been executed honestly
2. schema day-span progress has been tracked through real dates, not same-day snapshot inflation
3. daily recheck still says `not-yet`, and reasons are script-backed
4. successor routing is explicit and bounded

说明：

- 本 family 不承诺一定把 verdict 推到 rerun-admissible
- 但必须把剩余 `3` 个 reviewed gap 与 schema real-day accumulation 路径压成 honest daily truth

---

## 5. Workstreams

| Workstream | Objective | Main deliverables | Close gate |
|---|---|---|---|
| `DV1_REMAINING_REVIEW_VOLUME_TO_TEN` | 先在当前 bounded packet pool 内消化剩余 reviewed gap | widened reviewed lane, refreshed ledgers, refreshed write-back audit | reviewed teacher count reaches `10` or current pool is proven insufficient without cheating |
| `DV2_DAILY_SCHEMA_DAYSPAN_ACCUMULATION` | 只按真实 distinct dates 累积 schema stability | refreshed schema day-span progress, daily checkpoint truth | schema progress is day-based and replayable |
| `DV3_DAILY_RECHECK_AND_SUCCESSOR_DECISION` | 按新的 daily truth 决定 rerun 或继续 residual | refreshed daily recheck, closeout review, successor admission | honest next step is frozen |

---

## 6. Verification Ladder

### Layer A — active-slice proof

每个 slice 至少要有：

- fail-first targeted test or proof surface
- script-refreshable artifact
- `STATUS/WORKSET` writeback

### Layer B — serial refresh proof

每个 accepted slice 默认串行刷新：

1. targeted unittest
2. `python3 scripts/run_hardening_pipeline.py`（若 slice 触达 teacher/review/runtime truth）
3. `python3 scripts/run_data_teacher_accumulation.py`
4. artifact readback

### Layer C — family proof

每个 accepted slice 后默认跑：

```bash
python3 -m unittest discover -s tests -v
```

---

## 7. Risks / Blockers

1. current remaining `3` packets may not all be legitimately teacher-worthy without a bounded coverage-reserve rule
2. write-back could regress if reviewed count grows faster than outcome / training / incident backfill
3. schema gate cannot be rushed; same-day reruns never create real elapsed days
4. daily family can easily drift into “narrative waiting” unless every day still refreshes artifacts
5. local small model creep remains explicit blocker

---

## 8. Stop Conditions

遇到以下情况，`execute-plan` 必须停止并回 `plan-creator` 或用户：

- remaining reviewed gap cannot be closed without synthetic / unprovenanced review
- closing the remaining gap would require unbounded scope expansion
- same-day snapshots are being mistaken for real schema-day progress
- multiple equally-primary next slices emerge after daily recheck
- current evidence still says `not-yet`, but a proposed action tries to force rerun admission anyway

---

## 9. Successor Admission

本 family closeout 后允许的 successor 方向：

1. `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_RERUN`
   - 当 reviewed teacher count 与 schema day-span gates都真实满足
2. another bounded daily residual family
   - 当 reviewed gap / real elapsed days 仍未补齐，但 daily truth 已被新 evidence 重新冻结

当前默认不允许直接进入：

- `LOCAL_SMALL_MODEL_STUDENT_IMPLEMENTATION`

---

## 10. Initial Ordering

默认执行顺序：

1. `DV1.S1_REMAINING_BOUNDED_PACKET_REVIEW_APPEND_TO_TEN`
2. `DV2.S1_NEXT_DISTINCT_DATE_SCHEMA_PROGRESS_CHECKPOINT`
3. `DV3.S1_DAILY_RECHECK_AND_SUCCESSOR_DECISION`

只有当 `DV1` 诚实关闭 reviewed gap 或诚实证明当前 pool 无法继续后，才允许进入 `DV2`。
