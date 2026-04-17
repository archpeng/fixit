# Temporal Calibration Threshold Audit

## Recommendation
- action_threshold_recommendation: `keep_current_action_thresholds`
- teacher_trigger_recommendation: `trial_agreement_score_delta_with_history_as_bounded_review_backstop`
- reason: Current temporal evidence supports a bounded teacher-trigger backstop before any action-threshold change is admitted.

## Recommended Band
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

## Candidate Bands
- `agreement_score_delta_overlay` selected=5 delta=4 folds=3 budget_delta=4 severe=0 incidents=0
- `agreement_score_delta_with_history` selected=3 delta=3 folds=2 budget_delta=3 severe=0 incidents=0
- `agreement_score_delta_history_backstop` selected=3 delta=3 folds=2 budget_delta=3 severe=0 incidents=0
