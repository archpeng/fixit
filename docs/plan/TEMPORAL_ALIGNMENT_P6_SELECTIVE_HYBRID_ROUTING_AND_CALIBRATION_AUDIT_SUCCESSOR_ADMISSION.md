# TEMPORAL_ALIGNMENT_P6_SELECTIVE_HYBRID_ROUTING_AND_CALIBRATION_AUDIT_SUCCESSOR_ADMISSION

- Predecessor family: `TEMPORAL_ALIGNMENT_P6_SELECTIVE_HYBRID_ROUTING_AND_CALIBRATION_AUDIT`
- Predecessor verdict: `accept_with_residuals`
- Date: 2026-04-17
- Recommended successor: `TEMPORAL_ALIGNMENT_P7_TRIGGER_POLICY_AND_CALIBRATION_THRESHOLD_AUDIT`

---

## 1. Why a Successor Exists

P6 已把两件关键事做实：

1. selective hybrid routing can preserve bounded score lift while avoiding always-on fusion
2. calibration-style score audit can show where selected routing changes retrieval score but not downstream confidence

但 P6 结果也清楚表明：

- selected score lift did not turn into confidence lift
- major packet / episode metrics remain flat

因此若继续 temporal 方向，正确 successor 应优先围绕：

1. trigger-policy audit
2. calibration-threshold audit of when retrieval score deltas should matter downstream

## 2. Admitted Successor Scope

### In scope
- trigger-policy compare under anti-leakage discipline
- calibration-threshold audit
- score-delta usefulness audit beyond retrieval-only surface

### Out of scope
- bypassing blocked `DV2` schema gate
- pretending P6 already proved production metric lift
- full temporal sidecar production landing
- replacing packet as canonical decision unit

## 3. Entry Truth Frozen

- `packets_selected_for_hybrid = 5`
- `packets_with_selected_score_delta_gt_raw = 5`
- `packets_with_selected_confidence_delta_gt_raw = 0`
- `folds_with_selective_routing = 3`
- `max_selected_top_score_delta = 0.05`
- `anti_leakage_violation_count = 0`
- major packet / episode metrics remain flat

## 4. Relationship to Other Families

- successor remains orthogonal to blocked `DV2`
- historical/offline temporal work may continue without waiting on next date
- but it must not be used as fake evidence that the schema gate has passed
