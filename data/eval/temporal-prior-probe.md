# Temporal Prior Probe

## Summary
- baseline strict history docs: `4`
- expanded packet prior count: `10`
- expanded total doc count: `14`
- fold count: `4`

## Prior Summary
- service counts: `{'g-crm-campaign': 7, 'prod-hq-bff-service': 3}`
- severity counts: `{'severe': 4, 'moderate': 5, 'low': 1}`
- recommended action counts: `{'page_owner': 4, 'create_ticket': 5, 'observe': 1}`

## Compare
- folds_with_expanded_history_gt_baseline: `2`
- folds_with_expanded_refs_gt_baseline: `2`
- folds_with_top_hit_delta: `2`
- max_added_history_docs: `6`

## Baseline Packet Metrics
- severe_recall: `1.0`
- top_k_precision: `1.0`
- teacher_escalation_rate: `0.0`
- missed_severe_count: `0`
- missed_severe_packets: `[]`

## Expanded Packet Metrics
- severe_recall: `1.0`
- top_k_precision: `1.0`
- teacher_escalation_rate: `0.0`
- missed_severe_count: `0`
- missed_severe_packets: `[]`

## Folds
- `ep_inc-compile-500` packets=['ipk_w001', 'ipk_w004', 'ipk_w006', 'ipk_w009'] baseline_history=0 expanded_priors=0 expanded_history=0 baseline_refs=0 expanded_refs=0 top_hit_delta=False
- `ep_inc-compile-warmup` packets=['ipk_w002', 'ipk_w007'] baseline_history=0 expanded_priors=0 expanded_history=0 baseline_refs=0 expanded_refs=0 top_hit_delta=False
- `ep_inc-queue-depth` packets=['ipk_w005'] baseline_history=0 expanded_priors=2 expanded_history=2 baseline_refs=0 expanded_refs=2 top_hit_delta=True
- `ep_inc-other-service` packets=['ipk_w010', 'ipk_w011', 'ipk_w012'] baseline_history=2 expanded_priors=6 expanded_history=8 baseline_refs=6 expanded_refs=9 top_hit_delta=True
