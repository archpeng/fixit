# ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_STABILITY_AND_VOLUME_RESIDUAL_PLAN

- Status: completed
- Family: `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_STABILITY_AND_VOLUME_RESIDUAL`
- Created: 2026-04-16
- Plan type: repo-global residual execution pack
- Primary handoff: `execute-plan`
- Predecessor family:
  - `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP`
- Source anchors:
  - `docs/architecture/alert-intelligence-architecture.md`
  - `docs/mvp/alert-intelligence-mvp.md`
  - `docs/architecture/fixit-next-stage-recommended-runtime-architecture.md`
  - `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP_CLOSEOUT_REVIEW.md`
  - `docs/plan/ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP_SUCCESSOR_ADMISSION.md`
  - `data/eval/data-teacher-followup-closeout.json`
  - `data/eval/data-teacher-daily-review-batch.json`
  - `data/eval/data-teacher-runtime-baseline.json`
  - `data/eval/schema-stability-history.json`
  - `data/eval/local-small-model-phase2-audit.json`
  - `AGENTS.md`

---

## 1. Goal

把 followup family 留下的两个真实 residual：

- `teacher_reviewed_count: 3 -> 10`
- `schema_stability_days: 0 -> 14`

压成一个可连续执行、可跨天累计、不可作弊过门槛的 bounded family。

本 family 的目标不是再补 runtime 形态，也不是直接重开 local-small-model implementation；而是先把以下真相压成可执行 control plane：

1. 当前 bounded runtime 在现有 packet / review backlog 下，是否有能力自然把 reviewed teacher count 推到 `10`
2. 如果当前可见 packet 供给不足，应该如何在 **不突破 bounded allowlist** 的前提下补充 reviewable supply
3. schema checkpoint 如何只靠真实跨日累积，而不是靠同日多次 refresh 或 backdating 伪装达标
4. 什么时候才值得重开 `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_RERUN`

边界是：

> 先把 volume ceiling、day-span progress、daily evidence refresh 与 honest gate routing 固化清楚；在 gate 未满足前，不重开 small-model rerun，更不进入 implementation。

---

## 2. Scope

### 2.1 In scope

- reviewed teacher volume ceiling / gap baseline
- current bounded packet supply capacity readout
- current review backlog 与 remaining-to-target burn-down readout
- 若当前 ceiling 不足，small explicit bounded packet supply expansion
- daily reviewed teacher append with provenance-preserving ledgers
- multi-day schema checkpoint progress readout
- phase-2 gate recheck only after meaningful evidence change
- closeout review + successor routing

### 2.2 Out of scope

- local small model training / serving / rollout
- local small model rerun before `teacher_reviewed_count >= 10` and `schema_stability_days >= 14`
- all-service unbounded rollout
- fake timestamps / backdating / synthetic elapsed days
- synthetic teacher labels without provenance
- abandoning `incident packet` as canonical decision unit

---

## 3. Entry Criteria

以下前置已满足：

- predecessor `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_FOLLOWUP` 已 closeout
- predecessor verdict = `accept_with_residuals`
- predecessor successor admission = `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_STABILITY_AND_VOLUME_RESIDUAL`
- next-stage runtime architecture doc 已冻结两段打分 + human gate 形态
- 当前 hard facts:
  - `runtime_allowlist_count = 2`
  - `candidate_services = ['g-crm-campaign']`
  - `packet_services = ['g-crm-campaign']`
  - `current_packet_count = 7`
  - `current_teacher_reviewed_count = 3`
  - `remaining_to_phase2_target = 7`
  - `fallback_count = 0`
  - `current_schema_stability_days = 0`
  - `schema_snapshot_count = 3`
  - `phase2_verdict = not-yet`
- 当前已落地的稳定 truth：
  - runtime allowlist 已 bounded multi-pilot
  - reviewed packet write-back 已对当前 reviewed lane 闭合
  - schema history 已 append-only，但还没有跨日窗口

当前最关键的未冻结 truth：

- **当前 bounded packet / review backlog 是否足以自然把 reviewed teacher count 推到 `10`**
- 如果不足，下一刀应该是“bounded packet supply expansion”，而不是继续假设当前 daily append 足够

---

## 4. Family Exit Criteria

当以下条件满足其一时，本 family 可 closeout：

### A. Promotion-ready closeout

1. reviewed teacher volume 已达到或超过 `10`
2. schema stability 已达到或超过 `14 days`
3. phase-2 refresh 已不再是 `not-yet`
4. `PLAN/STATUS/WORKSET` 已写回 rerun admission truth

### B. Honest residual closeout

1. reviewed teacher volume capacity 与实际增长路径已被 script-backed artifact 证明
2. schema day-span progress 已按真实日期累积并可复盘
3. 当前为何仍不能 rerun 已被 refreshed evidence 明确冻结
4. successor routing 已指向新的 bounded residual family，而不是 narrative 模糊续做

说明：

- 本 family 不承诺一定把 phase-2 verdict 推到 `go`
- 但必须把“当前 volume ceiling 是否够、schema 天数如何自然积累、下一步为何继续或停止”压成 honest truth

---

## 5. Workstreams

