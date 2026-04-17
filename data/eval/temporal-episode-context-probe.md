# Temporal Episode-context Probe

## Summary
- episode-context prior count: `4`
- fold count: `4`
- episode-context prior summary: `{'packet_linked_prior_count': 4, 'service_counts': {'g-crm-campaign': 3, 'prod-hq-bff-service': 1}, 'severity_counts': {'severe': 1, 'moderate': 2, 'low': 1}, 'recommended_action_counts': {'page_owner': 1, 'create_ticket': 2, 'observe': 1}, 'exact_time_range': {'earliest': '2026-04-16T11:25:00Z', 'latest': '2026-04-16T12:25:00Z'}}`

## Compare
- folds_with_episode_context_doc_count_lt_boundary_safe: `2`
- folds_with_top_hit_overlap: `3`
- max_docs_removed_by_episode_context: `4`
- anti_leakage_violation_count: `0`

## Boundary-safe Packet Metrics
- severe_recall: `1.0`
- top_k_precision: `1.0`
- teacher_escalation_rate: `0.0`
- missed_severe_count: `0`
- missed_severe_packets: `[]`

## Episode-context Packet Metrics
- severe_recall: `1.0`
- top_k_precision: `1.0`
- teacher_escalation_rate: `0.0`
- missed_severe_count: `0`
- missed_severe_packets: `[]`

## Folds
- `ep_inc-compile-500` packets=['ipk_w001', 'ipk_w004', 'ipk_w006', 'ipk_w009'] raw_priors=0 episode_context_priors=0 boundary_safe_history=0 episode_context_history=0 overlap=False leakage_violations=0
- `ep_inc-compile-warmup` packets=['ipk_w002', 'ipk_w007'] raw_priors=1 episode_context_priors=1 boundary_safe_history=1 episode_context_history=1 overlap=True leakage_violations=0
- `ep_inc-queue-depth` packets=['ipk_w005'] raw_priors=3 episode_context_priors=2 boundary_safe_history=3 episode_context_history=2 overlap=True leakage_violations=0
- `ep_inc-other-service` packets=['ipk_w010', 'ipk_w011', 'ipk_w012'] raw_priors=7 episode_context_priors=3 boundary_safe_history=10 episode_context_history=6 overlap=True leakage_violations=0
