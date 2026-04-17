# TEMPORAL_ALIGNMENT_P2_EXACT_TIME_DATA_EXPANSION_AND_TEMPORAL_PRIOR_PROBE_STATUS

- Family: `TEMPORAL_ALIGNMENT_P2_EXACT_TIME_DATA_EXPANSION_AND_TEMPORAL_PRIOR_PROBE`
- Status: closed
- Refresh verdict: `family-closed-accept-with-residuals`
- Current phase: `TP2W3_CLOSEOUT_AND_SUCCESSOR_DECISION`
- Active slice: `none`
- Current branch: `main`
- Last updated: 2026-04-17

---

## 1. Final Truth

本 family 已完成其 P2 implementation 范围，并以 `accept_with_residuals` closeout。

已完成的 governing truth：

- exact-time temporal prior catalog 已 landed
- strict-cutoff temporal prior probe 已 landed
- script-backed artifacts 已写回
- closeout + successor routing 已写回

未改写的外部 truth：

- `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_DAILY_VOLUME_AND_SCHEMA_RESIDUAL` 的 `DV2` 仍被真实 next-date gate 阻塞
- 本 family 没有把 historical mining 结果包装成 schema gate 通过证据

## 2. What Landed

### Code / scripts
- `fixit_ai/temporal_alignment.py`
- `scripts/run_temporal_prior_probe.py`

### Tests
- `tests/test_temporal_alignment.py`

### Artifacts
- `data/eval/temporal-prior-catalog.jsonl`
- `data/eval/temporal-prior-summary.json`
- `data/eval/temporal-prior-probe.json`
- `data/eval/temporal-prior-probe.md`

### Docs
- `docs/plan/TEMPORAL_ALIGNMENT_P2_EXACT_TIME_DATA_EXPANSION_AND_TEMPORAL_PRIOR_PROBE_CLOSEOUT_REVIEW.md`
- `docs/plan/TEMPORAL_ALIGNMENT_P2_EXACT_TIME_DATA_EXPANSION_AND_TEMPORAL_PRIOR_PROBE_SUCCESSOR_ADMISSION.md`

## 3. Verified Evidence

### Prior catalog
- packet-linked exact-time priors = `10`
- service counts:
  - `g-crm-campaign = 7`
  - `prod-hq-bff-service = 3`
- severity counts:
  - `severe = 4`
  - `moderate = 5`
  - `low = 1`

### Probe compare
- baseline strict history docs = `4`
- expanded packet prior count = `10`
- expanded total docs = `14`
- compare:
  - `folds_with_expanded_history_gt_baseline = 2`
  - `folds_with_expanded_refs_gt_baseline = 2`
  - `folds_with_top_hit_delta = 2`
  - `max_added_history_docs = 6`

### Metric truth
- baseline packet severe recall = `1.0`
- expanded packet severe recall = `1.0`
- baseline top-K precision = `1.0`
- expanded top-K precision = `1.0`
- baseline episode top-K precision = `0.3333`
- expanded episode top-K precision = `0.3333`

## 4. Validation

```bash
python3 -m unittest tests.test_temporal_alignment -v
python3 scripts/run_temporal_prior_probe.py
python3 -m unittest discover -s tests -v
```

Result:
- targeted temporal tests green (`11 tests`)
- prior-probe script green
- full regression green (`45 tests`)

## 5. Residuals

1. earliest folds still have zero strict history under current boundary discipline
2. expanded priors change coverage and retrieval visibility, but major metrics are still flat
3. likely next-value work is boundary-safe cutoff review + higher-signal prior ablation
4. blocked `DV2` mainline gate remains unchanged

## 6. Next Step

本 family 已 closeout，不再续写。

推荐 successor：
- `TEMPORAL_ALIGNMENT_P3_BOUNDARY_SAFE_CUTOFF_AND_HIGHER_SIGNAL_PRIOR_ABLATION`

若未来恢复被日期阻塞的主线，则回到：
- `DV2.S1_NEXT_DISTINCT_DATE_SCHEMA_PROGRESS_CHECKPOINT`

前提仍然是：**真实 next date 到来。**
