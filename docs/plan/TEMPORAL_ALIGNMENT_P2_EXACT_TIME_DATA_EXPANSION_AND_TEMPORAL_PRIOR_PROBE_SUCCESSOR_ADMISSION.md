# TEMPORAL_ALIGNMENT_P2_EXACT_TIME_DATA_EXPANSION_AND_TEMPORAL_PRIOR_PROBE_SUCCESSOR_ADMISSION

- Predecessor family: `TEMPORAL_ALIGNMENT_P2_EXACT_TIME_DATA_EXPANSION_AND_TEMPORAL_PRIOR_PROBE`
- Predecessor verdict: `accept_with_residuals`
- Date: 2026-04-17
- Recommended successor: `TEMPORAL_ALIGNMENT_P3_BOUNDARY_SAFE_CUTOFF_AND_HIGHER_SIGNAL_PRIOR_ABLATION`

---

## 1. Why a Successor Exists

P2 已经把两件关键事做实：

1. packet-linked exact-time priors 可以被稳定构造成可复用 history surface
2. strict-cutoff compare 可以真实量化 expanded history coverage / retrieval deltas

但 P2 结果也清楚表明：

- earliest folds 仍然拿不到 strict history
- expanded priors 改变了 retrieval visibility，却没有带来 major metrics lift

因此若继续 temporal 方向，正确 successor 应优先围绕：

1. review current strict boundary semantics (`<` vs boundary-safe admissibility)
2. compare higher-signal priors against raw packet-copy priors

## 2. Admitted Successor Scope

### In scope
- boundary-safe cutoff review under explicit anti-leakage proof
- higher-signal temporal prior ablations
- compacted prior / prototype compare
- script-backed compare artifacts

### Out of scope
- bypassing blocked `DV2` schema gate
- pretending P2 already proved production metric lift
- full temporal sidecar production landing
- replacing packet as canonical decision unit

## 3. Entry Truth Frozen

- baseline strict history docs = `4`
- expanded packet priors = `10`
- `folds_with_expanded_history_gt_baseline = 2`
- `folds_with_top_hit_delta = 2`
- major packet / episode metrics remain flat

## 4. Relationship to Other Families

- successor remains orthogonal to blocked `DV2`
- historical/offline temporal work may continue without waiting on next date
- but it must not be used as fake evidence that the schema gate has passed
