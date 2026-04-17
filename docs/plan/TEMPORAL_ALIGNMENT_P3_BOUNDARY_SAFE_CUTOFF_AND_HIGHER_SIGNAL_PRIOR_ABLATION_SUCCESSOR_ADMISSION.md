# TEMPORAL_ALIGNMENT_P3_BOUNDARY_SAFE_CUTOFF_AND_HIGHER_SIGNAL_PRIOR_ABLATION_SUCCESSOR_ADMISSION

- Predecessor family: `TEMPORAL_ALIGNMENT_P3_BOUNDARY_SAFE_CUTOFF_AND_HIGHER_SIGNAL_PRIOR_ABLATION`
- Predecessor verdict: `accept_with_residuals`
- Date: 2026-04-17
- Recommended successor: `TEMPORAL_ALIGNMENT_P4_EPISODE_CONTEXT_PRIOR_SYNTHESIS_AND_SIGNAL_ABLATION`

---

## 1. Why a Successor Exists

P3 已把两件关键事做实：

1. boundary-safe cutoff admissibility 可以在不引入 leakage 的前提下扩展 strict history
2. compacted / prototype priors 可以减少 raw packet-copy docs，并在多数有历史的 folds 保持 top-hit overlap

但 P3 结果也清楚表明：

- earliest fold 仍然没有历史
- retrieval surface shape improved, but major packet / episode metrics remain flat

因此若继续 temporal 方向，正确 successor 应优先围绕：

1. richer episode-context prior synthesis
2. stronger signal ablation beyond raw packet-copy or simple prototype selection

## 2. Admitted Successor Scope

### In scope
- episode-context prior synthesis
- stronger signal compression / ablation
- script-backed compare artifacts
- continued anti-leakage discipline

### Out of scope
- bypassing blocked `DV2` schema gate
- pretending P3 already proved production metric lift
- full temporal sidecar production landing
- replacing packet as canonical decision unit

## 3. Entry Truth Frozen

- `folds_with_boundary_safe_history_gt_strict = 3`
- `equality_admitted_doc_count = 4`
- `anti_leakage_violation_count = 0`
- `folds_with_compacted_doc_count_lt_boundary_safe = 2`
- `folds_with_top_hit_overlap = 3`
- major packet / episode metrics remain flat

## 4. Relationship to Other Families

- successor remains orthogonal to blocked `DV2`
- historical/offline temporal work may continue without waiting on next date
- but it must not be used as fake evidence that the schema gate has passed
