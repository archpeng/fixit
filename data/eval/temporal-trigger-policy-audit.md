# Temporal Trigger Policy Audit

## Compare
- fold count: `4`
- raw_triggered_packet_count: `5`
- temporal_triggered_packet_count: `8`
- packets_with_policy_delta_gt_raw: `3`
- folds_with_policy_delta: `2`
- budget_delta_packet_count: `3`
- anti_leakage_violation_count: `0`

## Recommended Temporal Band
- band_id: `agreement_score_delta_with_history`
- description: `Require agreement-backed score delta plus at least three raw prior docs.`
- temporal_trigger_reason: `temporal_agreement_score_delta_with_history`
- rank: `2`
- selected_packet_ids: `['ipk_w005', 'ipk_w010', 'ipk_w011']`
- selected_packet_count: `3`
- policy_delta_packet_ids: `['ipk_w005', 'ipk_w010', 'ipk_w011']`
- packets_with_policy_delta_gt_raw: `3`
- folds_with_policy_delta: `2`
- raw_triggered_packet_count: `5`
- temporal_triggered_packet_count: `8`
- budget_delta_packet_count: `3`
- selected_actual_severe_count: `0`
- selected_actual_incident_count: `0`
- policy_delta_actual_severe_count: `0`
- policy_delta_actual_incident_count: `0`
- selected_packet_prior_doc_max: `7`
- selected_top_score_delta_max: `0.05`
- anti_leakage_violation_count: `0`

## Raw Trigger Reason Counts
- high_novelty: `4`
- rule_missed_high_score: `2`
- low_confidence: `1`

## Temporal Trigger Reason Counts
- high_novelty: `4`
- rule_missed_high_score: `2`
- low_confidence: `1`
- temporal_agreement_score_delta_with_history: `3`

## Folds
- `ep_inc-compile-500` raw_triggered=['ipk_w001', 'ipk_w004', 'ipk_w006', 'ipk_w009'] temporal_triggered=['ipk_w001', 'ipk_w004', 'ipk_w006', 'ipk_w009'] policy_delta=[] selected_band=[] leakage_violations=0
- `ep_inc-compile-warmup` raw_triggered=['ipk_w002'] temporal_triggered=['ipk_w002'] policy_delta=[] selected_band=[] leakage_violations=0
- `ep_inc-queue-depth` raw_triggered=[] temporal_triggered=['ipk_w005'] policy_delta=['ipk_w005'] selected_band=['ipk_w005'] leakage_violations=0
- `ep_inc-other-service` raw_triggered=[] temporal_triggered=['ipk_w010', 'ipk_w011'] policy_delta=['ipk_w010', 'ipk_w011'] selected_band=['ipk_w010', 'ipk_w011'] leakage_violations=0
