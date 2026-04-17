# TEMPORAL_ALIGNMENT_AND_TIME_AWARE_EVAL_IMPLEMENTATION_SUCCESSOR_ADMISSION

- Predecessor family: `TEMPORAL_ALIGNMENT_AND_TIME_AWARE_EVAL_IMPLEMENTATION`
- Predecessor verdict: `accept_with_residuals`
- Date: 2026-04-17
- Recommended successor: `TEMPORAL_ALIGNMENT_P1_RECENCY_AND_LIGHT_FEATURE_ENRICHMENT`

---

## 1. Why a Successor Exists

当前 family 已完成 P0：

- temporal lineage
- derived timestamp overlays
- episode-aware split
- time-aware eval

但文档中明确列出的 P1 仍未进入实现面，因此需要 successor，而不是把当前 family 无限延长。

## 2. Admitted Successor Scope

### In scope

1. heuristic / bounded episode grouping beyond explicit historical-incident backing
2. recency-aware retrieval weighting under strict cutoff discipline
3. light temporal features for structured student / Granite lane experiments

### Out of scope

- temporal sidecar backend landing (`TimesFM / Chronos family`)
- replacing packet as canonical unit
- bypassing blocked `DV2` schema gate
- multi-week forecasting runtime

## 3. Entry Truth Frozen by This Admission

- current exact-time packet range: `2026-04-16T11:25:00Z -> 2026-04-16T12:25:00Z`
- current strict-eval-eligible outcomes: `10`
- current strict-eval-eligible training examples: `10`
- current train-only unknown-time legacy examples: `6`
- current episode count: `4`
- current cutoff leakage evidence is non-zero across all folds

## 4. Why This Is the Correct Next Step

当前最值得继续推进的 temporal work 不再是“有没有时间 contract”，而是：

- 如何在 strict temporal discipline 下，让 retrieval 更合理利用 recency
- 如何让 episode grouping 从 explicit-only 走向 bounded heuristic generalization
- 如何在不引入重 temporal model 的前提下，把时间信息喂给现有 scorer

## 5. Relationship to Other Repo Workstreams

- successor 不能改写 `ALERT_INTELLIGENCE_DATA_AND_TEACHER_ACCUMULATION_DAILY_VOLUME_AND_SCHEMA_RESIDUAL` 的 `DV2` truth
- successor 可以并行于 `DV2` 的 real-date waiting window 执行，但不得把 historical eval 结果包装成 schema admission evidence
