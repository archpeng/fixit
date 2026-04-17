# Temporal Selective Hybrid Probe

## Compare
- fold count: `4`
- packets_selected_for_hybrid: `5`
- packets_with_selected_score_delta_gt_raw: `5`
- packets_with_selected_confidence_delta_gt_raw: `0`
- folds_with_selective_routing: `3`
- folds_with_top_hit_overlap: `3`
- max_selected_top_score_delta: `0.05`
- anti_leakage_violation_count: `0`

## Raw Packet Metrics
- severe_recall: `1.0`
- top_k_precision: `1.0`
- teacher_escalation_rate: `0.0`
- missed_severe_count: `0`
- missed_severe_packets: `[]`

## Selective Packet Metrics
- severe_recall: `1.0`
- top_k_precision: `1.0`
- teacher_escalation_rate: `0.0`
- missed_severe_count: `0`
- missed_severe_packets: `[]`

## Folds
- `ep_inc-compile-500` packets=['ipk_w001', 'ipk_w004', 'ipk_w006', 'ipk_w009'] raw_priors=0 selective_context_priors=0 selected_hybrid_packets=0 score_delta_packets=0 confidence_delta_packets=0 top_hit_overlap=False max_selected_top_score_delta=0.0 leakage_violations=0
- `ep_inc-compile-warmup` packets=['ipk_w002', 'ipk_w007'] raw_priors=1 selective_context_priors=1 selected_hybrid_packets=2 score_delta_packets=2 confidence_delta_packets=0 top_hit_overlap=True max_selected_top_score_delta=0.05 leakage_violations=0
- `ep_inc-queue-depth` packets=['ipk_w005'] raw_priors=3 selective_context_priors=2 selected_hybrid_packets=1 score_delta_packets=1 confidence_delta_packets=0 top_hit_overlap=True max_selected_top_score_delta=0.05 leakage_violations=0
- `ep_inc-other-service` packets=['ipk_w010', 'ipk_w011', 'ipk_w012'] raw_priors=7 selective_context_priors=3 selected_hybrid_packets=2 score_delta_packets=2 confidence_delta_packets=0 top_hit_overlap=True max_selected_top_score_delta=0.05 leakage_violations=0
