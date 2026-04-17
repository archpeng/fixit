# TEMPORAL_ALIGNMENT_P1_RECENCY_AND_LIGHT_FEATURE_ENRICHMENT_STATUS

- Family: `TEMPORAL_ALIGNMENT_P1_RECENCY_AND_LIGHT_FEATURE_ENRICHMENT`
- Status: closed
- Refresh verdict: `family-closed-accept-with-residuals`
- Current phase: `TWP4_CLOSEOUT_AND_SUCCESSOR_DECISION`
- Active slice: `none`
- Current branch: `main`
- Last updated: 2026-04-17

---

## 1. Final Truth

本 family 已完成其 P1 implementation 范围，并以 `accept_with_residuals` closeout。

已完成的 governing truth：

- heuristic episode grouping beyond explicit backing 已 landed
- recency-aware retrieval weighting under strict cutoff discipline 已 landed
- light temporal feature experiment lane 已 landed
- closeout + successor routing 已写回

未改写的外部 truth：

- `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_DAILY_VOLUME_AND_SCHEMA_RESIDUAL` 的 `DV2` 仍被真实 next-date gate 阻塞
- 本 family 没有把 historical mining 结果包装成 schema gate 通过证据

## 2. What Landed

### Code / scripts
- `fixit_ai/temporal_alignment.py`
- `fixit_ai/retrieval_index.py`
- `fixit_ai/student.py`
- `scripts/run_time_aware_historical_eval.py`
- `scripts/run_temporal_feature_experiment.py`

### Tests
- `tests/test_temporal_alignment.py`
- `tests/test_pipeline.py`

### Artifacts
- refreshed `data/eval/episode-index.json`
- refreshed `data/eval/time-aware-eval.json`
- refreshed `data/eval/time-aware-eval.md`
- `data/eval/temporal-feature-experiment.json`
- `data/eval/temporal-feature-experiment.md`

### Docs
- `docs/plan/TEMPORAL_ALIGNMENT_P1_RECENCY_AND_LIGHT_FEATURE_ENRICHMENT_CLOSEOUT_REVIEW.md`
- `docs/plan/TEMPORAL_ALIGNMENT_P1_RECENCY_AND_LIGHT_FEATURE_ENRICHMENT_SUCCESSOR_ADMISSION.md`

## 3. Verified Evidence

### Heuristic grouping
- synthetic bounded heuristic grouping test green
- current explicit incident-backed episode truth remains `4`

### Recency-aware retrieval
- optional `reference_ts` + `recency_half_life_minutes` landed in hardened retrieval search
- `time-aware-eval` now reports:
  - `strict_cutoff_fold_count = 4`
  - `folds_with_recency_delta = 1`

### Light temporal feature experiment
- temporal feature names:
  - `same_service_recent_packet_count`
  - `same_service_recent_error_packet_count`
  - `same_service_prev_gap_inverse`
- feature coverage:
  - packet-linked training rows = `10`
  - legacy zero-filled rows = `6`
- current metrics:
  - baseline severe recall = `1.0`
  - temporal severe recall = `1.0`
  - baseline top-K precision = `1.0`
  - temporal top-K precision = `1.0`

## 4. Validation

```bash
python3 -m unittest tests.test_temporal_alignment tests.test_pipeline -v
python3 scripts/run_time_aware_historical_eval.py
python3 scripts/run_temporal_feature_experiment.py
python3 -m unittest discover -s tests -v
```

Result:
- targeted temporal + pipeline tests green
- temporal scripts green
- full regression green (`43 tests`)

## 5. Residuals

1. current exact-time dataset is too small to prove temporal feature metric lift
2. recency signal is now operational but still sparse in current folds
3. temporal sidecar / persistence / future-risk lanes remain future work
4. blocked `DV2` mainline gate remains unchanged

## 6. Next Step

本 family 已 closeout，不再续写。

推荐 successor：
- `TEMPORAL_ALIGNMENT_P2_EXACT_TIME_DATA_EXPANSION_AND_TEMPORAL_PRIOR_PROBE`

若未来恢复被日期阻塞的主线，则回到：
- `DV2.S1_NEXT_DISTINCT_DATE_SCHEMA_PROGRESS_CHECKPOINT`

前提仍然是：**真实 next date 到来。**
