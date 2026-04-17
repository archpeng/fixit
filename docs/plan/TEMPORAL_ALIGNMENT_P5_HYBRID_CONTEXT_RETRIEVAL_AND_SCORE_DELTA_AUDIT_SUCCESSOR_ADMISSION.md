# TEMPORAL_ALIGNMENT_P5_HYBRID_CONTEXT_RETRIEVAL_AND_SCORE_DELTA_AUDIT_SUCCESSOR_ADMISSION

- Predecessor family: `TEMPORAL_ALIGNMENT_P5_HYBRID_CONTEXT_RETRIEVAL_AND_SCORE_DELTA_AUDIT`
- Predecessor verdict: `accept_with_residuals`
- Date: 2026-04-17
- Recommended successor: `TEMPORAL_ALIGNMENT_P6_SELECTIVE_HYBRID_ROUTING_AND_CALIBRATION_AUDIT`

---

## 1. Why a Successor Exists

P5 已把两件关键事做实：

1. hybrid raw/context retrieval can produce bounded score lift under continued anti-leakage discipline
2. score-delta audit can quantify where hybrid routing actually changes retrieval confidence

但 P5 结果也清楚表明：

- major packet / episode metrics remain flat
- always-on hybrid fusion is not yet justified as a clearly better default lane

因此若继续 temporal 方向，正确 successor 应优先围绕：

1. selective hybrid routing
2. calibration-oriented audit of where score delta should or should not matter

## 2. Admitted Successor Scope

### In scope
- selective hybrid routing rules under anti-leakage discipline
- calibration-oriented compare artifacts
- score-delta usefulness audit

### Out of scope
- bypassing blocked `DV2` schema gate
- pretending P5 already proved production metric lift
- full temporal sidecar production landing
- replacing packet as canonical decision unit

## 3. Entry Truth Frozen

- `hybrid_context_prior_count = 4`
- `packets_with_hybrid_score_delta_gt_raw = 6`
- `packets_with_agreement_bonus = 6`
- `folds_with_top_hit_overlap = 3`
- `max_top_score_delta = 0.05`
- `anti_leakage_violation_count = 0`
- major packet / episode metrics remain flat

## 4. Relationship to Other Families

- successor remains orthogonal to blocked `DV2`
- historical/offline temporal work may continue without waiting on next date
- but it must not be used as fake evidence that the schema gate has passed
