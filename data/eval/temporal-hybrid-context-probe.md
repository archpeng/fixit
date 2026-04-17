# Temporal Hybrid Context Probe

## Compare
- hybrid context prior count: `4`
- fold count: `4`
- packets_with_hybrid_score_delta_gt_raw: `6`
- packets_with_agreement_bonus: `6`
- folds_with_top_hit_overlap: `3`
- max_top_score_delta: `0.05`
- anti_leakage_violation_count: `0`

## Raw Packet Metrics
- severe_recall: `1.0`
- top_k_precision: `1.0`
- teacher_escalation_rate: `0.0`
- missed_severe_count: `0`
- missed_severe_packets: `[]`

## Hybrid Packet Metrics
- severe_recall: `1.0`
- top_k_precision: `1.0`
- teacher_escalation_rate: `0.0`
- missed_severe_count: `0`
- missed_severe_packets: `[]`

## Folds
- `ep_inc-compile-500` packets=['ipk_w001', 'ipk_w004', 'ipk_w006', 'ipk_w009'] raw_priors=0 hybrid_context_priors=0 score_delta_packets=0 agreement_bonus_packets=0 top_hit_overlap=False max_top_score_delta=0.0 leakage_violations=0
- `ep_inc-compile-warmup` packets=['ipk_w002', 'ipk_w007'] raw_priors=1 hybrid_context_priors=1 score_delta_packets=2 agreement_bonus_packets=2 top_hit_overlap=True max_top_score_delta=0.05 leakage_violations=0
- `ep_inc-queue-depth` packets=['ipk_w005'] raw_priors=3 hybrid_context_priors=2 score_delta_packets=1 agreement_bonus_packets=1 top_hit_overlap=True max_top_score_delta=0.05 leakage_violations=0
- `ep_inc-other-service` packets=['ipk_w010', 'ipk_w011', 'ipk_w012'] raw_priors=7 hybrid_context_priors=3 score_delta_packets=3 agreement_bonus_packets=3 top_hit_overlap=True max_top_score_delta=0.05 leakage_violations=0
