# TEMPORAL_ALIGNMENT_P4_EPISODE_CONTEXT_PRIOR_SYNTHESIS_AND_SIGNAL_ABLATION_SUCCESSOR_ADMISSION

- Predecessor family: `TEMPORAL_ALIGNMENT_P4_EPISODE_CONTEXT_PRIOR_SYNTHESIS_AND_SIGNAL_ABLATION`
- Predecessor verdict: `accept_with_residuals`
- Date: 2026-04-17
- Recommended successor: `TEMPORAL_ALIGNMENT_P5_HYBRID_CONTEXT_RETRIEVAL_AND_SCORE_DELTA_AUDIT`

---

## 1. Why a Successor Exists

P4 已把两件关键事做实：

1. episode-context prior synthesis 可以把 packet-linked priors 压成更高层的 context surface
2. synthesized context priors 在多数有 history 的 folds 上保留了 raw-lane top-hit overlap，同时减少 doc count

但 P4 结果也清楚表明：

- earliest fold 仍无历史
- retrieval surface shape improved, but major packet / episode metrics remain flat

因此若继续 temporal 方向，正确 successor 应优先围绕：

1. hybrid raw/context retrieval routing
2. more targeted score-delta audit instead of only doc-count compression

## 2. Admitted Successor Scope

### In scope
- hybrid context/raw retrieval compare
- score-delta audit under anti-leakage discipline
- script-backed compare artifacts

### Out of scope
- bypassing blocked `DV2` schema gate
- pretending P4 already proved production metric lift
- full temporal sidecar production landing
- replacing packet as canonical decision unit

## 3. Entry Truth Frozen

- `episode_context_prior_count = 4`
- `folds_with_episode_context_doc_count_lt_boundary_safe = 2`
- `folds_with_top_hit_overlap = 3`
- `max_docs_removed_by_episode_context = 4`
- `anti_leakage_violation_count = 0`
- major packet / episode metrics remain flat

## 4. Relationship to Other Families

- successor remains orthogonal to blocked `DV2`
- historical/offline temporal work may continue without waiting on next date
- but it must not be used as fake evidence that the schema gate has passed
