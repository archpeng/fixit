# TEMPORAL_ALIGNMENT_P5_HYBRID_CONTEXT_RETRIEVAL_AND_SCORE_DELTA_AUDIT_STATUS

- Family: `TEMPORAL_ALIGNMENT_P5_HYBRID_CONTEXT_RETRIEVAL_AND_SCORE_DELTA_AUDIT`
- Status: closed
- Refresh verdict: `family-closed-accept-with-residuals`
- Current phase: `TP5W2_CLOSEOUT_AND_SUCCESSOR_DECISION`
- Active slice: `none`
- Current branch: `main`
- Last updated: 2026-04-17

---

## 1. Final Truth

本 family 已完成其 P5 implementation 范围，并以 `accept_with_residuals` closeout。

已完成的 governing truth：

- hybrid retrieval fusion 已 landed
- score-delta audit 已 landed
- script-backed artifacts 已写回
- closeout + successor routing 已写回

未改写的外部 truth：

- `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_DAILY_VOLUME_AND_SCHEMA_RESIDUAL` 的 `DV2` 仍被真实 next-date gate 阻塞
- 本 family 没有把 historical mining 结果包装成 schema gate 通过证据

## 2. What Landed

### Code / scripts
- `fixit_ai/temporal_alignment.py`
- `scripts/run_temporal_hybrid_context_probe.py`

### Tests
- `tests/test_temporal_alignment.py`

### Artifacts
- `data/eval/temporal-hybrid-context-probe.json`
- `data/eval/temporal-hybrid-context-probe.md`

### Docs
- `docs/plan/TEMPORAL_ALIGNMENT_P5_HYBRID_CONTEXT_RETRIEVAL_AND_SCORE_DELTA_AUDIT_CLOSEOUT_REVIEW.md`
- `docs/plan/TEMPORAL_ALIGNMENT_P5_HYBRID_CONTEXT_RETRIEVAL_AND_SCORE_DELTA_AUDIT_SUCCESSOR_ADMISSION.md`

## 3. Verified Evidence

### Hybrid compare
- `hybrid_context_prior_count = 4`
- `packets_with_hybrid_score_delta_gt_raw = 6`
- `packets_with_agreement_bonus = 6`
- `folds_with_top_hit_overlap = 3`
- `max_top_score_delta = 0.05`
- `anti_leakage_violation_count = 0`

### Metrics remain flat
- packet severe recall stays `1.0`
- packet top-K precision stays `1.0`
- episode top-K precision stays `0.3333`

## 4. Validation

```bash
python3 -m unittest tests.test_temporal_alignment -v
python3 scripts/run_temporal_hybrid_context_probe.py
python3 -m unittest discover -s tests -v
```

Result:
- targeted temporal tests green (`16 tests`)
- hybrid-context probe script green
- full regression green (`50 tests`)

## 5. Residuals

1. earliest fold still has zero history because no exact-time rows predate the first episode
2. hybrid score gains improved retrieval confidence shape but major metrics remain flat
3. likely next-value work is selective hybrid routing + calibration audit
4. blocked `DV2` mainline gate remains unchanged

## 6. Next Step

本 family 已 closeout，不再续写。

推荐 successor：
- `TEMPORAL_ALIGNMENT_P6_SELECTIVE_HYBRID_ROUTING_AND_CALIBRATION_AUDIT`

若未来恢复被日期阻塞的主线，则回到：
- `DV2.S1_NEXT_DISTINCT_DATE_SCHEMA_PROGRESS_CHECKPOINT`

前提仍然是：**真实 next date 到来。**
