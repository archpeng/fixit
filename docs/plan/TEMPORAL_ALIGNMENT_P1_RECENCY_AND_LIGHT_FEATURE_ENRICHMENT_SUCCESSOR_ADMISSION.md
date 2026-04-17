# TEMPORAL_ALIGNMENT_P1_RECENCY_AND_LIGHT_FEATURE_ENRICHMENT_SUCCESSOR_ADMISSION

- Predecessor family: `TEMPORAL_ALIGNMENT_P1_RECENCY_AND_LIGHT_FEATURE_ENRICHMENT`
- Predecessor verdict: `accept_with_residuals`
- Date: 2026-04-17
- Recommended successor: `TEMPORAL_ALIGNMENT_P2_EXACT_TIME_DATA_EXPANSION_AND_TEMPORAL_PRIOR_PROBE`

---

## 1. Why a Successor Exists

P1 已把可直接落地的轻量 temporal enrichment 做完：

- heuristic grouping
- recency weighting
- light temporal features

但当前 closeout evidence 也明确表明：

- current exact-time dataset 仍太小
- temporal feature lane 尚未在当前 sample 上体现出指标 lift

因此若继续 temporal 方向，正确 successor 应优先围绕：

1. 扩 exact-time historical evidence
2. 增强 temporal prior probe，而不是直接跳到重 temporal model runtime

## 2. Admitted Successor Scope

### In scope
- richer exact-time history ingestion / expansion
- stronger temporal prior experiments under strict cutoff discipline
- higher-signal temporal ablation / compare artifacts
- optional preparatory work for temporal sidecar admission

### Out of scope
- bypassing blocked `DV2` schema gate
- replacing packet as canonical unit
- pretending current P1 already proved production gain
- full temporal sidecar production landing without new evidence

## 3. Entry Truth Frozen

- current exact-time packet range remains narrow
- current strict eval episodes = `4`
- `folds_with_recency_delta = 1`
- baseline vs temporal feature experiment currently flat on major packet metrics

## 4. Relationship to Other Families

- successor remains orthogonal to blocked `DV2`
- historical/offline temporal work may continue without waiting on next date
- but it must not be used as fake evidence that the schema gate has passed
