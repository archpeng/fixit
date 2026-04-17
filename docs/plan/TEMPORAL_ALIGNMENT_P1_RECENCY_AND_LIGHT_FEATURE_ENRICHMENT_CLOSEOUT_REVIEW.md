# TEMPORAL_ALIGNMENT_P1_RECENCY_AND_LIGHT_FEATURE_ENRICHMENT_CLOSEOUT_REVIEW

- Family: `TEMPORAL_ALIGNMENT_P1_RECENCY_AND_LIGHT_FEATURE_ENRICHMENT`
- Closeout verdict: `accept_with_residuals`
- Date: 2026-04-17
- Branch: `main`

---

## 1. Scope Actually Completed

本 family 已真实落地并验证：

1. heuristic / bounded episode grouping beyond explicit-only backing
2. recency-aware retrieval weighting under strict cutoff discipline
3. light temporal features for structured student experiment lane
4. closeout + successor routing

## 2. Landed Surfaces

### Code
- `fixit_ai/temporal_alignment.py`
- `fixit_ai/retrieval_index.py`
- `fixit_ai/student.py`

### Scripts
- `scripts/run_time_aware_historical_eval.py`
- `scripts/run_temporal_feature_experiment.py`

### Tests
- `tests/test_temporal_alignment.py`
- `tests/test_pipeline.py`

### Artifacts
- refreshed `data/eval/episode-index.json`
- refreshed `data/eval/time-aware-eval.json`
- refreshed `data/eval/time-aware-eval.md`
- new `data/eval/temporal-feature-experiment.json`
- new `data/eval/temporal-feature-experiment.md`

## 3. Verified Truth

### Heuristic episode enrichment
- explicit incident-backed episodes remain `4`
- unbacked packets now support bounded heuristic grouping via:
  - same service
  - same operation
  - bounded gap (`<= 60m`)
  - bounded token overlap
- synthetic fail-first test proves grouping happens only when these bounds are met

### Recency-aware retrieval
- hardened retrieval now supports optional:
  - `reference_ts`
  - `recency_half_life_minutes`
- synthetic fail-first test proves newer strict incident outranks older strict incident when semantics tie
- current `time-aware-eval` truth:
  - `strict_cutoff_fold_count = 4`
  - `folds_with_recency_delta = 1`

### Light temporal feature experiment
- temporal features landed:
  - `same_service_recent_packet_count`
  - `same_service_recent_error_packet_count`
  - `same_service_prev_gap_inverse`
- experiment coverage:
  - packet-linked training rows = `10`
  - legacy zero-filled rows = `6`
- current experiment metrics:
  - baseline severe recall = `1.0`
  - temporal severe recall = `1.0`
  - baseline top-K precision = `1.0`
  - temporal top-K precision = `1.0`

Interpretation:

- P1 code path is real and script-backed
- recency and light temporal features are now consumable assets
- 但在当前极小 exact-time dataset 上，temporal feature lane 尚未证明相对 baseline 的指标增益

## 4. Validation Evidence

### Targeted
```bash
python3 -m unittest tests.test_temporal_alignment tests.test_pipeline -v
```

### Script-backed
```bash
python3 scripts/run_time_aware_historical_eval.py
python3 scripts/run_temporal_feature_experiment.py
```

### Regression
```bash
python3 -m unittest discover -s tests -v
```

Result:
- targeted temporal + pipeline tests green
- temporal scripts green
- full regression green (`43 tests`)

## 5. Improvements Closed

1. episode grouping no longer collapses to explicit-only + single-packet fallback
2. retrieval can now exploit recency without breaking strict cutoff discipline
3. structured student lane can now ingest light temporal features in experiment form

## 6. Residuals

1. current exact-time dataset is still too small to prove temporal feature metric lift
2. recency delta appears in only a subset of folds, so broader exact-time history would make the signal more meaningful
3. temporal sidecar / future-risk / persistence modeling remains out of scope and still unimplemented
4. blocked `DV2` schema next-date gate remains untouched

## 7. Honest Closeout

本 family 已完成其被要求的 P1 implementation 范围，因此可以 closeout。

但 closeout 结论必须保持诚实：

- 我们已经把 historical-value-mining 的 P1 资产真实落地
- 我们还没有在当前数据量下证明 temporal feature lane 带来了指标提升
- 下一步若继续 temporal 深化，应优先扩 exact-time history / richer temporal prior probe，而不是夸大当前 gain
