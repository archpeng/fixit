# Temporal Boundary-safe Probe

## Strict vs Boundary-safe Compare
- fold_count: `4`
- folds_with_boundary_safe_history_gt_strict: `3`
- folds_with_equality_admitted_docs: `3`
- equality_admitted_doc_count: `4`
- anti_leakage_violation_count: `0`

## Prototype Compare
- folds_with_compacted_doc_count_lt_boundary_safe: `2`
- folds_with_top_hit_overlap: `3`
- max_docs_removed_by_compaction: `4`

## Boundary-safe Packet Metrics
- severe_recall: `1.0`
- top_k_precision: `1.0`
- teacher_escalation_rate: `0.0`
- missed_severe_count: `0`
- missed_severe_packets: `[]`

## Prototype Packet Metrics
- severe_recall: `1.0`
- top_k_precision: `1.0`
- teacher_escalation_rate: `0.0`
- missed_severe_count: `0`
- missed_severe_packets: `[]`

## Folds
- `ep_inc-compile-500` packets=['ipk_w001', 'ipk_w004', 'ipk_w006', 'ipk_w009'] strict_history=0 boundary_safe_history=0 equality_added=0 leakage_violations=0 raw_priors=0 compacted_priors=0 prototype_top_hit_overlap=False
- `ep_inc-compile-warmup` packets=['ipk_w002', 'ipk_w007'] strict_history=0 boundary_safe_history=1 equality_added=1 leakage_violations=0 raw_priors=1 compacted_priors=1 prototype_top_hit_overlap=True
- `ep_inc-queue-depth` packets=['ipk_w005'] strict_history=2 boundary_safe_history=3 equality_added=1 leakage_violations=0 raw_priors=3 compacted_priors=2 prototype_top_hit_overlap=True
- `ep_inc-other-service` packets=['ipk_w010', 'ipk_w011', 'ipk_w012'] strict_history=8 boundary_safe_history=10 equality_added=2 leakage_violations=0 raw_priors=7 compacted_priors=3 prototype_top_hit_overlap=True