| Workstream | Objective | Main deliverables | Close gate |
|---|---|---|---|
| `RW1_VOLUME_CAPACITY_BASELINE_AND_ROUTING` | 先证明当前 bounded runtime 的 reviewed volume ceiling 与 next-step routing | volume-capacity artifact, residual baseline readout, explicit next-slice admission | next slice is singular instead of guessed |
| `RW2A_BOUNDED_PACKET_SUPPLY_EXPANSION` | 若 current ceiling < `10`，在 bounded allowlist 内补 reviewable packet supply | refreshed replay/candidate/packet evidence, new packet capacity proof | visible reviewable supply no longer blocks target by construction |
| `RW2B_DAILY_REVIEW_APPEND_AND_GAP_BURNDOWN` | 若 current ceiling 已足够，则持续 append reviewed cases 并刷新 gap burn-down | refreshed teacher ledgers, batch report, progress delta | reviewed count grows with provenance and no write-back regression |
| `RW3_SCHEMA_DAYSPAN_PROGRESS` | 以 distinct-day truth 追踪 schema checkpoint 累积 | schema day-span progress readout, refreshed checkpoint artifact | real elapsed days are measurable without backdating |
| `RW4_PHASE2_RECHECK_AND_SUCCESSOR_DECISION` | 依据新 volume + schema evidence 重新判断 rerun 或 residual successor | refreshed phase2 audit, closeout review, successor admission | honest next step is frozen |

---

## 6. Verification Ladder

### Layer A — slice-local proof

每个 slice 至少补一个 proof-carrying surface：

- fail-first targeted test
- script-refreshable json / markdown artifact
- `STATUS/WORKSET` writeback

### Layer B — serial refresh proof

每个 accepted slice 默认按以下顺序串行刷新，避免 stale readout：

1. targeted unittest
2. `python3 scripts/run_hardening_pipeline.py`
3. `python3 scripts/run_data_teacher_accumulation.py`
4. artifact readback

### Layer C — family proof

每个 accepted slice 后跑：

```bash
python3 -m unittest discover -s tests -v
```

### Default command ladder

- `python3 -m unittest tests.test_data_teacher_accumulation -v`
- `python3 scripts/run_hardening_pipeline.py`
- `python3 scripts/run_data_teacher_accumulation.py`
- `python3 -m unittest discover -s tests -v`

---

## 7. Risks / Blockers

1. 当前 visible packet pool 可能天然不足以把 reviewed count 推到 `10`
2. 为追 volume 可能诱导低质量或无 provenance review
3. schema gate 需要真实跨日，不允许同日多次 refresh 冒充“持续稳定”
4. `prod-hq-bff-service` 当前仍无 candidate / packet 产出，volume growth 可能受 packet supply 而非 teacher budget 限制
5. direct `python3 scripts/run_teacher_review.py --seed-judgements data/eval/replay/manual_teacher_judgements.jsonl` 仍可能命中治理 false positive
6. local small model creep 可能把 family 从 residual accumulation 拉偏成 premature rerun / implementation

---

## 8. Stop Conditions

遇到以下情况，`execute-plan` 必须停止并回 `plan-creator` 或用户：

- 当前 active slice 需要 fake timestamps 或 backdating 才能“达标”
- 当前 active slice 需要突破 bounded allowlist 或扩成 all-service scope 才能继续
- current packet / review capacity 无法判断，且多个 equally-primary 下一刀同时成立
- teacher / human label provenance 无法保持
- 当前 family 需要直接重开 local-small-model rerun 才能解释 residual，而证据并未满足 gates

---

## 9. Successor Admission

本 family closeout 后允许的 successor 方向：

1. `LOCAL_SMALL_MODEL_STUDENT_UPGRADE_REVIEW_RERUN`
   - 当 `teacher_reviewed_count >= 10` 且 `schema_stability_days >= 14`，并且 refreshed phase-2 verdict 不再是 `not-yet`
2. another bounded residual family
   - 当 volume / schema 仍未过门槛，但 residual 已被新的 artifact / day-span truth 明确聚类

当前默认不允许直接进入：

- `LOCAL_SMALL_MODEL_STUDENT_IMPLEMENTATION`

---

## 10. Initial Ordering

默认执行顺序：

1. `RW1.S1_REVIEW_VOLUME_CAPACITY_AND_DAILY_PROGRESS_BASELINE`
2. branch by proof:
   - if current bounded ceiling `< 10` -> `RW2A.S1_BOUNDED_PACKET_SUPPLY_EXPANSION_TO_CLEAR_VOLUME_GATE`
   - else -> `RW2B.S1_DAILY_REVIEW_APPEND_AND_GAP_BURNDOWN`
3. `RW3.S1_MULTI_DAY_SCHEMA_PROGRESS_AND_DISTINCT_DATE_PROOF`
4. `RW4.S1_PHASE2_RECHECK_AND_SUCCESSOR_DECISION`

只有当 `RW1` 把 next slice 路由成单一明确结论后，才允许进入 `RW2A` 或 `RW2B`。

---

## 11. Closeout Note

本 family 已完成 closeout，当前 frozen outcome：

- reviewed-volume routing truth is script-backed
- bounded packet supply ceiling reached `10`
- reviewed teacher lane widened from `3` to `7` with `fallback = 0`
- widened reviewed lane remains fully backfilled across outcome / training / incident stores
- schema gate now uses distinct-date / elapsed-day truth rather than same-day snapshot count
- residual-family recheck remains `not-yet`
- recommended successor = `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_DAILY_VOLUME_AND_SCHEMA_RESIDUAL`
